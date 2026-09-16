import json

from pydantic import ValidationError

from src.schema import AppResearch


def validate_json(
    raw_output: str
) -> tuple[bool, dict, list[str]]:

    errors = []

    # --------------------------------------------------------
    # JSON parsing
    # --------------------------------------------------------

    try:

        data = json.loads(
            raw_output
        )

    except json.JSONDecodeError as e:

        return (
            False,
            {},
            [
                f"Invalid JSON: {e}"
            ]
        )

    # --------------------------------------------------------
    # Pydantic schema validation
    # --------------------------------------------------------

    try:

        validated = AppResearch.model_validate(
            data
        )

        clean_data = validated.model_dump(
            mode="json"
        )

    except ValidationError as e:

        for error in e.errors():

            location = ".".join(
                str(x)
                for x in error["loc"]
            )

            errors.append(
                f"{location}: {error['msg']}"
            )

        return (
            False,
            data,
            errors
        )

    return (
        True,
        clean_data,
        []
    )