from __future__ import annotations

from dataclasses import dataclass
import json
import string
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set
from ..versioning import save_prompt_version, list_prompt_versions, read_final_prompt, save_final_prompt


@dataclass(frozen=True)
class ChatPrompt:
	"""
	Minimal chat prompt representation.
	"""
	system: Optional[str]
	user: str

	def to_messages(self) -> list[dict]:
		messages: list[dict] = []
		if self.system:
			messages.append({"role": "system", "content": self.system})
		messages.append({"role": "user", "content": self.user})
		return messages
	
	def __or__(self, other: Any) -> Any:
		"""
		Pipe ChatPrompt to an LLM or parser.
		ChatPrompt | llm -> calls llm(ChatPrompt)
		ChatPrompt | parser -> calls parser.parse(llm_output)
		"""
		if callable(other):
			# Check if it's a parser (has parse method)
			if hasattr(other, "parse"):
				# This should not happen directly, parsers come after LLM
				raise TypeError("Cannot pipe ChatPrompt directly to parser. Use: template | llm | parser")
			# It's an LLM callable
			return other(self)
		raise TypeError(f"Cannot pipe ChatPrompt to {type(other)}")


class BasePromptTemplate:
	"""
	Base prompt template with Python str.format placeholders.
	"""

	def __init__(self, *, system: Optional[str], template: str, variables: Optional[Iterable[str]] = None) -> None:
		self._system = system
		self._template = template
		self._variables = list(variables) if variables is not None else None

	def format(self, variables: Any, *, instructions: Optional[str] = None) -> ChatPrompt:
		"""
		Format the template with variables. If variables is not a mapping, it will
		be available as the 'query' variable. If instructions are provided, they
		are appended to the user content automatically.
		"""
		context: Dict[str, Any]
		if isinstance(variables, dict):
			context = dict(variables)
		else:
			# Treat raw input as the user's query
			context = {"query": variables}

		self._validate_required_variables(context)
		user_text = self._template.format(**context)

		# Ensure the raw user query is present even if not in the template
		if "query" in context and "{query}" not in self._template:
			q = str(context["query"]).strip()
			if q:
				if user_text.strip():
					user_text = f"{user_text.rstrip()}\n\n{q}"
				else:
					user_text = q

		# Automatically include parser instructions if present
		if instructions:
			user_text = f"{user_text.rstrip()}\n\n{instructions}"

		chat = ChatPrompt(system=self._system, user=user_text)
		return chat

	def __call__(self, variables: Any, *, instructions: Optional[str] = None) -> ChatPrompt:
		return self.format(variables, instructions=instructions)

	def render(self, context: Mapping[str, Any], *, strict: bool = True) -> str:
		"""
		Render prompt to a plain string. Validates required variables first.
		"""
		if not isinstance(context, Mapping):
			raise TypeError("context must be a mapping of variable names to values")
		if strict:
			self._validate_required_variables(context)  # may raise
		out = self._template.format(**context)  # may still KeyError if non-strict
		return out

	def expected_variables(self) -> Set[str]:
		return self._expected_variables()

	def _expected_variables(self) -> Set[str]:
		if self._variables is not None:
			return {str(v) for v in self._variables}
		# Parse placeholders from the template
		fields: Set[str] = set()
		for literal_text, field_name, format_spec, conversion in string.Formatter().parse(self._template):
			if field_name:
				root = field_name.split(".")[0].split("[")[0]
				if root:
					fields.add(root)
		return fields

	def _validate_required_variables(self, context: Mapping[str, Any]) -> None:
		required = self._expected_variables()
		missing = sorted([name for name in required if name not in context])
		if missing:
			raise ValueError(f"Missing variables for template: {missing}. Expected: {sorted(required)}")
	
	def __or__(self, other: Any) -> Any:
		"""
		Pipe template to LLM or create a chain.
		template | llm -> returns a callable that formats and calls LLM
		template | llm | parser -> returns a callable that formats, calls LLM, and parses
		"""
		from functools import wraps
		
		if callable(other):
			# Check if it's a parser (has parse method)
			if hasattr(other, "parse"):
				raise TypeError("Cannot pipe template directly to parser. Use: template | llm | parser")
			
			# It's an LLM - return a chain function
			@wraps(other)
			def chain(variables: Any) -> Any:
				# Format the template
				chat_prompt = self.format(variables)
				# Call the LLM
				return other(chat_prompt)
			
			# Attach pipe operator to the chain for further composition
			def chain_or(next_callable: Any) -> Any:
				if hasattr(next_callable, "parse"):
					# It's a parser
					@wraps(next_callable.parse)
					def parse_chain(variables: Any) -> Any:
						# Get format instructions if parser provides them
						instructions = None
						if hasattr(next_callable, "get_format_instructions"):
							instructions = next_callable.get_format_instructions()
						
						# Format with instructions
						chat_prompt = self.format(variables, instructions=instructions)
						# Call LLM
						llm_output = other(chat_prompt)
						# Parse output
						return next_callable.parse(str(llm_output))
					return parse_chain
				else:
					# Continue chaining
					raise TypeError(f"Cannot pipe to {type(next_callable)}")
			
			chain.__or__ = chain_or
			return chain
		
		raise TypeError(f"Cannot pipe template to {type(other)}")
	
	def __ror__(self, other: Any) -> Any:
		"""
		Allow string | template (query from left).
		"query" | template -> returns a ChainBuilder that supports further piping
		"""
		if isinstance(other, str):
			# Create a chain builder class to properly handle the pipe operator
			class ChainBuilder:
				def __init__(self, template_ref, query_str):
					self._template = template_ref
					self._query = query_str
				
				def __call__(self, variables: Any = None) -> ChatPrompt:
					if variables is None:
						variables = {}
					if isinstance(variables, dict):
						ctx = dict(variables)
						if "query" not in ctx:
							ctx["query"] = self._query
					else:
						ctx = {"query": self._query}
					return self._template.format(ctx)
				
				def __or__(self, next_item: Any) -> Any:
					if callable(next_item):
						# Check if it's a parser
						if hasattr(next_item, "parse"):
							raise TypeError("Cannot pipe query+template directly to parser. Use: query | template | llm | parser")
						
						# It's an LLM - create LLM chain
						class LLMChain:
							def __init__(self, template_ref, query_str, llm):
								self._template = template_ref
								self._query = query_str
								self._llm = llm
							
							def __call__(self, variables: Any = None) -> Any:
								if variables is None:
									variables = {}
								if isinstance(variables, dict):
									ctx = dict(variables)
									if "query" not in ctx:
										ctx["query"] = self._query
								else:
									ctx = {"query": self._query}
								chat_prompt = self._template.format(ctx)
								return self._llm(chat_prompt)
							
							def __or__(self, parser: Any) -> Any:
								if hasattr(parser, "parse"):
									# It's a parser - create full chain
									def full_chain(variables: Any = None) -> Any:
										if variables is None:
											variables = {}
										if isinstance(variables, dict):
											ctx = dict(variables)
											if "query" not in ctx:
												ctx["query"] = self._query
										else:
											ctx = {"query": self._query}
										
										# Get format instructions if parser provides them
										instructions = None
										if hasattr(parser, "get_format_instructions"):
											instructions = parser.get_format_instructions()
										
										chat_prompt = self._template.format(ctx, instructions=instructions)
										llm_output = self._llm(chat_prompt)
										return parser.parse(str(llm_output))
									return full_chain
								raise TypeError(f"Cannot pipe to {type(parser)}")
						
						return LLMChain(self._template, self._query, next_item)
					raise TypeError(f"Cannot pipe to {type(next_item)}")
			
			return ChainBuilder(self, other)
		
		raise TypeError(f"Cannot pipe {type(other)} to template")


