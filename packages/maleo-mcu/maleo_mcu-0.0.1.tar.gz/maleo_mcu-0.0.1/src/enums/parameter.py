from enum import StrEnum
from maleo.types.string import ListOfStrs


class Granularity(StrEnum):
    STANDARD = "standard"
    FULL = "full"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]

    @property
    def column(self) -> str:
        return self.value


class ParameterGroup(StrEnum):
    ANAMNESIS = "Anamnesis"
    PHYSICAL_EXAMINATION = "Physical Examination"
    HEMATOLOGY = "Hematology"
    IMMUNOLOGY = "Immunology"
    CLINICAL_CHEMISTRY = "Clinical Chemistry"
    RADIOLOGY = "Radiology"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]

class ParameterType(StrEnum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEXT = "text"
    BOOLEAN = "boolean"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]