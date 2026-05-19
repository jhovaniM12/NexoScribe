from sqlalchemy.orm import Session

from app.models.user import User


def update_user_profile(
    db: Session,
    *,
    user: User,
    name: str | None = None,
    image_url: str | None = None,
) -> User:
    if name is not None:
        user.name = name

    if image_url is not None:
        user.image_url = image_url

    db.add(user)
    db.flush()

    return user

