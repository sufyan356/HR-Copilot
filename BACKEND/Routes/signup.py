from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from BACKEND.Models.model import User
from BACKEND.Database.get_db import get_db
from BACKEND.Schema.auth_schema import SignUpRequest, StandardResponse
from BACKEND.Utils.auth_utils import hash_password,create_token,verify_token

signupRouter = APIRouter()


@signupRouter.post("/signup", response_model=StandardResponse)
async def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == req.user_email).first()

        if existing_user:
            return StandardResponse(
                data=None,
                error="EMAIL_ALREADY_EXISTS",
                message="User with this email already exists",
                status=False
            )

        new_user = User(
            username=req.user_name,
            email=req.user_email,
            password=hash_password(req.user_password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        token = create_token(new_user.id, new_user.email)

        return StandardResponse(
            data={
                "id":new_user.id,
                "user_name":new_user.username,
                "user_email":new_user.email,
                "token":token
            },
            error=None,
            message="User registered successfully",
            status=True
        )

    except Exception as e:
        return StandardResponse(
            data=None,
            error=str(e),
            message="Signup failed",
            status=False
        )
