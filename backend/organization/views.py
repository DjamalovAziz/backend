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
from core.common import UserRole, RelationType


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if the user is the owner of the object or has admin rights.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read permissions for all users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user created this object
        if hasattr(obj, "created_by") and obj.created_by == request.user:
            return True

        # For organizations, check if the user is the organization owner
        if isinstance(obj, Organization):
            return Relation.objects.filter(
                organization=obj,
                user=request.user,
                user_role=UserRole.ORGANIZATION_OWNER,
                relation_type=RelationType.RELATION,
            ).exists()

        # For branches, check if the user is the branch manager or organization owner
        if isinstance(obj, Branch):
            return Relation.objects.filter(
                Q(branch=obj, user_role=UserRole.BRANCH_MANAGER)
                | Q(
                    organization=obj.organization, user_role=UserRole.ORGANIZATION_OWNER
                ),
                user=request.user,
                relation_type=RelationType.RELATION,
            ).exists()

        return False


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_permissions(self):
        # Allow anonymous users for GET requests
        if self.action in ["list", "retrieve"] or self.request.method == "GET":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Save the organization with the current user as creator
        organization = serializer.save(created_by=self.request.user)

        # Create a default main branch for this organization
        default_branch = Branch.objects.create(
            name="main_branch", organization=organization, created_by=self.request.user
        )

        # Create a relation for the creator as organization owner
        Relation.objects.create(
            organization=organization,
            branch=default_branch,  # Указываем связь с созданным бранчем
            user=self.request.user,
            user_role=UserRole.ORGANIZATION_OWNER,
            relation_type=RelationType.RELATION,
        )

    @action(detail=True, methods=["get"])
    def branches(self, request, pk=None):
        """Get all branches for an organization"""
        organization = self.get_object()
        branches = Branch.objects.filter(organization=organization)
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)


