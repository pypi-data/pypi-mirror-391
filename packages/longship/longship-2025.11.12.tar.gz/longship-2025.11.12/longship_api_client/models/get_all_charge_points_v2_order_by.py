from enum import Enum


class GetAllChargePointsV2OrderBy(str, Enum):
    MODEL = "model"
    NAME = "name"
    OFFLINESINCE = "offlinesince"
    OUNAME = "ouname"
    PRODUCT = "product"
    SERIALNUMBER = "serialnumber"

    def __str__(self) -> str:
        return str(self.value)
