# backend\user\schema.py:

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_basic_type
from rest_framework import serializers


# Расширение для правильной обработки ImageField в схеме API
class ImageFieldFix(OpenApiSerializerFieldExtension):
    target_class = serializers.ImageField

    def map_serializer_field(self, auto_schema, direction, field):
        # Возвращаем поле как строку (URL) для документации
        return build_basic_type(str)
