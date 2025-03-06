# backend\organization\serializers.py:

from rest_framework import serializers

#
from organization.models import Branch, Organization

# ~~~~~~~~~~~~~~~~~~~~ Organization ~~~~~~~~~~~~~~~~~~~~


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["uuid", "name"]


# ~~~~~~~~~~~~~~~~~~~~ Branch ~~~~~~~~~~~~~~~~~~~~


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["uuid", "name", "organization"]
