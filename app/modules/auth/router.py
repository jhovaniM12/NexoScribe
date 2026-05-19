from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from sqlalchemy.orm import Session
from app.shared.responses import SuccessResponse
from app.core.email import send_password_reset_email
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.modules.auth.schemas import (
    AuthUserResponse,
    LoginRequest,
    RegisterRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest
)
from app.modules.auth.service import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidAccessTokenError,
    AuthenticatedUserNotFoundError,
    authenticate_user,
    get_authenticated_user,
    register_user,
    validate_refresh_token,
    InvalidPasswordResetTokenError,
    request_password_reset,
    reset_user_password
)
from app.modules.users.serializers import serialize_user
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    try:
        user = register_user(db, payload)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    return {"success": True, "data": {"user": user}}


@router.post(
    "/login",
    response_model=AuthUserResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    try:
        user = authenticate_user(db, payload)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/",
    )

    return SuccessResponse(success=True, data={"user": user})


@router.post(
    "/refresh",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
) -> dict:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    try:
        user_id = validate_refresh_token(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(subject=user_id)
    new_refresh_token = create_refresh_token(subject=user_id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/",
    )

    return SuccessResponse(success=True)


@router.get(
    "/me",
    response_model=AuthUserResponse,
    status_code=status.HTTP_200_OK,
)
def get_me(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> dict:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing",
        )

    try:
        user = get_authenticated_user(db, access_token)
    except InvalidAccessTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )
    except AuthenticatedUserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found",
        )

    return {"success": True, "data": {"user": serialize_user(user)}}


@router.post(
    "/logout",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
def logout(response: Response) -> dict:
    response.delete_cookie(
        key="access_token",
          path="/",
          samesite="lax",
          secure=settings.cookie_secure,
          httponly=True
        )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="lax",
        secure=settings.cookie_secure,
        httponly=True
    )
    return SuccessResponse(success=True)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
    token = request_password_reset(db, payload.email)

    if token is not None and settings.debug:
        send_password_reset_email(
            to_email=payload.email,
            reset_token=token
          )
        print(f"Password reset token for {payload.email}: {token}")
    return ForgotPasswordResponse(
        success=True,
        message="If an account with that email exists, a password reset link has been sent.",
    )
    

@router.post(
    "/reset-password",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
      try:
         reset_user_password(db, payload.token, payload.password)
      except InvalidPasswordResetTokenError:
          raise HTTPException(
              status_code=status.HTTP_400_BAD_REQUEST,
              detail="Invalid or expired password reset token",
          )
      return SuccessResponse(success=True)
