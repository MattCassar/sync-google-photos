from pydantic import BaseModel
from humps import camel  # type: ignore


class GoogleApiBaseModel(BaseModel):
    class Config:
        alias_generator = camel.case


class GoogleApiDate(GoogleApiBaseModel):
    year: int
    month: int
    day: int


class GoogleApiDateRange(GoogleApiBaseModel):
    start_date: GoogleApiDate
    end_date: GoogleApiDate

    class Config:
        alias_generator = camel.case
        use_enum_values = True
        arbitrary_types_allowed = True
