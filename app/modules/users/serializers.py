from app.core.config import settings
from app.core.storage import create_signed_gcs_url
from app.models.user import User


def serialize_user(user: User) -> dict:
    image_url = None

    if user.image_url is not None:
        image_url = create_signed_gcs_url(
            blob_reference=user.image_url,
            expiration_minutes=settings.profile_image_signed_url_expire_minutes,
        )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "image_url": image_url,
    }
