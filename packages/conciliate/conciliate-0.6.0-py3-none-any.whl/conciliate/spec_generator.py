"""Spec generator for extracting API specifications from backend frameworks."""

import importlib.util
import sys
import re
import ast
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import subprocess

from .config import ConciliateConfig


class SpecGeneratorError(Exception):
    """Exception raised when spec generation fails."""
    pass


class SpecGenerator:
    """Generates API specifications from backend code."""
    
    def __init__(self, config: ConciliateConfig):
        self.config = config
        self.backend_path = Path(config.backend_path)
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate OpenAPI spec from backend.
        
        Returns:
            OpenAPI specification as dictionary
        
        Raises:
            SpecGeneratorError: If spec generation fails
        """
        # Auto-detect framework if set to 'auto'
        framework = self.config.framework.lower()
        if framework == "auto":
            framework = self._detect_framework()
        
        if framework == "fastapi":
            return self._generate_fastapi_spec()
        elif framework == "flask":
            return self._generate_flask_spec()
        elif framework == "express":
            return self._generate_express_spec()
        elif self.config.custom_spec_command:
            return self._generate_from_command()
        else:
            raise SpecGeneratorError(
                f"Unsupported framework: {framework}. "
                "Supported: fastapi, flask, express. "
                "Or specify custom_spec_command in .conciliate.yaml"
            )
    
    def _generate_fastapi_spec(self) -> Dict[str, Any]:
        """
        Extract OpenAPI spec from FastAPI application.
        
        Returns:
            OpenAPI specification dictionary
        """
        # Find main.py or app.py in backend directory
        main_file = self._find_fastapi_app()
        
        if not main_file:
            raise SpecGeneratorError(
                "Could not find FastAPI app. Looking for main.py or app.py "
                f"in {self.backend_path}"
            )
        
        # Try to import and extract spec
        try:
            spec = self._import_and_extract_spec(main_file)
            return spec
        except Exception as e:
            raise SpecGeneratorError(f"Failed to extract FastAPI spec: {e}")
    
    def _find_fastapi_app(self) -> Optional[Path]:
        """Find the main FastAPI application file."""
        candidates = ["main.py", "app.py", "api.py", "server.py"]
        
        for candidate in candidates:
            app_file = self.backend_path / candidate
            if app_file.exists():
                return app_file
        
        # Search recursively
        for py_file in self.backend_path.rglob("*.py"):
            if py_file.name in candidates:
                return py_file
        
        return None
    
    def _import_and_extract_spec(self, app_file: Path) -> Dict[str, Any]:
        """
        Import FastAPI app and extract OpenAPI schema.
        
        Args:
            app_file: Path to the FastAPI application file
        
        Returns:
            OpenAPI specification dictionary
        """
        # Add backend directory to Python path
        backend_path_str = str(self.backend_path.resolve())
        if backend_path_str not in sys.path:
            sys.path.insert(0, backend_path_str)
        
        # Import the module
        module_name = app_file.stem
        spec = importlib.util.spec_from_file_location(module_name, app_file)
        
        if spec is None or spec.loader is None:
            raise SpecGeneratorError(f"Could not load module from {app_file}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Find FastAPI app instance
        app = None
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue
            attr = getattr(module, attr_name)
            # Check if it's a FastAPI instance (not the class itself)
            # FastAPI instances have openapi method and routes attribute
            if (hasattr(attr, "openapi") and 
                hasattr(attr, "routes") and 
                callable(getattr(attr, "openapi", None)) and
                not isinstance(attr, type)):  # Ensure it's not a class
                app = attr
                break
        
        if app is None:
            raise SpecGeneratorError(f"No FastAPI app instance found in {app_file}")
        
        # Extract OpenAPI schema
        openapi_schema = app.openapi()
        
        return openapi_schema
    
    def _generate_from_command(self) -> Dict[str, Any]:
        """
        Generate spec using custom command.
        
        Returns:
            OpenAPI specification dictionary
        """
        if not self.config.custom_spec_command:
            raise SpecGeneratorError("No custom spec command configured")
        
        try:
            result = subprocess.run(
                self.config.custom_spec_command,
                shell=True,
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode != 0:
                raise SpecGeneratorError(
                    f"Custom command failed: {result.stderr}"
                )
            
            # Parse JSON output
            spec = json.loads(result.stdout)
            return spec
            
        except subprocess.TimeoutExpired:
            raise SpecGeneratorError("Custom command timed out")
        except json.JSONDecodeError as e:
            raise SpecGeneratorError(f"Invalid JSON output from custom command: {e}")
        except Exception as e:
            raise SpecGeneratorError(f"Failed to run custom command: {e}")
    
    def _detect_framework(self) -> str:
        """
        Auto-detect backend framework by inspecting files.
        
        Returns:
            Detected framework name (fastapi, flask, or express)
        """
        # Check Python files for FastAPI/Flask
        for py_file in self.backend_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # Check for FastAPI
                if "from fastapi import" in content or "import fastapi" in content:
                    return "fastapi"
                
                # Check for Flask
                if "from flask import" in content or "import flask" in content:
                    return "flask"
                    
            except Exception:
                continue
        
        # Check JavaScript/TypeScript files for Express
        for js_file in self.backend_path.rglob("*.js"):
            try:
                content = js_file.read_text(encoding="utf-8")
                if "express()" in content or "require('express')" in content:
                    return "express"
            except Exception:
                continue
        
        for ts_file in self.backend_path.rglob("*.ts"):
            try:
                content = ts_file.read_text(encoding="utf-8")
                if "express()" in content or "from 'express'" in content:
                    return "express"
            except Exception:
                continue
        
        # Default to fastapi if nothing detected
        return "fastapi"
    
    def _generate_flask_spec(self) -> Dict[str, Any]:
        """
        Extract OpenAPI spec from Flask application.
        
        Returns:
            OpenAPI specification dictionary
        """
        app_file = self._find_flask_app()
        
        if not app_file:
            raise SpecGeneratorError(
                "Could not find Flask app. Looking for main.py or app.py "
                f"in {self.backend_path}"
            )
        
        try:
            # Extract routes from Flask app
            routes = self._extract_flask_routes(app_file)
            
            # Build OpenAPI spec from routes
            spec = self._build_openapi_from_routes(routes, "Flask")
            return spec
            
        except Exception as e:
            raise SpecGeneratorError(f"Failed to extract Flask spec: {e}")
    
    def _generate_express_spec(self) -> Dict[str, Any]:
        """
        Extract OpenAPI spec from Express application.
        
        Returns:
            OpenAPI specification dictionary
        """
        app_file = self._find_express_app()
        
        if not app_file:
            raise SpecGeneratorError(
                "Could not find Express app. Looking for index.js, app.js, or server.js "
                f"in {self.backend_path}"
            )
        
        try:
            # Extract routes from Express app
            routes = self._extract_express_routes(app_file)
            
            # Build OpenAPI spec from routes
            spec = self._build_openapi_from_routes(routes, "Express")
            return spec
            
        except Exception as e:
            raise SpecGeneratorError(f"Failed to extract Express spec: {e}")
    
    def _find_flask_app(self) -> Optional[Path]:
        """Find the main Flask application file."""
        candidates = ["app.py", "main.py", "application.py", "server.py"]
        
        for candidate in candidates:
            app_file = self.backend_path / candidate
            if app_file.exists():
                # Verify it contains Flask
                try:
                    content = app_file.read_text(encoding="utf-8")
                    if "flask" in content.lower():
                        return app_file
                except Exception:
                    continue
        
        # Search recursively
        for py_file in self.backend_path.rglob("*.py"):
            if py_file.name in candidates:
                try:
                    content = py_file.read_text(encoding="utf-8")
                    if "flask" in content.lower():
                        return py_file
                except Exception:
                    continue
        
        return None
    
    def _find_express_app(self) -> Optional[Path]:
        """Find the main Express application file."""
        candidates = ["index.js", "app.js", "server.js", "main.js", "index.ts", "app.ts", "server.ts"]
        
        for candidate in candidates:
            app_file = self.backend_path / candidate
            if app_file.exists():
                # Verify it contains Express
                try:
                    content = app_file.read_text(encoding="utf-8")
                    if "express" in content.lower():
                        return app_file
                except Exception:
                    continue
        
        # Search in src directory
        src_dir = self.backend_path / "src"
        if src_dir.exists():
            for candidate in candidates:
                app_file = src_dir / candidate
                if app_file.exists():
                    try:
                        content = app_file.read_text(encoding="utf-8")
                        if "express" in content.lower():
                            return app_file
                    except Exception:
                        continue
        
        return None
    
    def _extract_flask_routes(self, app_file: Path) -> List[Dict[str, Any]]:
        """
        Extract routes from Flask application using AST parsing.
        
        Args:
            app_file: Path to Flask application file
            
        Returns:
            List of route dictionaries
        """
        routes = []
        
        try:
            content = app_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for route decorator
                    for decorator in node.decorator_list:
                        route_info = self._parse_flask_decorator(decorator, node)
                        if route_info:
                            routes.append(route_info)
                            
        except Exception as e:
            raise SpecGeneratorError(f"Failed to parse Flask routes: {e}")
        
        return routes
    
    def _parse_flask_decorator(self, decorator: ast.expr, func: ast.FunctionDef) -> Optional[Dict[str, Any]]:
        """Parse Flask route decorator."""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                # app.route(), blueprint.route()
                if decorator.func.attr == "route":
                    path = "/"
                    methods = ["GET"]
                    
                    # Extract path
                    if decorator.args:
                        if isinstance(decorator.args[0], ast.Constant):
                            path = decorator.args[0].value
                    
                    # Extract methods
                    for keyword in decorator.keywords:
                        if keyword.arg == "methods":
                            if isinstance(keyword.value, ast.List):
                                methods = [
                                    elt.value for elt in keyword.value.elts
                                    if isinstance(elt, ast.Constant)
                                ]
                    
                    return {
                        "path": path,
                        "methods": methods,
                        "function": func.name,
                        "description": ast.get_docstring(func) or f"{func.name} endpoint"
                    }
        
        return None
    
    def _extract_express_routes(self, app_file: Path) -> List[Dict[str, Any]]:
        """
        Extract routes from Express application using regex parsing.
        
        Args:
            app_file: Path to Express application file
            
        Returns:
            List of route dictionaries
        """
        routes = []
        
        try:
            content = app_file.read_text(encoding="utf-8")
            
            # Pattern: app.get('/path', ...), app.post('/path', ...), etc.
            route_pattern = r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"
            
            for match in re.finditer(route_pattern, content):
                method = match.group(1).upper()
                path = match.group(2)
                
                routes.append({
                    "path": path,
                    "methods": [method],
                    "function": f"{method.lower()}_{path.replace('/', '_').strip('_')}",
                    "description": f"{method} {path}"
                })
                
        except Exception as e:
            raise SpecGeneratorError(f"Failed to parse Express routes: {e}")
        
        return routes
    
    def _build_openapi_from_routes(self, routes: List[Dict[str, Any]], framework: str) -> Dict[str, Any]:
        """
        Build OpenAPI specification from extracted routes.
        
        Args:
            routes: List of route dictionaries
            framework: Framework name (Flask or Express)
            
        Returns:
            OpenAPI specification dictionary
        """
        paths = {}
        
        for route in routes:
            path = route["path"]
            if path not in paths:
                paths[path] = {}
            
            for method in route["methods"]:
                paths[path][method.lower()] = {
                    "summary": route["description"],
                    "operationId": route["function"],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{framework} API",
                "version": "1.0.0",
                "description": f"Auto-generated API specification from {framework} application"
            },
            "paths": paths
        }
        
        return spec


def generate_spec(config: ConciliateConfig) -> Dict[str, Any]:
    """
    Convenience function to generate API spec.
    
    Args:
        config: Conciliate configuration
    
    Returns:
        OpenAPI specification dictionary
    """
    generator = SpecGenerator(config)
    return generator.generate()
