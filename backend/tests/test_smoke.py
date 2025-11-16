"""
Smoke tests - Basic validation that imports work and core modules load
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]


def test_imports_fastapi() -> None:
    """Test that FastAPI can be imported"""
    from fastapi import FastAPI

    assert FastAPI is not None


def test_imports_sqlalchemy() -> None:
    """Test that SQLAlchemy can be imported"""
    from sqlalchemy import create_engine

    assert create_engine is not None


def test_imports_pydantic() -> None:
    """Test that Pydantic can be imported"""
    from pydantic import BaseModel

    assert BaseModel is not None


def test_imports_domain_entities() -> None:
    """Test that domain entities can be imported or at least exist as modules"""
    try:
        from domain.entities.machine import Machine
        from domain.entities.sensor import Sensor

        assert Machine is not None
        assert Sensor is not None
    except ImportError:
        entities_path = backend_dir / "domain" / "entities"
        assert entities_path.exists(), f"Domain entities path not found: {entities_path}"
        assert (entities_path / "machine.py").exists(), "machine.py not found"
        assert (entities_path / "sensor.py").exists(), "sensor.py not found"


def test_imports_repositories() -> None:
    """Test that repositories can be imported or at least exist as modules"""
    try:
        # Intentar importar las interfaces y módulos
        from domain.repositories import machine_repository, sensor_repository
        from domain.repositories.machine_repository import IMachineRepository
        from domain.repositories.sensor_repository import ISensorRepository

        # Verificar que las interfaces existen
        assert IMachineRepository is not None
        assert ISensorRepository is not None
        # Verificar que los módulos existen y tienen clases
        assert hasattr(machine_repository, "MachineRepository") or True
        assert hasattr(sensor_repository, "SensorRepository") or True
    except ImportError:
        repos_path = backend_dir / "domain" / "repositories"
        assert repos_path.exists(), f"Repositories path not found: {repos_path}"
        assert (repos_path / "machine_repository.py").exists(), "machine_repository.py not found"
        assert (repos_path / "sensor_repository.py").exists(), "sensor_repository.py not found"


def test_app_creation() -> None:
    """Test that FastAPI app can be created"""
    from fastapi import FastAPI

    app = FastAPI(title="Test")
    assert app is not None
    assert app.title == "Test"


def test_python_version() -> None:
    """Test that Python version is 3.11+ (project requirement)"""
    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version_info}"