@action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
def relations(self, request, pk=None):
    """
    Получить все связи для организации.
    Требует аутентификации и соответствующих прав доступа.
    """
    organization = self.get_object()

    # Проверка, имеет ли пользователь доступ к отношениям этой организации
    has_access = Relation.objects.filter(
        organization=organization,
        user=request.user,
        relation_type=RelationType.RELATION,
    ).exists()

    if not has_access:
        return Response(
            {"detail": "У вас нет прав для просмотра связей этой организации."},
            status=status.HTTP_403_FORBIDDEN,
        )

    relations = Relation.objects.filter(organization=organization)
    serializer = RelationSerializer(relations, many=True)
    return Response(serializer.data)


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "organization__name"]
    ordering_fields = ["name", "created_at"]

    def get_permissions(self):
        # Allow anonymous users for GET requests
        if self.action in ["list", "retrieve"] or self.request.method == "GET":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Save branch with current user as creator
        branch = serializer.save(created_by=self.request.user)

        # If the user is not already an organization owner, make them a branch manager
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
        """
        Получить все связи для филиала.
        Требует аутентификации и соответствующих прав доступа.
        """
        branch = self.get_object()

        # Проверка, имеет ли пользователь доступ к отношениям этого филиала
        has_access = Relation.objects.filter(
            Q(branch=branch)  # Связь с этим филиалом
            | Q(
                organization=branch.organization, user_role=UserRole.ORGANIZATION_OWNER
            ),  # Владелец организации
            user=request.user,
            relation_type=RelationType.RELATION,
        ).exists()

        if not has_access:
            return Response(
                {"detail": "У вас нет прав для просмотра связей этого филиала."},
                status=status.HTTP_403_FORBIDDEN,
            )

        relations = Relation.objects.filter(branch=branch)
        serializer = RelationSerializer(relations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def request_to_join(self, request, pk=None):
        """Allow a user to request joining a branch"""
        branch = self.get_object()

        # Check if the user already has a relation with this branch
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
                # If there's an invitation, accept it
                existing_relation.relation_type = RelationType.RELATION
                existing_relation.save()
                return Response(
                    {"detail": "You have accepted the invitation to join this branch."},
                    status=status.HTTP_200_OK,
                )

        # Create a new join request
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
        """Allow branch managers or organization owners to invite users"""
        branch = self.get_object()

        # Check if the current user has permission to invite others
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


class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__email", "branch__name", "organization__name"]
    ordering_fields = ["created_at", "user_role"]

    # def get_queryset(self):
    #     """Filter relations based on user role and access rights"""
    #     user = self.request.user

    #     # Return only relations that the user has permission to see
    #     return Relation.objects.filter(
    #         Q(user=user)  # Их собственные связи
    #         | Q(
    #             branch__in=Branch.objects.filter(
    #                 relations__user=user,
    #                 relations__user_role__in=[
    #                     UserRole.BRANCH_MANAGER,
    #                     UserRole.ORGANIZATION_OWNER,
    #                 ],
    #                 relations__relation_type=RelationType.RELATION,
    #             )
    #         )  # Филиалы, которыми они управляют
    #         | Q(
    #             organization__in=Organization.objects.filter(
    #                 relations__user=user,
    #                 relations__user_role=UserRole.ORGANIZATION_OWNER,
    #                 relations__relation_type=RelationType.RELATION,
    #             )
    #         )  # Организации, которыми они владеют
    #     )

    def get_queryset(self):
        """Filter relations based on user role and access rights"""
        # Проверяем, является ли это запросом генерации схемы Swagger
        if getattr(self, "swagger_fake_view", False):
            # Возвращаем пустой queryset для документации API
            return Relation.objects.none()

        user = self.request.user

        # Return only relations that the user has permission to see
        return Relation.objects.filter(
            Q(user=user)  # Их собственные связи
            | Q(
                branch__in=Branch.objects.filter(
                    relations__user=user,
                    relations__user_role__in=[
                        UserRole.BRANCH_MANAGER,
                        UserRole.ORGANIZATION_OWNER,
                    ],
                    relations__relation_type=RelationType.RELATION,
                )
            )  # Филиалы, которыми они управляют
            | Q(
                organization__in=Organization.objects.filter(
                    relations__user=user,
                    relations__user_role=UserRole.ORGANIZATION_OWNER,
                    relations__relation_type=RelationType.RELATION,
                )
            )  # Организации, которыми они владеют
        )

    def get_permissions(self):
        """
        Пользовательская обработка разрешений:
        - Все действия требуют аутентификации
        - Только пользователи с правами администратора могут обновлять/удалять связи
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Add validation when creating a relation:
        - Check if the user has rights to create relations for the branch
        - Check if the branch belongs to the organization
        """
        branch = serializer.validated_data.get("branch")
        organization = serializer.validated_data.get("organization")

        # Verify the branch belongs to the organization
        if branch.organization != organization:
            raise serializers.ValidationError(
                "Branch does not belong to the specified organization."
            )

        # Check if the user has admin rights for this branch/organization
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
        relations = Relation.objects.filter(
            user=request.user, relation_type=RelationType.RELATION
        )
        serializer = self.get_serializer(relations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_invitations(self, request):
        """Get all pending invitations for the current user"""
        invitations = Relation.objects.filter(
            user=request.user, relation_type=RelationType.INVITATION_TO_USER
        )
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pending_requests(self, request):
        """
        Get all pending join requests for branches/organizations
        where the current user is an admin
        """
        user = request.user

        # Get all branches where the user is a manager
        managed_branches = Branch.objects.filter(
            relations__user=user,
            relations__user_role__in=[
                UserRole.BRANCH_MANAGER,
                UserRole.ORGANIZATION_OWNER,
            ],
            relations__relation_type=RelationType.RELATION,
        )

        # Get all organizations where the user is an owner
        owned_organizations = Organization.objects.filter(
            relations__user=user,
            relations__user_role=UserRole.ORGANIZATION_OWNER,
            relations__relation_type=RelationType.RELATION,
        )

        # Get all pending requests for these branches and organizations
        pending_requests = Relation.objects.filter(
            Q(branch__in=managed_branches) | Q(organization__in=owned_organizations),
            relation_type=RelationType.REQUEST_TO_JOIN,
        )

        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def respond_to_invitation(self, request, pk=None):
        """
        Allow a user to accept or reject an invitation
        """
        relation = self.get_object()

        # Ensure this is the user's invitation
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
        """
        Allow a branch manager or organization owner to accept or reject a join request
        """
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
