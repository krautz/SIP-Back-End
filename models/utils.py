from typing import TypeVar

Model = TypeVar("Model")


def convert_list_to_model(model: Model, data_list: list) -> list[Model]:
    return [model.model_validate(data) for data in data_list]


def convert_model_to_list(data_list: list[Model]) -> list[dict]:
    return [data.model_dump() for data in data_list]
