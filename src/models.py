import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, model_validator


def convert_datetime_to_gmt(dt: datetime) -> str:
    """
    Convert a datetime object to a string representation in GMT format.
    If the datetime object does not have a timezone, it is assumed to be in UTC.
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    """
    A custom base model that provides additional functionality.
    """

    model_config = ConfigDict(
        json_encoders={datetime: convert_datetime_to_gmt},
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def set_null_microseconds(cls, data: dict[str, Any] | bytes) -> dict[str, Any]:
        """
        Set the microseconds of datetime fields to 0 in the given data dictionary or bytes.
        """
        if isinstance(data, bytes):
            data = json.loads(data.decode("utf-8"))

        datetime_fields = {k: v.replace(microsecond=0) for k, v in data.items() if isinstance(v, datetime)}
        return {**data, **datetime_fields}

    def serializable_dict(self, **kwargs):
        """
        Return a dictionary that contains only serializable fields of the model.
        """
        default_dict = self.model_dump()

        return jsonable_encoder(default_dict)
