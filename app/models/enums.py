from enum import Enum


class WorkspaceMemberRole(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    guest = "guest"


class WorkspaceMemberStatus(str, Enum):
    active = "active"
    invited = "invited"
    removed = "removed"
