from typing import List, Union

from fastapi import Form, HTTPException, status
from pydantic import TypeAdapter, ValidationError

from app.models.additional_info import AdditionalInfoAnswer, AdditionalInfoSubmission


SUBMISSION_ADAPTER = TypeAdapter(AdditionalInfoSubmission)
ARRAY_ADAPTER = TypeAdapter(
    Union[List[AdditionalInfoSubmission], List[AdditionalInfoAnswer]]
)


def parse_additional_info(
    additional_info: List[str] = Form(
        [],
        description="One JSON answer array or repeated JSON objects with question, type and answer",
    ),
) -> List[AdditionalInfoAnswer]:
    try:
        if not additional_info:
            return []
        if len(additional_info) == 1 and additional_info[0].lstrip().startswith("["):
            values = ARRAY_ADAPTER.validate_json(additional_info[0])
            return [
                value.answer if isinstance(value, AdditionalInfoSubmission) else value
                for value in values
            ]
        submissions = [
            SUBMISSION_ADAPTER.validate_json(value) for value in additional_info
        ]
        return [submission.answer for submission in submissions]
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "additional_info must be one JSON answer array or repeated JSON "
                "objects with question, type (text, single, multiple) and answer; "
                "text/single answers must be strings and multiple answers arrays of strings"
            ),
        ) from error
