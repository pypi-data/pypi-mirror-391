from pydantic import BaseModel


class CancellationMessage(BaseModel):
    task_id: str
    timestamp: float
