from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LinkBase(BaseModel):
    original_url: HttpUrl

class LinkCreate(LinkBase):
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    short_code: Optional[str] = None

class LinkStats(BaseModel):
    original_url: str
    short_code: str
    created_at: datetime
    clicks: int
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LinkResponse(LinkBase):
    short_code: str
    short_url: str

    class Config:
        from_attributes = True
