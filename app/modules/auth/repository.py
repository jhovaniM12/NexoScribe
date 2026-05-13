from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.enums import WorkspaceMemberRole, WorkspaceMemberStatus


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def create_user(
    db: Session,
    *,
    name: str,
    email: str,
    password_hash: str,
) -> User:
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
    )

    db.add(user)
    db.flush()

    return user


def create_personal_workspace(
    db: Session,
    *,
    user: User,
) -> Workspace:
    workspace = Workspace(
        name=f"{user.name}'s Workspace",
        slug=f"user-{user.id}",
        owner_id=user.id,
    )

    db.add(workspace)
    db.flush()
    member = WorkspaceMember(
        user_id=user.id,
        workspace_id=workspace.id,
        role=WorkspaceMemberRole.owner,
        status=WorkspaceMemberStatus.active,
    )

    db.add(member)
    db.flush()

    return workspace
