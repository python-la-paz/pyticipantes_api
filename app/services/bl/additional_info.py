from typing import List, Optional, Tuple

from app.models.additional_info import AdditionalInfoAnswer, AdditionalInfoQuestion
from app.models.result import StatusCode


def validate_additional_info(
    questions: Optional[List[AdditionalInfoQuestion]],
    answers: List[AdditionalInfoAnswer],
) -> Optional[Tuple[str, StatusCode]]:
    questions = questions or []
    if questions and not answers:
        return "Additional info required", StatusCode.ADDITIONAL_INFO_REQUIRED
    if len(answers) != len(questions):
        return "Responses are not complete", StatusCode.RESPONSES_NOT_COMPLETE
    for question, answer in zip(questions, answers):
        if question.type == "multiple":
            valid = (
                isinstance(answer, list)
                and bool(answer)
                and all(isinstance(option, str) for option in answer)
                and len(set(answer)) == len(answer)
                and all(option in question.options for option in answer)
            )
        else:
            valid = isinstance(answer, str) and bool(answer.strip())
            if question.type == "single":
                valid = valid and answer in question.options
        if not valid:
            return (
                "Response does not match the question type or available options",
                StatusCode.RESPONSES_NOT_COMPLETE,
            )
    return None
