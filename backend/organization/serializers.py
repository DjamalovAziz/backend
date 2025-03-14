# backend\organization\serializers.py:

from rest_framework import serializers
from django.db import transaction
from .models import Organization, Branch, Relation
from utils.enamurations import UserRole, RelationType
from user.serializers import UserSerializer

# ~~~~~~~~~~~~~~~~~~~~ ORGANIZATION ~~~~~~~~~~~~~~~~~~~~


class OrganizationSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Organization
        fields = (
            "uuid",
            "name",
            "description",
            "created_at",
            "updated_at",
            "created_by",
        )
        read_only_fields = ("uuid", "created_at", "updated_at", "created_by")


# ~~~~~~~~~~~~~~~~~~~~ BRANCH ~~~~~~~~~~~~~~~~~~~~


class BranchSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = Branch
        fields = (
            "uuid",
            "name",
            "description",
            "organization",
            "organization_name",
            "created_at",
            "updated_at",
            "created_by",
        )
        read_only_fields = (
            "uuid",
            "created_at",
            "updated_at",
            "created_by",
            "organization_name",
        )


# ~~~~~~~~~~~~~~~~~~~~ RELATION ~~~~~~~~~~~~~~~~~~~~


class RelationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Relation
        fields = (
            "uuid",
            "organization",
            "branch",
            "user",
            "user_role",
            "relation_type",
            "created_at",
            "updated_at",
            "user_details",
            "organization_name",
            "branch_name",
        )
        read_only_fields = (
            "uuid",
            "created_at",
            "updated_at",
            "user_details",
            "organization_name",
            "branch_name",
        )


class RequestToJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ("uuid", "user_role")
        read_only_fields = ("uuid",)

    def create(self, validated_data):
        user = self.context["request"].user
        branch = validated_data["branch"]

        organization = branch.organization

        relation = Relation.objects.create(
            user=user,
            branch=branch,
            organization=organization,
            user_role=validated_data.get("user_role", UserRole.WORKER),
            relation_type=RelationType.REQUEST_TO_JOIN,
        )

        return relation


class InvitationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    user_role = serializers.ChoiceField(
        choices=UserRole.choices, default=UserRole.WORKER
    )

    class Meta:
        model = Relation
        fields = ("uuid", "branch", "user_role", "email")
        read_only_fields = ("uuid",)

    def validate(self, attrs):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            attrs["user"] = User.objects.get(email=attrs.pop("email"))
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "User with this email does not exist."}
            )

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authenticated user required.")
        user = request.user

        branch = attrs.get("branch")
        if not branch or not hasattr(branch, "organization"):
            raise serializers.ValidationError({"branch": "Invalid branch."})

        requested_role = attrs.get("user_role")
        current_user_role = (
            Relation.objects.filter(
                user=user,
                organization=branch.organization,
                relation_type=RelationType.RELATION,
            )
            .values_list("user_role", flat=True)
            .first()
        )

        if not current_user_role:
            raise serializers.ValidationError(
                "You are not related to this organization."
            )

        if requested_role == UserRole.ORGANIZATION_OWNER:
            if current_user_role != UserRole.ORGANIZATION_OWNER:
                raise serializers.ValidationError(
                    {"user_role": "Only ORGANIZATION_OWNER can assign this role."}
                )
        elif current_user_role == UserRole.BRANCH_MANAGER and requested_role not in [
            UserRole.WORKER,
            UserRole.BRANCH_MANAGER,
        ]:
            raise serializers.ValidationError(
                {
                    "user_role": "BRANCH_MANAGER can only assign WORKER or BRANCH_MANAGER roles."
                }
            )

        return attrs

    def create(self, validated_data):
        user = validated_data.pop("user")
        branch = validated_data["branch"]
        organization = branch.organization

        relation = Relation.objects.create(
            user=user,
            branch=branch,
            organization=organization,
            user_role=validated_data["user_role"],
            relation_type=RelationType.INVITATION_TO_USER,
        )

        return relation


class RelationResponseSerializer(serializers.Serializer):
    accept = serializers.BooleanField()

    def update(self, instance, validated_data):
        accept = validated_data.get("accept")

        if accept:
            instance.relation_type = RelationType.RELATION
            instance.save()
            return instance
        else:
            instance.delete()
            return None
