import re
from typing import Optional

from pydantic import BaseModel, model_validator


USER_EMAIL_PLACEHOLDERS = frozenset(
    {"username", "given_name", "family_name", "email"}
)
PLACEHOLDER_PATTERN = re.compile(r"{{\s*([^{}]+?)\s*}}")


class RegistrationEmailConfig(BaseModel):
    email_enabled: bool = False
    email_template: Optional[str] = None

    @model_validator(mode="after")
    def validate_template(self) -> "RegistrationEmailConfig":
        if self.email_enabled and not (self.email_template and self.email_template.strip()):
            raise ValueError("An HTML template is required when email is enabled")
        if self.email_template:
            unknown = set(PLACEHOLDER_PATTERN.findall(self.email_template)) - USER_EMAIL_PLACEHOLDERS
            if unknown:
                raise ValueError(f"Unknown email placeholders: {', '.join(sorted(unknown))}")
        return self
