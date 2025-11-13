from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


def _instance_dir(name: str, *, root: Path | None = None) -> Path:
	"""Get the directory for a prompt instance."""
	base = root if root is not None else Path.cwd()
	return base / ".prompt" / name


def _ts() -> str:
	"""Get current timestamp in ISO format."""
	return datetime.now(timezone.utc).isoformat()


def log_event(instance_name: str, event: str, details: dict | None = None, *, root: Path | None = None) -> Path:
	"""
	No-op function for compatibility. Returns the would-be path but does nothing.
	"""
	name = instance_name.strip()
	path = _instance_dir(name, root=root) / "events.log"
	return path


class PromptRecord(BaseModel):
	"""Record for a prompt version."""
	ts: str
	instance: str
	version: int
	system: Optional[str] = None
	template: str
	variables: List[str] = []


def _parse_version_from_name(path: Path) -> Optional[int]:
	"""Parse version number from filename."""
	stem = path.stem  # e.g., "<name>__prompt__v12"
	if "__prompt__v" not in stem:
		return None
	try:
		return int(stem.split("__prompt__v", 1)[1])
	except Exception:
		return None


def list_prompt_versions(instance_name: str, *, root: Path | None = None) -> List[Path]:
	"""Return all prompt version files for an instance."""
	name = instance_name.strip()
	dir_path = _instance_dir(name, root=root)
	if not dir_path.exists():
		return []
	json_files = [p for p in dir_path.glob(f"{name}__prompt__v*.json") if p.is_file()]
	return sorted(json_files, key=lambda p: (_parse_version_from_name(p) or 0))


def next_prompt_version(instance_name: str, *, root: Path | None = None) -> int:
	"""Compute the next version number for a prompt instance."""
	existing = list_prompt_versions(instance_name, root=root)
	if not existing:
		return 1
	last_version = _parse_version_from_name(existing[-1])
	return (last_version + 1) if last_version is not None else 1


def final_prompt_path(instance_name: str, *, root: Path | None = None) -> Path:
	"""Get the path to the final prompt file."""
	name = instance_name.strip()
	return _instance_dir(name, root=root) / "final_prompt.json"


def based_on_versions(instance_name: str, *, root: Path | None = None) -> List[int]:
	"""Return list of version numbers for an instance."""
	versions = list_prompt_versions(instance_name, root=root)
	version_nums: List[int] = []
	for v_path in versions:
		v_num = _parse_version_from_name(v_path)
		if v_num is not None:
			version_nums.append(v_num)
	return version_nums


def read_final_prompt(instance_name: str, *, root: Path | None = None) -> tuple[str | None, str] | None:
	"""Read the final prompt if it exists."""
	path = final_prompt_path(instance_name, root=root)
	if not path.exists():
		return None
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
		return data.get("system"), data.get("template", "")
	except Exception:
		return None


def save_final_prompt(
	instance_name: str,
	*,
	system: str | None,
	template: str,
	variables: List[str],
	root: Path | None = None,
) -> Path:
	"""Save the final synthesized prompt."""
	name = instance_name.strip()
	target_dir = _instance_dir(name, root=root)
	target_dir.mkdir(parents=True, exist_ok=True)
	
	json_path = target_dir / "final_prompt.json"
	
	record = {
		"ts": _ts(),
		"instance": name,
		"version": -1,  # Special marker for final prompt
		"system": system,
		"template": template,
		"variables": sorted(variables),
	}
	
	json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
	return json_path


def save_prompt_version(
	instance_name: str,
	*,
	system: Optional[str],
	template: str,
	variables: List[str] | None = None,
	user_text: str = "",
	root: Path | None = None,
) -> tuple[Path, bool]:
	"""
	Save a new prompt version if it differs from the last saved version.
	
	Returns:
		tuple[Path, bool]: (path to version file, True if new version was created)
	"""
	name = instance_name.strip()
	if not name:
		raise ValueError("instance_name cannot be empty")
	
	target_dir = _instance_dir(name, root=root)
	target_dir.mkdir(parents=True, exist_ok=True)

	# Normalize variables to a list of strings
	var_list: List[str] = []
	if variables:
		var_list = sorted([str(v) for v in variables])

	# Check if ANY existing version is identical (not just the last one)
	existing_versions = list_prompt_versions(name, root=root)
	if existing_versions:
		# Helper function to normalize values for comparison
		def normalize_system(s):
			if s is None or s == "null":
				return None
			return str(s).strip() if s else None
		
		# Normalize current prompt for comparison
		current_system_norm = normalize_system(system)
		current_template_norm = template.strip() if template else ""
		current_vars_norm = sorted([str(v).strip() for v in var_list])
		
		# Check each existing version
		for version_path in existing_versions:
			try:
				version_data = json.loads(version_path.read_text(encoding="utf-8"))
				# Compare only the critical fields (system, template, variables)
				# EXCLUDE timestamp ('ts') and 'version' from comparison
				existing_system = version_data.get("system")
				existing_template = version_data.get("template")
				existing_variables = version_data.get("variables", [])
				
				# Normalize existing version for comparison
				existing_system_norm = normalize_system(existing_system)
				existing_template_norm = existing_template.strip() if existing_template else ""
				existing_vars_norm = sorted([str(v).strip() for v in existing_variables])
				
				# Compare
				system_match = current_system_norm == existing_system_norm
				template_match = current_template_norm == existing_template_norm
				variables_match = current_vars_norm == existing_vars_norm
				
				if system_match and template_match and variables_match:
					# Found an identical version - return it without creating a new one
					return version_path, False
			except Exception:
				# Skip this version if we can't read it
				continue

	# Create new version
	next_version = next_prompt_version(name, root=root)
	json_path = target_dir / f"{name}__prompt__v{next_version}.json"

	record = PromptRecord(
		ts=_ts(),
		instance=name,
		version=next_version,
		system=system,
		template=template,
		variables=var_list,
	)
	
	json_path.write_text(json.dumps(record.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
	return json_path, True


