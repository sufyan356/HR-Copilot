from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from BACKEND.Models.model import User
from BACKEND.Database.get_db import get_db
from BACKEND.Schema.auth_schema import LoginRequest, StandardResponse
from BACKEND.Utils.auth_utils import verify_password, create_token


loginRouter = APIRouter()


@loginRouter.post("/login", response_model=StandardResponse)
async def login(
    req: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        # Find user by email
        user = (
            db.query(User)
            .filter(User.email == req.user_email)
            .first()
        )

        # User does not exist
        if not user:
            return StandardResponse(
                data=None,
                error="INVALID_CREDENTIALS",
                message="Invalid email or password",
                status=False
            )

        # Verify password
        if not verify_password(
            req.user_password,
            user.password
        ):
            return StandardResponse(
                data=None,
                error="INVALID_CREDENTIALS",
                message="Invalid email or password",
                status=False
            )

        # Generate JWT
        token = create_token(
            user.id,
            user.email
        )

        return StandardResponse(
            data={
                "id": user.id,
                "user_name": user.username,
                "user_email": user.email,
                "token": token
            },
            error=None,
            message="Login successful",
            status=True
        )

    except Exception as e:
        db.rollback()

        return StandardResponse(
            data=None,
            error=str(e),
            message="Login failed",
            status=False
        )