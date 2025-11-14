"""
Concrete PostgreSQL implementation of IMachineRepository
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.machine_repository import IMachineRepository
from domain.entities.machine import Machine
from infrastructure.db.models import MachineModel


class PostgresMachineRepository(IMachineRepository):
    """PostgreSQL implementation of machine repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, machine_id: str) -> Optional[Machine]:
        """Get machine by ID"""
        stmt = select(MachineModel).where(MachineModel.machine_id == machine_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self._model_to_entity(model)
        return None

    async def get_all(self) -> List[Machine]:
        """Get all machines"""
        stmt = select(MachineModel).order_by(MachineModel.machine_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def save(self, machine: Machine) -> Machine:
        """Save or update machine"""
        # Check if machine exists
        stmt = select(MachineModel).where(MachineModel.machine_id == machine.machine_id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.machine_type = machine.machine_type
            existing.location = machine.location
            existing.operational = machine.operational
            existing.updated_at = datetime.utcnow()
            model = existing
        else:
            # Create new
            model = MachineModel(
                machine_id=machine.machine_id,
                machine_type=machine.machine_type,
                location=machine.location,
                operational=machine.operational,
            )
            self.session.add(model)

        await self.session.flush()
        return self._model_to_entity(model)

    async def delete(self, machine_id: str) -> bool:
        """Delete machine by ID"""
        stmt = select(MachineModel).where(MachineModel.machine_id == machine_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

    async def exists(self, machine_id: str) -> bool:
        """Check if machine exists"""
        stmt = select(MachineModel.id).where(MachineModel.machine_id == machine_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _model_to_entity(self, model: MachineModel) -> Machine:
        """Convert SQLAlchemy model to domain entity"""
        return Machine(
            machine_id=model.machine_id,
            machine_type=model.machine_type,
            location=model.location,
            operational=model.operational,
        )

    def _entity_to_model(self, entity: Machine) -> MachineModel:
        """Convert domain entity to SQLAlchemy model"""
        return MachineModel(
            machine_id=entity.machine_id,
            machine_type=entity.machine_type,
            location=entity.location,
            operational=entity.operational,
        )

    async def find_by_id(self, machine_id: UUID) -> Optional[Machine]:
        raise NotImplementedError

    async def find_by_code(self, tenant_id: UUID, code: str) -> Optional[Machine]:
        raise NotImplementedError

    async def find_by_site(self, site_id: UUID, skip: int = 0, limit: int = 100) -> List[Machine]:
        raise NotImplementedError

    async def find_by_tenant(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[Machine]:
        raise NotImplementedError

