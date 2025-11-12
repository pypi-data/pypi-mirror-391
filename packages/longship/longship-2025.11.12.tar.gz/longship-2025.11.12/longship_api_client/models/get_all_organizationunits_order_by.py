from enum import Enum


class GetAllOrganizationunitsOrderBy(str, Enum):
    CODE = "code"
    CREATED = "created"
    NAME = "name"
    UPDATED = "updated"

    def __str__(self) -> str:
        return str(self.value)
