from pydantic import BaseModel
class PipelineStatus(BaseModel):
    id: str
    status: str
