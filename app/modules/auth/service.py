from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, decode_token
from app.models.user import User
from app.modules.auth import repository
from app.modules.auth.schemas import RegisterRequest, LoginRequest
from jose import JWTError


class EmailAlreadyRegisteredError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class InvalidRefreshTokenError(Exception):
      pass

class InvalidAccessTokenError(Exception):
      pass

class AuthenticatedUserNotFoundError(Exception):
      pass

def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = repository.get_user_by_email(db, payload.email)

    if user is None or user.password_hash is None:
        raise InvalidCredentialsError

    if not verify_password(payload.password, user.password_hash):
        raise InvalidCredentialsError

    return user


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing_user = repository.get_user_by_email(db, payload.email)

    if existing_user is not None:
        raise EmailAlreadyRegisteredError

    user = repository.create_user(
        db,
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
      )

    repository.create_personal_workspace(db, user=user)

    db.commit()
    db.refresh(user)

    return user


def validate_refresh_token(token: str) -> str:
    try:
        payload = decode_token(token)
    except JWTError:
        raise InvalidRefreshTokenError

    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError

    user_id = payload.get("sub")

    if user_id is None:
        raise InvalidRefreshTokenError

    return user_id

def validate_access_token(token: str) -> str:
    try:
        payload = decode_token(token)
    except JWTError:
        raise InvalidAccessTokenError

    if payload.get("type") != "access":
        raise InvalidAccessTokenError

    user_id = payload.get("sub")

    if user_id is None:
        raise InvalidAccessTokenError

    return user_id


def get_authenticated_user(db: Session, token: str) -> User:
    user_id = validate_access_token(token)
    user = repository.get_user_by_id(db, user_id)

    if user is None:
        raise AuthenticatedUserNotFoundError

    return user