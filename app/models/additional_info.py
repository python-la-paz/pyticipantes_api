from typing import List, Literal, Union

from pydantic import BaseModel, Field, StrictStr, model_validator


AdditionalInfoAnswer = Union[StrictStr, List[StrictStr]]


class AdditionalInfoSubmission(BaseModel):
    question: StrictStr
    type: Literal["text", "multiple", "single"]
    answer: AdditionalInfoAnswer

    @model_validator(mode="after")
    def validate_answer_type(self) -> "AdditionalInfoSubmission":
        if self.type == "multiple":
            if not isinstance(self.answer, list):
                raise ValueError("Multiple-choice answers must be arrays of strings")
        elif not isinstance(self.answer, str):
            raise ValueError("Text and single-choice answers must be strings")
        return self


class AdditionalInfoQuestion(BaseModel):
    question: StrictStr
    type: Literal["text", "multiple", "single"] = "text"
    options: List[StrictStr] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def convert_legacy_question(cls, value: object) -> object:
        if isinstance(value, str):
            return {"question": value, "type": "text"}
        return value

    @model_validator(mode="after")
    def validate_question(self) -> "AdditionalInfoQuestion":
        if not self.question.strip():
            raise ValueError("Question must not be empty")
        if self.type == "text":
            if self.options:
                raise ValueError("Text questions cannot have options")
        elif not self.options or any(not option.strip() for option in self.options):
            raise ValueError("Choice questions require non-empty options")
        if len(set(self.options)) != len(self.options):
            raise ValueError("Question options must be unique")
        return self
