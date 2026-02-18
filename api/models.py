from typing import Optional, Literal

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel


class PaginationQueryParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: Literal["id", "name", "email"] = "id"


class UserProfileBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(unique=True)
    age: Optional[int] = Field(default=None, gt=0, lt=130)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfile(UserProfileBase, table=True):
    __tablename__ = "user_profiles"

    id: int | None = Field(primary_key=True)


class UserProfilePatch(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(default=None, gt=0, lt=130)


class UserProfileList(SQLModel):
    users: list[UserProfile]
    offset: int
    limit: int
    total: int


def create_all(engine):
    SQLModel.metadata.create_all(engine)