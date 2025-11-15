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
        stmt = select(MachineModel).where(MachineModel.machine_id == machine_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            return self._model_to_entity(model)
        return None

    async def get_all(self) -> List[Machine]:
        stmt = select(MachineModel).order_by(MachineModel.machine_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def save(self, machine: Machine) -> Machine:
        stmt = select(MachineModel).where(MachineModel.machine_id == machine.machine_id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            setattr(existing, 'machine_type', machine.machine_type)
            setattr(existing, 'location', machine.location)
            setattr(existing, 'operational', machine.operational)
            if hasattr(existing, 'updated_at'):
                setattr(existing, 'updated_at', datetime.utcnow())
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
        return Machine(
            machine_id=str(model.machine_id),
            machine_type=str(model.machine_type),
            location=str(model.location),
            operational=bool(model.operational),
        )

    def _entity_to_model(self, entity: Machine) -> MachineModel:
        return MachineModel(
            machine_id=str(entity.machine_id),
            machine_type=str(entity.machine_type),
            location=str(entity.location),
            operational=bool(entity.operational),
        )

    async def find_by_id(self, machine_id: UUID) -> Optional[Machine]:
        raise NotImplementedError

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
