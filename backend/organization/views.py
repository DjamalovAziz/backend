# backend\organization\views.py:

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets

#
from organization.models import Branch, Organization
from organization.serializers import BranchSerializer, OrganizationSerializer


# ~~~~~~~~~~~~~~~~~~~~ Organization ~~~~~~~~~~~~~~~~~~~~
class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


# ~~~~~~~~~~~~~~~~~~~~ Branch ~~~~~~~~~~~~~~~~~~~~
class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
