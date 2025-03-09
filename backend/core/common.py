from django.db import models


class UserRole(models.TextChoices):
    ORGANIZATION_OWNER = "organization_owner", "Organization Owner"
    BRANCH_MANAGER = "branch_manager", "Branch Manager"
    WORKER = "worker", "Worker"


class RelationType(models.TextChoices):
    REQUEST_TO_JOIN = "request_to_join", "Request to Join"
    RELATION = "relation", "Relation"
    INVITATION_TO_USER = "invitation_to_user", "Invitation to User"
