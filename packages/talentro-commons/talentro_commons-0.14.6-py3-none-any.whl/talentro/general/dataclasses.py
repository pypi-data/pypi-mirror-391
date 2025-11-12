from abc import abstractmethod, ABC
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class SelectionMethod(StrEnum):
    LIST = 'list'
    ALL = 'all'
    RULES = 'rules'


class ResolvableModel(BaseModel, ABC):

    @staticmethod
    @abstractmethod
    async def resolve_object(object_id: UUID) -> "ResolvableModel":
        pass


class ResolvableCompanyModel(BaseModel, ABC):

    @staticmethod
    @abstractmethod
    async def resolve_object(object_id: UUID, organization_id: str) -> "ResolvableCompanyModel":
        pass


@dataclass
class DropdownOption:
    value: str
    label: str
    detail: str | None = None


@dataclass
class VacancySelectionRule:
    field: str
    operator: str
    value: str


@dataclass
class VacancySelectionCriteria:
    rules: list[VacancySelectionRule]
    selected_vacancies: list[UUID]
    selection_method: SelectionMethod
