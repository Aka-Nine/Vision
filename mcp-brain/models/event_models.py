from pydantic import BaseModel
class EventLog(BaseModel):
    event_name: str
