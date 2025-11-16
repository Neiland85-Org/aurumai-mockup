"""
Concrete PostgreSQL implementation of IMachineRepository
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.machine import Machine
from domain.repositories.machine_repository import IMachineRepository
from infrastructure.db.models import MachineModel


class PostgresMachineRepository(IMachineRepository):
    """PostgreSQL implementation of machine repository"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_id(self, machine_id: str) -> Optional[Machine]:
        stmt = select(MachineModel).where(MachineModel.machine_id == machine_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            return self._model_to_entity(model)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Machine]:
        stmt = select(MachineModel).order_by(MachineModel.machine_id)
        if skip:
            stmt = stmt.offset(skip)
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def save(self, machine: Machine) -> Machine:
        stmt = select(MachineModel).where(MachineModel.machine_id == machine.machine_id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            # Actualiza los campos principales
            existing.machine_type = machine.machine_type
            existing.location = machine.location
            existing.operational = machine.operational
            # Solo actualiza updated_at si existe el campo
            if hasattr(existing, "updated_at"):
                existing.updated_at = datetime.utcnow()
            model = existing
        else:
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
        stmt = select(MachineModel).where(MachineModel.machine_id == machine_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

    async def exists(self, machine_id: str) -> bool:
        stmt = select(MachineModel.id).where(MachineModel.machine_id == machine_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _model_to_entity(self, model: MachineModel) -> Machine:
        """Convert SQLAlchemy model to domain entity"""
        return Machine(
            machine_id=str(getattr(model, "machine_id", "")),
            machine_type=str(getattr(model, "machine_type", "")),
            location=str(getattr(model, "location", "")),
            operational=bool(getattr(model, "operational", False)),
        )

    def _entity_to_model(self, entity: Machine) -> MachineModel:
        return MachineModel(
            machine_id=str(entity.machine_id),
            machine_type=str(entity.machine_type),
            location=str(entity.location),
            operational=bool(entity.operational),
        )

    async def find_by_code(self, tenant_id: UUID, code: str) -> Optional[Machine]:
        raise NotImplementedError

    async def find_by_site(
        self, site_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Machine]:
        raise NotImplementedError

    async def find_by_tenant(
        self, tenant_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Machine]:
        raise NotImplementedError
