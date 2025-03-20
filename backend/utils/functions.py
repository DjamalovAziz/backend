# backend\utils\functions.py:

from utils.constants import DeletedUser
from user.models import User


def get_deleted_user_id():
    deleted_user, created = User.objects.get_or_create(
        uuid=DeletedUser.UUID,
        defaults={
            "username": DeletedUser.USERNAME,
            "email": DeletedUser.EMAIL,
            "is_active": DeletedUser.IS_ACTIVE,
        },
    )
    return deleted_user.uuid
