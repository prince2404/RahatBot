from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import typing

class ModelName(str, Enum):
    GPT4_O = "gpt-4o"
    GPT4_O_MINI = "gpt-4o-mini"

class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName.GPT4_O)

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName

class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime
    file_size: typing.Optional[int] = None # New field
    content_type: typing.Optional[str] = None # New field

class DeleteFileRequest(BaseModel):
    file_id: int

class DeleteFileResponse(BaseModel):
    message: str