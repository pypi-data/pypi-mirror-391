"""Diff engine for comparing API specifications."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from deepdiff import DeepDiff


class DiffResult:
    """Represents the result of a spec diff operation."""
    
    def __init__(self, diff: DeepDiff, old_spec: Dict[str, Any], new_spec: Dict[str, Any]):
        self.diff = diff
        self.old_spec = old_spec
        self.new_spec = new_spec
        self.timestamp = datetime.utcnow().isoformat()
    
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return bool(self.diff)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert diff result to dictionary."""
        return {
            "timestamp": self.timestamp,
            "has_changes": self.has_changes(),
            "changes": json.loads(self.diff.to_json()) if self.diff else {},
            "summary": self.get_summary(),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate a human-readable summary of changes."""
        if not self.has_changes():
            return {"message": "No changes detected"}
        
        summary = {
            "endpoints_added": [],
            "endpoints_removed": [],
            "endpoints_modified": [],
            "schemas_added": [],
            "schemas_removed": [],
            "schemas_modified": [],
        }
        
        diff_dict = self.diff.to_dict()
        
        # Check for path changes (endpoints)
        if "dictionary_item_added" in diff_dict:
            for item in diff_dict["dictionary_item_added"]:
                if "root['paths']" in item:
                    endpoint = item.split("['paths']['")[1].rstrip("']")
                    summary["endpoints_added"].append(endpoint)
                elif "root['components']['schemas']" in item:
                    schema = item.split("['schemas']['")[1].rstrip("']")
                    summary["schemas_added"].append(schema)
        
        if "dictionary_item_removed" in diff_dict:
            for item in diff_dict["dictionary_item_removed"]:
                if "root['paths']" in item:
                    endpoint = item.split("['paths']['")[1].rstrip("']")
                    summary["endpoints_removed"].append(endpoint)
                elif "root['components']['schemas']" in item:
                    schema = item.split("['schemas']['")[1].rstrip("']")
                    summary["schemas_removed"].append(schema)
        
        if "values_changed" in diff_dict or "dictionary_item_added" in diff_dict:
            # Track modified endpoints
            old_paths = set(self.old_spec.get("paths", {}).keys())
            new_paths = set(self.new_spec.get("paths", {}).keys())
            modified = old_paths.intersection(new_paths)
            
            for path in modified:
                old_path_def = self.old_spec.get("paths", {}).get(path, {})
                new_path_def = self.new_spec.get("paths", {}).get(path, {})
                if old_path_def != new_path_def:
                    summary["endpoints_modified"].append(path)
        
        return summary
    
    def to_json(self) -> str:
        """Convert diff result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class DiffEngine:
    """Compares API specifications and detects changes."""
    
    def __init__(self):
        self.last_spec: Optional[Dict[str, Any]] = None
        self.last_diff: Optional[DiffResult] = None
    
    def compare(
        self,
        old_spec: Dict[str, Any],
        new_spec: Dict[str, Any],
        ignore_metadata: bool = True
    ) -> DiffResult:
        """
        Compare two API specifications.
        
        Args:
            old_spec: Previous API specification
            new_spec: Current API specification
            ignore_metadata: If True, ignore metadata fields like version, title, etc.
        
        Returns:
            DiffResult containing the differences
        """
        exclude_paths = []
        
        if ignore_metadata:
            # Ignore common metadata fields that change frequently
            exclude_paths = [
                "root['info']['version']",
                "root['servers']",
                "root['openapi']",
            ]
        
        diff = DeepDiff(
            old_spec,
            new_spec,
            exclude_paths=exclude_paths,
            ignore_order=True,
            report_repetition=True,
        )
        
        result = DiffResult(diff, old_spec, new_spec)
        self.last_diff = result
        
        return result
    
    def check_new_spec(self, new_spec: Dict[str, Any]) -> Optional[DiffResult]:
        """
        Check a new spec against the last known spec.
        
        Args:
            new_spec: New API specification to check
        
        Returns:
            DiffResult if there's a previous spec to compare, None otherwise
        """
        if self.last_spec is None:
            self.last_spec = new_spec
            return None
        
        result = self.compare(self.last_spec, new_spec)
        
        if result.has_changes():
            self.last_spec = new_spec
        
        return result
    
    def update_spec(self, spec: Dict[str, Any]) -> None:
        """Update the stored spec without comparing."""
        self.last_spec = spec


def compare_specs(
    old_spec: Dict[str, Any],
    new_spec: Dict[str, Any]
) -> DiffResult:
    """
    Convenience function to compare two specs.
    
    Args:
        old_spec: Previous API specification
        new_spec: Current API specification
    
    Returns:
        DiffResult containing the differences
    """
    engine = DiffEngine()
    return engine.compare(old_spec, new_spec)