class PromptTemplate(BasePromptTemplate):
	"""
	Standard prompt template that saves versions when instantiated with an instance_name.
	"""

	def __init__(
		self,
		*,
		system: Optional[str],
		template: str,
		variables: Optional[Iterable[str]] = None,
		instance_name: Optional[str] = None,
		version_root: Optional[Path] = None,
	) -> None:
		super().__init__(system=system, template=template, variables=variables)
		# If an instance name is provided, persist a prompt version immediately
		if instance_name:
			try:
				var_keys = sorted(self._expected_variables())
				version_path, is_new = save_prompt_version(
					instance_name,
					system=self._system,
					user_text="",
					root=version_root,
					template=self._template,
					variables=var_keys,
				)
				# Store path for downstream reference
				self._saved_version_path = version_path  # type: ignore[attr-defined]
				self._is_new_version = is_new  # type: ignore[attr-defined]
				
				# Print status message
				if is_new:
					# Extract version number from path
					version_num = version_path.stem.split("__prompt__v")[-1]
					print(f"[+] New prompt version created: v{version_num}")
					print(f"    Saved to: {version_path}")
				else:
					# Extract version number from path
					version_num = version_path.stem.split("__prompt__v")[-1]
					print(f"[=] Prompt unchanged - using existing version: v{version_num}")
					print(f"    Location: {version_path}")
			except Exception as e:
				print(f"[!] Failed to save prompt version: {e}")


