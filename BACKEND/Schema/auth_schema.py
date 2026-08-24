from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any

class SignUpRequest(BaseModel):
    user_name: str = Field(..., max_length=30)
    user_email: EmailStr
    user_password: str = Field(..., min_length=8, max_length=255)
    
class LoginRequest(BaseModel):
    user_email: EmailStr
    user_password: str
    

class StandardResponse(BaseModel):
    data: Optional[Any]
    error: Optional[str]
    message: str
    status: bool
