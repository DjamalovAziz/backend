# backend\utils\constants.py:

import uuid


class DeletedUser:
    UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")
    USERNAME = "deleted_account"
    EMAIL = "deleted@example.com"
    IS_ACTIVE = False
