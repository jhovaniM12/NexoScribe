from fastapi import APIRouter, Cookie, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.schemas import AuthUserResponse
from app.modules.auth.service import (
    AuthenticatedUserNotFoundError,
    InvalidAccessTokenError,
)
from app.modules.users.serializers import serialize_user
from app.modules.users.service import (
    ProfileImageTooLargeError,
    UnsupportedProfileImageTypeError,
    update_authenticated_user_profile,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch(
    "/me",
    response_model=AuthUserResponse,
    status_code=status.HTTP_200_OK,
)
def update_me(
    name: str | None = Form(default=None, min_length=2, max_length=100),
    image: UploadFile | None = File(default=None),
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> dict:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing",
        )

    image_bytes = image.file.read() if image is not None else None
    image_content_type = image.content_type if image is not None else None

    try:
        user = update_authenticated_user_profile(
            db,
            access_token=access_token,
            name=name,
            image_bytes=image_bytes,
            image_content_type=image_content_type,
        )
    except (InvalidAccessTokenError, AuthenticatedUserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )
    except UnsupportedProfileImageTypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image type. Use JPEG, PNG, or WebP.",
        )
    except ProfileImageTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Profile image must be 5MB or smaller.",
        )

    return {"success": True, "data": {"user": serialize_user(user)}}
