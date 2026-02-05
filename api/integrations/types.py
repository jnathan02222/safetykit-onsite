from pydantic import BaseModel
from datetime import datetime


class ExampleOut(BaseModel):
    id: int
    text: str


class PolicyViolationOut(BaseModel):
    id: int
    url: str
    title: str
    is_adderall_sold: bool
    appears_licensed_pharmacy: bool
    uses_visa: bool
    explanation: str
    screenshot_path: str
    screenshots: list[str]  # List of base64 encoded images
    analyzed_at: datetime
