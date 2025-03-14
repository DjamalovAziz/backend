# backend\organization\views.py:

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers

#
from .models import Organization, Branch, Relation
from .serializers import (
    OrganizationSerializer,
    BranchSerializer,
    RelationSerializer,
    RequestToJoinSerializer,
    InvitationSerializer,
    RelationResponseSerializer,
)
from utils.enamurations import UserRole, RelationType
from utils.permissions import IsOwnerOrAdmin

# ~~~~~~~~~~~~~~~~~~~~ ORGANIZATION ~~~~~~~~~~~~~~~~~~~~


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related("created_by").all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"] or self.request.method == "GET":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        organization = serializer.save(created_by=self.request.user)

        default_branch = Branch.objects.create(
            name="main_branch", organization=organization, created_by=self.request.user
        )

        Relation.objects.create(
            organization=organization,
            branch=default_branch,
            user=self.request.user,
            user_role=UserRole.ORGANIZATION_OWNER,
            relation_type=RelationType.RELATION,
        )

    @action(detail=True, methods=["get"])
    def branches(self, request, pk=None):
        organization = self.get_object()
        branches = Branch.objects.select_related("organization", "created_by").filter(
            organization=organization
        )
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def relations(self, request, pk=None):
        organization = self.get_object()

        has_access = Relation.objects.filter(
            organization=organization,
            user=request.user,
            relation_type=RelationType.RELATION,
        ).exists()

        if not has_access:
            return Response(
                {"detail": "You have not permissions to view relations of this organization."},
                status=status.HTTP_403_FORBIDDEN,
            )

        relations = Relation.objects.filter(organization=organization)
        serializer = RelationSerializer(relations, many=True)
        return Response(serializer.data)


