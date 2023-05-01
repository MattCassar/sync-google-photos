from pydantic import BaseModel


def to_camel(snake_case: str) -> str:
    parts = snake_case.split("_")
    camel_case = parts[0] + "".join([part.capitalize() for part in parts[1:]])
    return camel_case


class GoogleApiBaseModel(BaseModel):
    class Config:
        alias_generator = to_camel
        use_enum_values = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True


class GoogleApiDate(GoogleApiBaseModel):
    year: int
    month: int
    day: int


class GoogleApiDateRange(GoogleApiBaseModel):
    start_date: GoogleApiDate
    end_date: GoogleApiDate
