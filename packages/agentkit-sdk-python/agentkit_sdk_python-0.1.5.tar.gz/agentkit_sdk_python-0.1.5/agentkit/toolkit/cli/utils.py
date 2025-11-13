from typing import Literal, get_args, get_origin

from InquirerPy import resolver
from pydantic import BaseModel


def prompt_base_model(model: type[BaseModel]) -> dict:
    prompts = []

    for field_name, model_field in model.model_fields.items():
        if get_origin(model_field.annotation) == Literal:
            prompts.append(
                {
                    "type": "list",
                    "name": field_name,
                    "default": model_field.default if model_field.default else "",
                    "message": model_field.description
                    if model_field.description
                    else field_name,
                    "choices": list(get_args(model_field.annotation)),
                }
            )
        elif model_field.annotation is bool:
            prompts.append(
                {
                    "type": "confirm",
                    "name": field_name,
                    "default": model_field.default if model_field.default else False,
                    "message": model_field.description
                    if model_field.description
                    else field_name,
                }
            )
        else:
            prompts.append(
                {
                    "type": "input",
                    "name": field_name,
                    "default": str(model_field.default) if model_field.default else "",
                    "message": model_field.description
                    if model_field.description
                    else field_name,
                }
            )

    responses = resolver.prompt(prompts)
    return responses
