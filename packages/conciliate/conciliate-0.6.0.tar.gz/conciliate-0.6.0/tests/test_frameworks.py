"""Test Flask and Express spec generation."""

import pytest
from pathlib import Path
from conciliate.spec_generator import SpecGenerator
from conciliate.config import ConciliateConfig


def test_fastapi_detection():
    """Test FastAPI framework auto-detection."""
    config = ConciliateConfig(
        backend_path="./example/backend",
        framework="auto"
    )
    generator = SpecGenerator(config)
    detected = generator._detect_framework()
    assert detected == "fastapi"

def test_flask_detection():
    """Test Flask framework auto-detection."""
    config = ConciliateConfig(
        backend_path="./example/flask-backend",
        framework="auto"
    )
    generator = SpecGenerator(config)
    detected = generator._detect_framework()
    assert detected == "flask"


def test_express_detection():
    """Test Express framework auto-detection."""
    config = ConciliateConfig(
        backend_path="./example/express-backend",
        framework="auto"
    )
    generator = SpecGenerator(config)
    detected = generator._detect_framework()
    assert detected == "express"


def test_fastapi_spec_generation():
    """Test FastAPI OpenAPI spec generation."""
    config = ConciliateConfig(
        backend_path="./example/backend",
        framework="fastapi"
    )
    generator = SpecGenerator(config)
    spec = generator.generate()
    
    assert "openapi" in spec
    assert spec["openapi"] == "3.1.0"
    assert "paths" in spec
    assert "/" in spec["paths"]
    print(spec["paths"].keys())
    assert "/users" in spec["paths"]

def test_flask_spec_generation():
    """Test Flask OpenAPI spec generation."""
    config = ConciliateConfig(
        backend_path="./example/flask-backend",
        framework="flask"
    )
    generator = SpecGenerator(config)
    spec = generator.generate()
    
    assert "openapi" in spec
    assert spec["openapi"] == "3.0.0"
    assert "paths" in spec
    assert "/" in spec["paths"]
    assert "/api/users" in spec["paths"]


def test_express_spec_generation():
    """Test Express OpenAPI spec generation."""
    config = ConciliateConfig(
        backend_path="./example/express-backend",
        framework="express"
    )
    generator = SpecGenerator(config)
    spec = generator.generate()
    
    assert "openapi" in spec
    assert spec["openapi"] == "3.0.0"
    assert "paths" in spec
    assert "/" in spec["paths"]
    assert "/api/users" in spec["paths"]
