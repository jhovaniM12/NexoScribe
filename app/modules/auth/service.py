from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, decode_token, create_password_reset_token
from app.models.user import User
from app.modules.auth import repository
from app.modules.auth.schemas import RegisterRequest, LoginRequest
from jose import JWTError
from uuid import UUID


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

class InvalidPasswordResetTokenError(Exception):
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
    try:
        user_id = UUID(validate_access_token(token))
    except ValueError:
        raise InvalidAccessTokenError

    user = repository.get_user_by_id(db, user_id)

    if user is None:
        raise AuthenticatedUserNotFoundError

    return user


def request_password_reset(db: Session, email: str) -> str | None:
    user = repository.get_user_by_email(db, email)

    if user is None:
        return None

    return create_password_reset_token(subject=str(user.id))


def validate_password_reset_token(token: str) -> str:
      try:
          payload = decode_token(token)
      except JWTError:
          raise InvalidPasswordResetTokenError

      if payload.get("type") != "password_reset":
          raise InvalidPasswordResetTokenError

      user_id = payload.get("sub")

      if user_id is None:
          raise InvalidPasswordResetTokenError

      return user_id


def reset_user_password(db: Session, token: str, password: str) -> None:
      try:
          user_id = validate_password_reset_token(token)
          user_uuid = UUID(user_id)
      except (InvalidPasswordResetTokenError, ValueError):
          raise InvalidPasswordResetTokenError

      user = repository.get_user_by_id(db, user_uuid)

      if user is None:
          raise InvalidPasswordResetTokenError

      repository.update_user_password(
          db,
          user=user,
          new_password_hash=hash_password(password),
      )

      db.commit()
