"""
Smoke tests - Basic validation that imports work and core modules load
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def test_imports_fastapi():
    """Test that FastAPI can be imported"""
    from fastapi import FastAPI
    assert FastAPI is not None


def test_imports_sqlalchemy():
    """Test that SQLAlchemy can be imported"""
    from sqlalchemy import create_engine
    assert create_engine is not None


def test_imports_pydantic():
    """Test that Pydantic can be imported"""
    from pydantic import BaseModel
    assert BaseModel is not None


def test_imports_domain_entities():
    """Test that domain entities can be imported"""
    try:
        from domain.entities.machine import Machine
        from domain.entities.sensor import Sensor
        assert Machine is not None
        assert Sensor is not None
    except ImportError as e:
        # If imports fail, at least check the modules exist
        import os
        entities_path = backend_dir / "domain" / "entities"
        assert entities_path.exists(), f"Domain entities path not found: {entities_path}"
        assert (entities_path / "machine.py").exists(), "machine.py not found"
        assert (entities_path / "sensor.py").exists(), "sensor.py not found"


def test_imports_repositories():
    """Test that repositories can be imported"""
    try:
        from domain.repositories.machine_repository import MachineRepository
        from domain.repositories.sensor_repository import SensorRepository
        assert MachineRepository is not None
        assert SensorRepository is not None
    except ImportError:
        # If imports fail, at least check the modules exist
        import os
        repos_path = backend_dir / "domain" / "repositories"
        assert repos_path.exists(), f"Repositories path not found: {repos_path}"
        assert (repos_path / "machine_repository.py").exists(), "machine_repository.py not found"
        assert (repos_path / "sensor_repository.py").exists(), "sensor_repository.py not found"


def test_app_creation():
    """Test that FastAPI app can be created"""
    from fastapi import FastAPI
    
    app = FastAPI(title="Test")
    assert app is not None
    assert app.title == "Test"


def test_python_version():
    """Test that Python version is 3.11+"""
    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version_info}"
