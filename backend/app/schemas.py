import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Todo ----------

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    done: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    done: Optional[bool] = None


class TodoOut(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------- Note ----------

class NoteBase(BaseModel):
    title: str
    content: str = ""


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NoteOut(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------- TrackerRow ----------

class TrackerRowBase(BaseModel):
    name: str
    category: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    date: Optional[datetime.datetime] = None
    notes: Optional[str] = None


class TrackerRowCreate(TrackerRowBase):
    pass


class TrackerRowUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    date: Optional[datetime.datetime] = None
    notes: Optional[str] = None


class TrackerRowOut(TrackerRowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
