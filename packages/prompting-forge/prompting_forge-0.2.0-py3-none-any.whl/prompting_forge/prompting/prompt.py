from __future__ import annotations

from dataclasses import dataclass
import json
import string
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set
from ..versioning import (
	save_prompt_version, 
	list_prompt_versions, 
	read_final_prompt, 
	save_final_prompt,
	save_refined_prompt,
	final_prompt_path,
)


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


class RefinedPromptTemplate(BasePromptTemplate):
	"""
	Refines a prompt through iterative LLM-based improvement.
	
	The LLM generates outputs using a prompt, then reviews those outputs
	to improve the prompt iteratively. Supports two analysis modes:
	- isolated: Only analyzes the most recent prompt-response pair
	- cumulative: Considers all prompts and responses during refinement
	"""

	def __init__(
		self,
		*,
		instance_name: str,
		variables: List[str],
		llm_client: Any,
		iterations: int = 3,
		mode: str = "isolated",
		refinement_instructions: Optional[str] = None,
		test_query: Optional[Any] = None,
		version_root: Optional[Path] = None,
		refined_filename: str = "refined_prompt.json",
		auto_run: bool = True,
	) -> None:
		"""
		Create a refined prompt through iterative LLM-based improvement.
		
		Args:
			instance_name: Name of the prompt instance to refine
			variables: List of variable names the refined template should use
			llm_client: LLM client from genai-forge
			iterations: Number of refinement iterations (default: 3)
			mode: Refinement mode - "isolated" or "cumulative" (default: "isolated")
			refinement_instructions: Optional custom instructions for refinement
			test_query: Optional test query/context to use for generating outputs during refinement
			version_root: Root directory for .prompt/ folder
			refined_filename: Filename for the refined prompt (default: "refined_prompt.json")
			auto_run: If True, automatically run an LLM call with the refined prompt (default: True)
		"""
		if mode not in ["isolated", "cumulative"]:
			raise ValueError(f"mode must be 'isolated' or 'cumulative', got: {mode}")
		
		if iterations < 1:
			raise ValueError(f"iterations must be at least 1, got: {iterations}")
		
		self._instance_name = instance_name
		self._variables = variables
		self._llm_client = llm_client
		self._iterations = iterations
		self._mode = mode
		self._refinement_instructions = refinement_instructions
		self._test_query = test_query
		self._version_root = version_root
		self._refined_filename = refined_filename
		self._auto_run = auto_run
		
		# Get or create initial prompt
		initial_prompt = self._get_initial_prompt()
		
		# Run refinement process
		refined_system, refined_template = self._refine_prompt(initial_prompt)
		
		# Save refined prompt
		refined_path = save_refined_prompt(
			instance_name,
			system=refined_system,
			template=refined_template,
			variables=variables,
			filename=refined_filename,
			root=version_root,
		)
		
		print(f"[+] Refined prompt saved to: {refined_path}")
		
		# Initialize with the refined prompt
		super().__init__(system=refined_system, template=refined_template, variables=variables)
		
		# Store reference for LLMCall tracking
		# Use _saved_final_path so LLMCall from genai-forge can find it
		self._saved_refined_path = refined_path  # type: ignore[attr-defined]
		self._saved_final_path = refined_path  # type: ignore[attr-defined] - for LLMCall compatibility
		self._instance_name = instance_name  # type: ignore[attr-defined]
		
		# Optionally run an LLM call with the refined prompt
		if auto_run and test_query is not None:
			self._run_with_refined_prompt()
	
	def _get_initial_prompt(self) -> tuple[str | None, str]:
		"""
		Get the starting prompt for refinement.
		First tries to load the final prompt, if not available, creates one from versions.
		"""
		# Try to load existing final prompt
		existing = read_final_prompt(self._instance_name, root=self._version_root)
		if existing:
			print(f"[*] Starting refinement from existing final prompt")
			return existing
		
		# No final prompt exists - create one from versions
		print(f"[*] No final prompt found, creating one from existing versions...")
		versions = list_prompt_versions(self._instance_name, root=self._version_root)
		
		if not versions:
			raise ValueError(
				f"No final prompt or versions found for '{self._instance_name}'. "
				"Create at least one prompt version first using PromptTemplate."
			)
		
		if len(versions) == 1:
			# Only one version - use it directly
			print(f"[*] Found 1 version, using it as the starting point")
			data = json.loads(versions[0].read_text(encoding="utf-8"))
			system = data.get("system")
			template = data.get("template", "")
			
			# Save as final prompt for future reference
			save_final_prompt(
				self._instance_name,
				system=system,
				template=template,
				variables=self._variables,
				root=self._version_root,
			)
			return system, template
		
		# Multiple versions - synthesize a final prompt
		print(f"[*] Found {len(versions)} versions, synthesizing final prompt...")
		final_template = FinalPromptTemplate(
			instance_name=self._instance_name,
			variables=self._variables,
			llm_client=self._llm_client,
			version_root=self._version_root,
			force_regenerate=False,
		)
		
		return final_template._system, final_template._template
	
	def _refine_prompt(self, initial_prompt: tuple[str | None, str]) -> tuple[str | None, str]:
		"""
		Run the iterative refinement process.
		"""
		print(f"\n[*] Starting {self._mode} refinement with {self._iterations} iterations...")
		
		current_system, current_template = initial_prompt
		
		# Track all iterations for cumulative mode
		history: List[Dict[str, Any]] = []
		
		for i in range(self._iterations):
			print(f"\n--- Iteration {i + 1}/{self._iterations} ---")
			
			# Step 1: Generate output using current prompt
			output = self._generate_output(current_system, current_template)
			print(f"[*] Generated output ({len(output)} chars)")
			
			# Step 2: Analyze and improve the prompt
			if self._mode == "isolated":
				improved_system, improved_template = self._analyze_isolated(
					current_system, current_template, output
				)
			else:  # cumulative
				history.append({
					"system": current_system,
					"template": current_template,
					"output": output,
				})
				improved_system, improved_template = self._analyze_cumulative(history)
			
			print(f"[+] Prompt improved")
			
			# Update for next iteration
			current_system = improved_system
			current_template = improved_template
		
		print(f"\n[+] Refinement complete after {self._iterations} iterations")
		return current_system, current_template
	
	def _generate_output(self, system: str | None, template: str) -> str:
		"""
		Generate an output using the current prompt.
		"""
		# Create a temporary prompt template
		temp_prompt = BasePromptTemplate(
			system=system,
			template=template,
			variables=self._variables,
		)
		
		# Prepare test context
		if self._test_query is None:
			# Create a default test context
			test_context = {var: f"<{var}_value>" for var in self._variables}
		elif isinstance(self._test_query, dict):
			test_context = self._test_query
		else:
			test_context = {"query": str(self._test_query)}
		
		# Format the prompt
		chat_prompt = temp_prompt.format(test_context)
		
		# Call the LLM
		from genai_forge.llm import LLMCall
		
		llm_call = LLMCall(
			query="",
			prompt_template=temp_prompt,
			client=self._llm_client,
			name=f"refine_{self._instance_name}_test",
			enable_versioning=False,
		)
		
		_, response = llm_call.run(test_context)
		return str(response)
	
	def _analyze_isolated(
		self, 
		system: str | None, 
		template: str, 
		output: str
	) -> tuple[str | None, str]:
		"""
		Analyze the most recent prompt-response pair and improve the prompt (isolated mode).
		"""
		default_instructions = (
			"Analyze the prompt below and the output it generated. "
			"Identify weaknesses, ambiguities, or areas for improvement. "
			"Create an improved version of the prompt that will produce better outputs."
		)
		
		user_instructions = self._refinement_instructions or default_instructions
		
		# Build explicit variable list for the prompt
		var_examples = ", ".join([f"{{{var}}}" for var in self._variables])
		
		analysis_input = (
			f"{user_instructions}\n\n"
			f"Current Prompt:\n"
			f"System: {system or 'None'}\n"
			f"Template: {template}\n\n"
			f"Generated Output:\n{output}\n\n"
			f"CRITICAL REQUIREMENT - Required variables: {self._variables}\n"
			f"The improved template MUST include ALL of these variables: {var_examples}\n"
			f"Do NOT hardcode values that should be variables. Use placeholders for all required variables.\n\n"
			f"Return ONLY a JSON object with this exact structure:\n"
			f'{{"system": "improved system message or null", "template": "improved template"}}\n\n'
			f"EXAMPLE of correct template format: \"Write docs for {{feature}} with {{sections}}\"\n"
			f"WRONG: \"Write docs for API with overview and examples\" (hardcoded values)\n"
			f"RIGHT: \"Write docs for {{feature}} with {{sections}}\" (uses variables)\n\n"
			f"Your improved template MUST include every variable from this list: {self._variables}"
		)
		
		return self._call_refinement_llm(analysis_input)
	
	def _analyze_cumulative(self, history: List[Dict[str, Any]]) -> tuple[str | None, str]:
		"""
		Analyze all prompts and responses to determine the best improved prompt (cumulative mode).
		"""
		default_instructions = (
			"Analyze all the prompts below and their corresponding outputs. "
			"Identify patterns, weaknesses, and successful elements across all iterations. "
			"Create an optimized prompt that incorporates the best insights from all versions."
		)
		
		user_instructions = self._refinement_instructions or default_instructions
		
		# Build history text
		history_text = "\n\n".join([
			f"Iteration {idx + 1}:\n"
			f"System: {item['system'] or 'None'}\n"
			f"Template: {item['template']}\n"
			f"Output: {item['output'][:500]}{'...' if len(item['output']) > 500 else ''}"
			for idx, item in enumerate(history)
		])
		
		# Build explicit variable list for the prompt
		var_examples = ", ".join([f"{{{var}}}" for var in self._variables])
		
		analysis_input = (
			f"{user_instructions}\n\n"
			f"Prompt History:\n{history_text}\n\n"
			f"CRITICAL REQUIREMENT - Required variables: {self._variables}\n"
			f"The optimized template MUST include ALL of these variables: {var_examples}\n"
			f"Do NOT hardcode values that should be variables. Use placeholders for all required variables.\n\n"
			f"Return ONLY a JSON object with this exact structure:\n"
			f'{{"system": "optimized system message or null", "template": "optimized template"}}\n\n'
			f"EXAMPLE of correct template format: \"Write docs for {{feature}} with {{sections}}\"\n"
			f"WRONG: \"Write docs for API with overview and examples\" (hardcoded values)\n"
			f"RIGHT: \"Write docs for {{feature}} with {{sections}}\" (uses variables)\n\n"
			f"Your optimized template MUST include every variable from this list: {self._variables}"
		)
		
		return self._call_refinement_llm(analysis_input)
	
	def _call_refinement_llm(self, analysis_input: str, retry_count: int = 0, max_retries: int = 2) -> tuple[str | None, str]:
		"""
		Call the LLM to analyze and improve the prompt.
		Includes retry logic if required variables are missing.
		"""
		from genai_forge.llm import LLMCall
		
		analysis_prompt = PromptTemplate(
			system="You are an expert prompt engineer specializing in iterative prompt refinement and optimization.",
			template="{analysis_input}",
			variables=["analysis_input"]
		)
		
		llm_call = LLMCall(
			query=analysis_input,
			prompt_template=analysis_prompt,
			client=self._llm_client,
			name=f"refine_{self._instance_name}_analysis",
			enable_versioning=False,
		)
		
		_, response = llm_call.run({"analysis_input": analysis_input})
		
		# Parse LLM response
		try:
			response_text = str(response)
			if "```json" in response_text:
				response_text = response_text.split("```json")[1].split("```")[0]
			elif "```" in response_text:
				response_text = response_text.split("```")[1].split("```")[0]
			
			result = json.loads(response_text.strip())
			improved_system = result.get("system")
			improved_template = result["template"]
			
			# CRITICAL: Validate that ALL required variables are in the template
			try:
				self._validate_template_variables(improved_template)
			except ValueError as ve:
				# Variables are missing - try to retry with more explicit instructions
				if retry_count < max_retries:
					print(f"[!] Template validation failed: {ve}")
					print(f"    Retrying with more explicit instructions (attempt {retry_count + 1}/{max_retries})...")
					
					# Add the validation error to the prompt for the retry
					retry_input = (
						f"{analysis_input}\n\n"
						f"PREVIOUS ATTEMPT FAILED:\n"
						f"Your previous template was: {improved_template}\n"
						f"ERROR: {ve}\n\n"
						f"Try again and ensure EVERY variable is included as a placeholder in the template."
					)
					return self._call_refinement_llm(retry_input, retry_count + 1, max_retries)
				else:
					# Max retries exceeded - raise the error
					raise
			
			return improved_system, improved_template
		except Exception as e:
			print(f"[!] Warning: Failed to parse or validate refinement response: {e}")
			print(f"    Response: {str(response)[:200]}...")
			raise ValueError(f"Failed to process refinement LLM response after {retry_count + 1} attempts: {e}\nResponse: {response}")
	
	def _validate_template_variables(self, template: str) -> None:
		"""
		Validate that all required variables are present in the template.
		Raises ValueError if any variables are missing.
		"""
		# Extract variables from template
		template_vars = set()
		for _, field_name, _, _ in string.Formatter().parse(template):
			if field_name:
				root = field_name.split(".")[0].split("[")[0]
				if root:
					template_vars.add(root)
		
		# Check for missing variables
		required_vars = set(self._variables)
		missing_vars = required_vars - template_vars
		
		if missing_vars:
			raise ValueError(
				f"Refined template is missing required variables: {sorted(missing_vars)}. "
				f"Template has: {sorted(template_vars)}. Required: {sorted(required_vars)}. "
				f"Template: {template}"
			)
	
	def _run_with_refined_prompt(self) -> None:
		"""
		Automatically run an LLM call with the refined prompt using the test query.
		"""
		print(f"\n[*] Running LLM call with refined prompt...")
		
		from genai_forge.llm import LLMCall
		
		llm_call = LLMCall(
			query="" if isinstance(self._test_query, dict) else str(self._test_query or ""),
			prompt_template=self,
			client=self._llm_client,
			name=f"{self._instance_name}_refined",
			enable_versioning=True,
		)
		
		# Prepare context
		if self._test_query is None:
			context = {var: f"<{var}_value>" for var in self._variables}
		elif isinstance(self._test_query, dict):
			context = self._test_query
		else:
			context = {"query": str(self._test_query)}
		
		_, response = llm_call.run(context)
		
		print(f"\n[+] Refined prompt execution complete")
		print(f"    Response: {str(response)[:200]}{'...' if len(str(response)) > 200 else ''}")


