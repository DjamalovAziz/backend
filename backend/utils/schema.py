# backend\utils\schema.py:

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_basic_type
from rest_framework import serializers


class ImageFieldFix(OpenApiSerializerFieldExtension):
    target_class = serializers.ImageField

    def map_serializer_field(self, auto_schema, direction, field):
        return build_basic_type(str)
