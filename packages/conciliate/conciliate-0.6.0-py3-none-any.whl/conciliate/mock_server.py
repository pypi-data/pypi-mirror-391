"""
Mock Server Mode - Generate fake API responses from OpenAPI spec
"""

import json
import random
import string
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()


class MockDataGenerator:
    """Generate mock data based on OpenAPI schema"""

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
            Faker.seed(seed)

    def generate_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Generate mock data from JSON schema"""
        
        # Handle $ref references
        if "$ref" in schema:
            # For now, return a placeholder
            return {"$ref": schema["$ref"]}

        schema_type = schema.get("type", "string")
        
        # Handle enums
        if "enum" in schema:
            return random.choice(schema["enum"])
        
        # Handle examples
        if "example" in schema:
            return schema["example"]
        
        # Generate based on type
        if schema_type == "string":
            return self._generate_string(schema)
        elif schema_type == "number":
            return self._generate_number(schema)
        elif schema_type == "integer":
            return self._generate_integer(schema)
        elif schema_type == "boolean":
            return random.choice([True, False])
        elif schema_type == "array":
            return self._generate_array(schema)
        elif schema_type == "object":
            return self._generate_object(schema)
        elif schema_type == "null":
            return None
        else:
            return None

    def _generate_string(self, schema: Dict[str, Any]) -> str:
        """Generate string based on format and pattern"""
        format_type = schema.get("format", "")
        
        # Format-based generation
        if format_type == "date":
            return fake.date()
        elif format_type == "date-time":
            return fake.iso8601()
        elif format_type == "email":
            return fake.email()
        elif format_type == "uuid":
            return fake.uuid4()
        elif format_type == "uri":
            return fake.url()
        elif format_type == "hostname":
            return fake.hostname()
        elif format_type == "ipv4":
            return fake.ipv4()
        elif format_type == "ipv6":
            return fake.ipv6()
        
        # Pattern-based generation
        if "pattern" in schema:
            # Simple pattern matching
            pattern = schema["pattern"]
            if pattern == "^[0-9]+$":
                return str(random.randint(1000, 9999))
            elif pattern.startswith("^[a-zA-Z]"):
                return fake.word()
        
        # Length constraints
        min_length = schema.get("minLength", 5)
        max_length = schema.get("maxLength", 50)
        
        # Field name hints
        field_name = schema.get("title", "").lower()
        if "name" in field_name:
            return fake.name()
        elif "email" in field_name:
            return fake.email()
        elif "address" in field_name:
            return fake.address()
        elif "phone" in field_name:
            return fake.phone_number()
        elif "city" in field_name:
            return fake.city()
        elif "country" in field_name:
            return fake.country()
        elif "description" in field_name:
            return fake.text(max_nb_chars=max_length)
        elif "title" in field_name:
            return fake.sentence()
        
        # Default string generation
        length = random.randint(min_length, min(max_length, min_length + 20))
        return fake.text(max_nb_chars=length)[:length]

    def _generate_number(self, schema: Dict[str, Any]) -> float:
        """Generate number with constraints"""
        minimum = schema.get("minimum", 0.0)
        maximum = schema.get("maximum", 1000.0)
        multiple_of = schema.get("multipleOf")
        
        if multiple_of:
            steps = int((maximum - minimum) / multiple_of)
            return minimum + (random.randint(0, steps) * multiple_of)
        
        return round(random.uniform(minimum, maximum), 2)

    def _generate_integer(self, schema: Dict[str, Any]) -> int:
        """Generate integer with constraints"""
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 1000)
        multiple_of = schema.get("multipleOf", 1)
        
        if multiple_of > 1:
            steps = (maximum - minimum) // multiple_of
            return minimum + (random.randint(0, steps) * multiple_of)
        
        return random.randint(minimum, maximum)

    def _generate_array(self, schema: Dict[str, Any]) -> list:
        """Generate array with items"""
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 5)
        
        count = random.randint(min_items, max_items)
        return [self.generate_from_schema(items_schema) for _ in range(count)]

    def _generate_object(self, schema: Dict[str, Any]) -> dict:
        """Generate object with properties"""
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        result = {}
        
        # Always include required properties
        for prop_name in required:
            if prop_name in properties:
                result[prop_name] = self.generate_from_schema(properties[prop_name])
        
        # Randomly include optional properties (50% chance)
        for prop_name, prop_schema in properties.items():
            if prop_name not in required and random.random() > 0.5:
                result[prop_name] = self.generate_from_schema(prop_schema)
        
        return result


class MockServer:
    """Mock server for generating fake API responses"""

    def __init__(self, spec: Dict[str, Any], delay_range: tuple = (0, 0)):
        self.spec = spec
        self.delay_min, self.delay_max = delay_range
        self.generator = MockDataGenerator()

    def get_mock_response(self, path: str, method: str) -> Dict[str, Any]:
        """Generate mock response for endpoint"""
        
        # Find endpoint in spec
        endpoint = self._find_endpoint(path, method)
        if not endpoint:
            return {
                "status": 404,
                "headers": {"Content-Type": "application/json"},
                "body": {"error": "Endpoint not found in spec"}
            }

        # Get successful response schema (200, 201, etc.)
        responses = endpoint.get("responses", {})
        success_response = None
        
        for status_code in ["200", "201", "202"]:
            if status_code in responses:
                success_response = responses[status_code]
                break
        
        if not success_response:
            # Try default response
            success_response = responses.get("default", {})
        
        if not success_response:
            return {
                "status": 501,
                "headers": {"Content-Type": "application/json"},
                "body": {"error": "No response schema defined"}
            }

        # Extract response schema
        content = success_response.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        if not schema:
            return {
                "status": 204,
                "headers": {"Content-Type": "application/json"},
                "body": None
            }

        # Generate mock data
        mock_data = self.generator.generate_from_schema(schema)

        return {
            "status": int(list(responses.keys())[0]) if responses else 200,
            "headers": {
                "Content-Type": "application/json",
                "X-Mock-Server": "Conciliate"
            },
            "body": mock_data
        }

    def _find_endpoint(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """Find endpoint definition in OpenAPI spec"""
        paths = self.spec.get("paths", {})
        
        # Exact match
        if path in paths:
            path_item = paths[path]
            return path_item.get(method.lower())
        
        # Try path parameter matching
        for spec_path, path_item in paths.items():
            if self._match_path(path, spec_path):
                return path_item.get(method.lower())
        
        return None

    def _match_path(self, actual_path: str, spec_path: str) -> bool:
        """Match path with path parameters"""
        actual_parts = actual_path.split("/")
        spec_parts = spec_path.split("/")
        
        if len(actual_parts) != len(spec_parts):
            return False
        
        for actual, spec in zip(actual_parts, spec_parts):
            # Path parameter (e.g., {id})
            if spec.startswith("{") and spec.endswith("}"):
                continue
            # Exact match required
            if actual != spec:
                return False
        
        return True


def create_mock_endpoint_handler(spec: Dict[str, Any], delay_range: tuple = (0, 0)):
    """Create a FastAPI endpoint handler for mock server"""
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import asyncio
    
    mock_server = MockServer(spec, delay_range)
    
    async def handle_mock_request(request: Request):
        """Handle mock API request"""
        path = request.url.path
        method = request.method
        
        # Simulate delay
        if delay_range[1] > 0:
            delay = random.uniform(delay_range[0], delay_range[1])
            await asyncio.sleep(delay / 1000)  # Convert ms to seconds
        
        # Generate mock response
        response = mock_server.get_mock_response(path, method)
        
        return JSONResponse(
            content=response["body"],
            status_code=response["status"],
            headers=response["headers"]
        )
    
    return handle_mock_request
