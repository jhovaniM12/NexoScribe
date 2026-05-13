from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.modules.auth import repository
from app.modules.auth.schemas import RegisterRequest


class EmailAlreadyRegisteredError(Exception):
    pass


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