class FinalPromptTemplate(BasePromptTemplate):
	"""
	Synthesizes a final prompt from multiple versions using an LLM.
	Requires at least 2 prompt versions to synthesize.
	"""

	def __init__(
		self,
		*,
		instance_name: str,
		variables: List[str],
		llm_client: Any,
		synthesis_instructions: Optional[str] = None,
		version_root: Optional[Path] = None,
		force_regenerate: bool = True,
	) -> None:
		"""
		Create a final prompt by synthesizing all versions with an LLM.
		
		Args:
			instance_name: Name of the prompt instance to synthesize
			variables: List of variable names the final template should use
			llm_client: LLM client from genai-forge
			synthesis_instructions: Optional custom instructions for synthesis
			version_root: Root directory for .prompt/ folder
			force_regenerate: If True, always regenerate (default: True)
		"""
		# Check if final prompt already exists (only if not forcing regeneration)
		if not force_regenerate:
			existing = read_final_prompt(instance_name, root=version_root)
			if existing:
				system, template = existing
				print(f"[=] Using existing final prompt for '{instance_name}'")
				super().__init__(system=system, template=template, variables=variables)
				# Store reference to the final prompt file for LLMCall tracking
				final_path = final_prompt_path(instance_name, root=version_root)
				self._saved_final_path = final_path  # type: ignore[attr-defined]
				self._instance_name = instance_name  # type: ignore[attr-defined]
				return

		# Collect all versions
		versions = list_prompt_versions(instance_name, root=version_root)
		if len(versions) < 2:
			raise ValueError(
				f"Need at least 2 prompt versions to synthesize. Found {len(versions)} for '{instance_name}'. "
				"Create more prompt versions first using PromptTemplate."
			)

		print(f"[*] Synthesizing final prompt from {len(versions)} versions...")

		# Read all version contents
		version_data: List[Dict[str, Any]] = []
		for version_path in versions:
			try:
				data = json.loads(version_path.read_text(encoding="utf-8"))
				version_data.append({
					"version": data.get("version", "?"),
					"system": data.get("system"),
					"template": data.get("template"),
					"variables": data.get("variables", []),
				})
			except Exception:
				continue

		# Build synthesis prompt
		versions_text = "\n\n".join([
			f"Version {v['version']}:\n"
			f"System: {v['system']}\n"
			f"Template: {v['template']}\n"
			f"Variables: {v['variables']}"
			for v in version_data
		])

		default_instructions = (
			"Analyze the prompt versions below and create a final, optimized prompt.\n"
			"Your task is to synthesize the best elements from all versions into a single, high-quality prompt."
		)

		user_instructions = synthesis_instructions or default_instructions
		
		synthesis_template_text = (
			f"{user_instructions}\n\n"
			f"Required variables for the final template: {variables}\n\n"
			f"Previous versions:\n{versions_text}\n\n"
			f"Return ONLY a JSON object with this exact structure:\n"
			f'{{"system": "system message here or null", "template": "template with {{{variables[0]}}} etc."}}\n'
			"The template MUST use ALL required variables in Python format style (e.g., {variable_name})."
		)

		# Use PromptTemplate + LLMCall for synthesis
		from genai_forge.llm import LLMCall
		
		synthesis_prompt = PromptTemplate(
			system="You are an expert prompt engineer. Create optimized prompts based on iterative versions.",
			template="{synthesis_input}",
			variables=["synthesis_input"]
		)

		llm_call = LLMCall(
			query=synthesis_template_text,
			prompt_template=synthesis_prompt,
			client=llm_client,
			name=f"synthesize_{instance_name}",
			enable_versioning=False,  # Don't save synthesis calls to .llm_call/
		)

		_, response = llm_call.run({"synthesis_input": synthesis_template_text})
		
		# Parse LLM response
		try:
			# Extract JSON from response
			response_text = str(response)
			if "```json" in response_text:
				response_text = response_text.split("```json")[1].split("```")[0]
			elif "```" in response_text:
				response_text = response_text.split("```")[1].split("```")[0]
			
			result = json.loads(response_text.strip())
			final_system = result.get("system")
			final_template = result["template"]
		except Exception as e:
			raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {response}")

		# Validate that all required variables are in the template
		template_vars = set()
		for _, field_name, _, _ in string.Formatter().parse(final_template):
			if field_name:
				root = field_name.split(".")[0].split("[")[0]
				if root:
					template_vars.add(root)
		
		missing = set(variables) - template_vars
		if missing:
			print(f"[!] Warning: Template missing required variables: {missing}")

		# Save final prompt
		final_path = save_final_prompt(
			instance_name,
			system=final_system,
			template=final_template,
			variables=variables,
			root=version_root,
		)

		print(f"[+] Final prompt synthesized and saved")
		
		# Initialize with the synthesized prompt
		super().__init__(system=final_system, template=final_template, variables=variables)
		
		# Store reference to the final prompt file for LLMCall tracking
		self._saved_final_path = final_path  # type: ignore[attr-defined]
		self._instance_name = instance_name  # type: ignore[attr-defined]


