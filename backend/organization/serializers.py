# backend\organization\serializers.py:

from rest_framework import serializers
from django.db import transaction
from .models import Organization, Branch, Relation
from core.common import UserRole, RelationType
from user.serializers import UserSerializer


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
    """
    Serializer for users requesting to join a branch
    """

    class Meta:
        model = Relation
        fields = ("uuid", "branch", "user_role")
        read_only_fields = ("uuid",)

    def create(self, validated_data):
        user = self.context["request"].user
        branch = validated_data["branch"]

        # Get the organization from the branch
        organization = branch.organization

        # Create a relation with relation_type = REQUEST_TO_JOIN
        relation = Relation.objects.create(
            user=user,
            branch=branch,
            organization=organization,
            user_role=validated_data.get("user_role", UserRole.WORKER),
            relation_type=RelationType.REQUEST_TO_JOIN,
        )

        return relation


class InvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for organization owners/branch managers to invite users
    """

    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Relation
        fields = ("uuid", "branch", "user_role", "email")
        read_only_fields = ("uuid",)

    def validate(self, attrs):
        # Check if the user exists
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            attrs["user"] = User.objects.get(email=attrs.pop("email"))
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "User with this email does not exist."}
            )

        return attrs

    def create(self, validated_data):
        user = validated_data.pop("user")
        branch = validated_data["branch"]
        organization = branch.organization

        # Create an invitation relation
        relation = Relation.objects.create(
            user=user,
            branch=branch,
            organization=organization,
            user_role=validated_data.get("user_role", UserRole.WORKER),
            relation_type=RelationType.INVITATION_TO_USER,
        )

        return relation


class RelationResponseSerializer(serializers.Serializer):
    """
    Serializer for responding to invitations or join requests
    """

    accept = serializers.BooleanField()

    def update(self, instance, validated_data):
        accept = validated_data.get("accept")

        if accept:
            # Convert to a full relation
            instance.relation_type = RelationType.RELATION
            instance.save()
            return instance
        else:
            # Delete the relation if rejected
            instance.delete()
            return None