# ~~~~~~~~~~~~~~~~~~~~ BRANCH ~~~~~~~~~~~~~~~~~~~~


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.select_related("organization", "created_by").all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "organization__name"]
    ordering_fields = ["name", "created_at"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"] or self.request.method == "GET":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        branch = serializer.save(created_by=self.request.user)

        if not Relation.objects.filter(
            organization=branch.organization,
            user=self.request.user,
            user_role=UserRole.ORGANIZATION_OWNER,
            relation_type=RelationType.RELATION,
        ).exists():
            Relation.objects.create(
                organization=branch.organization,
                branch=branch,
                user=self.request.user,
                user_role=UserRole.BRANCH_MANAGER,
                relation_type=RelationType.RELATION,
            )

    @action(
        detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def relations(self, request, pk=None):
        branch = self.get_object()

        has_access = Relation.objects.filter(
            Q(branch=branch)
            | Q(
                organization=branch.organization, user_role=UserRole.ORGANIZATION_OWNER
            ),
            user=request.user,
            relation_type=RelationType.RELATION,
        ).exists()

        if not has_access:
            return Response(
                {"detail": "You have not permissions to view relations of this branch."},
                status=status.HTTP_403_FORBIDDEN,
            )

        relations = Relation.objects.select_related(
            "user", "organization", "branch"
        ).filter(organization=organization)
        serializer = RelationSerializer(relations, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def request_to_join(self, request, pk=None):
        branch = self.get_object()

        existing_relation = Relation.objects.filter(
            branch=branch, user=request.user
        ).first()
        if existing_relation:
            if existing_relation.relation_type == RelationType.RELATION:
                return Response(
                    {"detail": "You are already a member of this branch."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif existing_relation.relation_type == RelationType.REQUEST_TO_JOIN:
                return Response(
                    {"detail": "You have already requested to join this branch."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif existing_relation.relation_type == RelationType.INVITATION_TO_USER:
                existing_relation.relation_type = RelationType.RELATION
                existing_relation.save()
                return Response(
                    {"detail": "You have accepted the invitation to join this branch."},
                    status=status.HTTP_200_OK,
                )

        serializer = RequestToJoinSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(branch=branch)

        return Response(
            {"detail": "Your request to join has been submitted."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def invite_user(self, request, pk=None):
        branch = self.get_object()

        has_permission = Relation.objects.filter(
            Q(branch=branch, user_role=UserRole.BRANCH_MANAGER)
            | Q(
                organization=branch.organization, user_role=UserRole.ORGANIZATION_OWNER
            ),
            user=request.user,
            relation_type=RelationType.RELATION,
        ).exists()

        if not has_permission:
            return Response(
                {"detail": "You don't have permission to invite users to this branch."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = InvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(branch=branch)

        return Response(
            {"detail": "Invitation has been sent."}, status=status.HTTP_201_CREATED
        )


# ~~~~~~~~~~~~~~~~~~~~ RELATION ~~~~~~~~~~~~~~~~~~~~


class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.select_related("user", "organization", "branch").all()
    serializer_class = RelationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__email", "branch__name", "organization__name"]
    ordering_fields = ["created_at", "user_role"]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)

        if self.action == "destroy":
            user = request.user

            if obj.user == user:
                return True

            is_org_owner = Relation.objects.filter(
                organization=obj.organization,
                user=user,
                user_role=UserRole.ORGANIZATION_OWNER,
                relation_type=RelationType.RELATION,
            ).exists()

            is_branch_manager = False
            if (
                obj.user_role == UserRole.WORKER
            ): 
                is_branch_manager = Relation.objects.filter(
                    branch=obj.branch,
                    user=user,
                    user_role=UserRole.BRANCH_MANAGER,
                    relation_type=RelationType.RELATION,
                ).exists()

            if not (is_org_owner or is_branch_manager):
                raise permissions.PermissionDenied(
                    "You do not have permission to perform this action."
                )

    def get_queryset(self):
        user = self.request.user
        return Relation.objects.select_related("user", "organization", "branch").filter(
            Q(user=user)
            | Q(
                branch__in=Branch.objects.filter(
                    relations__user=user,
                    relations__user_role__in=[
                        UserRole.BRANCH_MANAGER,
                        UserRole.ORGANIZATION_OWNER,
                    ],
                    relations__relation_type=RelationType.RELATION,
                )
            )
            | Q(
                organization__in=Organization.objects.filter(
                    relations__user=user,
                    relations__user_role=UserRole.ORGANIZATION_OWNER,
                    relations__relation_type=RelationType.RELATION,
                )
            )
        )

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        branch = serializer.validated_data.get("branch")
        organization = serializer.validated_data.get("organization")

        if branch.organization != organization:
            raise serializers.ValidationError(
                "Branch does not belong to the specified organization."
            )

        has_permission = (
            organization.created_by == self.request.user
            or Relation.objects.filter(
                Q(organization=organization, user_role=UserRole.ORGANIZATION_OWNER)
                | Q(branch=branch, user_role=UserRole.BRANCH_MANAGER),
                user=self.request.user,
                relation_type=RelationType.RELATION,
            ).exists()
        )

        if not has_permission:
            raise permissions.PermissionDenied(
                "You don't have permission to create relations for this branch."
            )

        serializer.save()

    @action(detail=False, methods=["get"])
    def my_relations(self, request):
        """Get all relations for the current user"""
        relations = Relation.objects.select_related(
            "user", "organization", "branch"
        ).filter(user=request.user, relation_type=RelationType.RELATION)
        serializer = self.get_serializer(relations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_invitations(self, request):
        invitations = Relation.objects.select_related(
            "user", "organization", "branch"
        ).filter(user=request.user, relation_type=RelationType.INVITATION_TO_USER)
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pending_requests(self, request):
        user = request.user
        managed_branches = Branch.objects.filter(
            relations__user=user,
            relations__user_role__in=[
                UserRole.BRANCH_MANAGER,
                UserRole.ORGANIZATION_OWNER,
            ],
            relations__relation_type=RelationType.RELATION,
        )
        owned_organizations = Organization.objects.filter(
            relations__user=user,
            relations__user_role=UserRole.ORGANIZATION_OWNER,
            relations__relation_type=RelationType.RELATION,
        )
        pending_requests = Relation.objects.select_related(
            "user", "organization", "branch"
        ).filter(
            Q(branch__in=managed_branches) | Q(organization__in=owned_organizations),
            relation_type=RelationType.REQUEST_TO_JOIN,
        )
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def respond_to_invitation(self, request, pk=None):
        relation = self.get_object()

        if (
            relation.user != request.user
            or relation.relation_type != RelationType.INVITATION_TO_USER
        ):
            return Response(
                {"detail": "This is not a valid invitation for you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RelationResponseSerializer(relation, data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        if result:
            return Response(
                {"detail": "Invitation accepted."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invitation rejected."}, status=status.HTTP_200_OK
            )

    @action(detail=True, methods=["post"])
    def respond_to_request(self, request, pk=None):
        relation = self.get_object()

        # Ensure this is a join request
        if relation.relation_type != RelationType.REQUEST_TO_JOIN:
            return Response(
                {"detail": "This is not a join request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the current user has permission to respond
        has_permission = Relation.objects.filter(
            Q(branch=relation.branch, user_role=UserRole.BRANCH_MANAGER)
            | Q(
                organization=relation.organization,
                user_role=UserRole.ORGANIZATION_OWNER,
            ),
            user=request.user,
            relation_type=RelationType.RELATION,
        ).exists()

        if not has_permission:
            return Response(
                {"detail": "You don't have permission to respond to this request."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RelationResponseSerializer(relation, data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        if result:
            return Response({"detail": "Request accepted."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Request rejected."}, status=status.HTTP_200_OK)
