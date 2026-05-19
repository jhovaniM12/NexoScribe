from sqlalchemy.orm import Session

from app.core.storage import upload_bytes_to_gcs
from app.models.user import User
from app.modules.auth.service import get_authenticated_user
from app.modules.users import repository


SUPPORTED_PROFILE_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
}

MAX_PROFILE_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


class UnsupportedProfileImageTypeError(Exception):
    pass


class ProfileImageTooLargeError(Exception):
    pass


def update_authenticated_user_profile(
    db: Session,
    *,
    access_token: str,
    name: str | None = None,
    image_bytes: bytes | None = None,
    image_content_type: str | None = None,
) -> User:
    user = get_authenticated_user(db, access_token)
    image_reference = None

    if image_bytes is not None:
        if image_content_type not in SUPPORTED_PROFILE_IMAGE_TYPES:
            raise UnsupportedProfileImageTypeError

        if len(image_bytes) > MAX_PROFILE_IMAGE_SIZE_BYTES:
            raise ProfileImageTooLargeError

        extension = SUPPORTED_PROFILE_IMAGE_TYPES[image_content_type]
        destination = f"users/{user.id}/profile-image.{extension}"
        upload_bytes_to_gcs(
            file_bytes=image_bytes,
            destination_blob_name=destination,
            content_type=image_content_type,
        )
        image_reference = destination

    updated_user = repository.update_user_profile(
        db,
        user=user,
        name=name,
        image_url=image_reference,
    )

    db.commit()
    db.refresh(updated_user)

    return updated_user
