"""
ByteDocs Django - Schema Extractor
Extract schema information from DRF serializers, Django models, and Pydantic models
"""

import inspect
from typing import Any, Dict, List, Optional, get_type_hints, Union
from dataclasses import asdict, is_dataclass

from ..core.types import Schema, Parameter, ParameterLocation, RequestBody, ResponseDef


class SchemaExtractor:
    """Extract schemas from various Django model types"""

    @staticmethod
    def extract_from_serializer(serializer_class) -> Schema:
        """Extract schema from DRF serializer

        Args:
            serializer_class: DRF Serializer class

        Returns:
            Schema object
        """
        try:
            from rest_framework import serializers
        except ImportError:
            return Schema(type="object")

        if not inspect.isclass(serializer_class) or not issubclass(serializer_class, serializers.Serializer):
            return Schema(type="object")

        # Create serializer instance
        try:
            serializer = serializer_class()
        except Exception:
            # If instantiation fails, return basic schema
            return Schema(type="object")

        properties = {}
        required = []

        # Extract fields from serializer
        for field_name, field in serializer.fields.items():
            # Get field schema
            field_schema = SchemaExtractor._extract_field_schema(field)
            properties[field_name] = field_schema

            # Check if required
            if field.required:
                required.append(field_name)

        return Schema(
            type="object",
            properties=properties,
            required=required if required else None,
        )

    @staticmethod
    def _extract_field_schema(field) -> Schema:
        """Extract schema from DRF field

        Args:
            field: DRF field instance

        Returns:
            Schema object
        """
        try:
            from rest_framework import serializers
        except ImportError:
            return Schema(type="string")

        # Map field types to OpenAPI types
        type_mapping = {
            serializers.IntegerField: ("integer", "int32"),
            serializers.FloatField: ("number", "float"),
            serializers.DecimalField: ("number", "double"),
            serializers.BooleanField: ("boolean", None),
            serializers.CharField: ("string", None),
            serializers.EmailField: ("string", "email"),
            serializers.URLField: ("string", "uri"),
            serializers.UUIDField: ("string", "uuid"),
            serializers.DateField: ("string", "date"),
            serializers.DateTimeField: ("string", "date-time"),
            serializers.TimeField: ("string", "time"),
            serializers.JSONField: ("object", None),
        }

        # Get base type
        field_type = type(field)
        openapi_type, openapi_format = type_mapping.get(field_type, ("string", None))

        schema = Schema(
            type=openapi_type,
            format=openapi_format,
            description=field.help_text if hasattr(field, 'help_text') else None,
            default=field.default if hasattr(field, 'default') and field.default is not serializers.empty else None,
        )

        # Handle list fields
        if isinstance(field, serializers.ListField):
            if hasattr(field, 'child'):
                schema = Schema(
                    type="array",
                    items=SchemaExtractor._extract_field_schema(field.child),
                )

        # Handle nested serializers
        elif isinstance(field, serializers.Serializer):
            schema = SchemaExtractor.extract_from_serializer(field.__class__)

        # Handle choice fields
        elif isinstance(field, serializers.ChoiceField):
            choices = list(field.choices.keys()) if hasattr(field, 'choices') else None
            schema.enum = choices

        # Handle min/max validators
        if hasattr(field, 'min_value'):
            schema.minimum = field.min_value
        if hasattr(field, 'max_value'):
            schema.maximum = field.max_value

        # Handle min/max length validators
        if hasattr(field, 'min_length'):
            schema.min_length = field.min_length
        if hasattr(field, 'max_length'):
            schema.max_length = field.max_length

        return schema

    @staticmethod
    def extract_from_model(model_class) -> Schema:
        """Extract schema from Django model

        Args:
            model_class: Django model class

        Returns:
            Schema object
        """
        try:
            from django.db import models
        except ImportError:
            return Schema(type="object")

        if not inspect.isclass(model_class) or not issubclass(model_class, models.Model):
            return Schema(type="object")

        properties = {}
        required = []

        # Extract fields from model
        for field in model_class._meta.get_fields():
            if hasattr(field, 'name'):
                field_name = field.name
                field_schema = SchemaExtractor._extract_model_field_schema(field)
                properties[field_name] = field_schema

                # Check if required
                if hasattr(field, 'null') and not field.null and hasattr(field, 'blank') and not field.blank:
                    required.append(field_name)

        return Schema(
            type="object",
            properties=properties,
            required=required if required else None,
        )

    @staticmethod
    def _extract_model_field_schema(field) -> Schema:
        """Extract schema from Django model field

        Args:
            field: Django model field instance

        Returns:
            Schema object
        """
        try:
            from django.db import models
        except ImportError:
            return Schema(type="string")

        # Map field types to OpenAPI types
        type_mapping = {
            models.IntegerField: ("integer", "int32"),
            models.BigIntegerField: ("integer", "int64"),
            models.SmallIntegerField: ("integer", "int32"),
            models.FloatField: ("number", "float"),
            models.DecimalField: ("number", "double"),
            models.BooleanField: ("boolean", None),
            models.CharField: ("string", None),
            models.TextField: ("string", None),
            models.EmailField: ("string", "email"),
            models.URLField: ("string", "uri"),
            models.UUIDField: ("string", "uuid"),
            models.DateField: ("string", "date"),
            models.DateTimeField: ("string", "date-time"),
            models.TimeField: ("string", "time"),
            models.JSONField: ("object", None),
        }

        # Get base type
        field_type = type(field)
        openapi_type, openapi_format = type_mapping.get(field_type, ("string", None))

        schema = Schema(
            type=openapi_type,
            format=openapi_format,
            description=field.help_text if hasattr(field, 'help_text') else None,
            default=field.default if hasattr(field, 'default') and field.default is not models.NOT_PROVIDED else None,
        )

        # Handle max length
        if hasattr(field, 'max_length') and field.max_length:
            schema.max_length = field.max_length

        return schema

    @staticmethod
    def extract_from_pydantic(model_class) -> Schema:
        """Extract schema from Pydantic model (for django-ninja)

        Args:
            model_class: Pydantic model class

        Returns:
            Schema object
        """
        try:
            from pydantic import BaseModel
        except ImportError:
            return Schema(type="object")

        if not inspect.isclass(model_class) or not issubclass(model_class, BaseModel):
            return Schema(type="object")

        # Get model schema from Pydantic
        try:
            pydantic_schema = model_class.model_json_schema()
            return SchemaExtractor._convert_pydantic_schema(pydantic_schema)
        except Exception:
            return Schema(type="object")

    @staticmethod
    def _convert_pydantic_schema(pydantic_schema: Dict[str, Any]) -> Schema:
        """Convert Pydantic JSON schema to our Schema format

        Args:
            pydantic_schema: Pydantic JSON schema dict

        Returns:
            Schema object
        """
        schema_type = pydantic_schema.get("type", "object")

        # Handle object type
        if schema_type == "object":
            properties = {}
            if "properties" in pydantic_schema:
                for prop_name, prop_schema in pydantic_schema["properties"].items():
                    properties[prop_name] = SchemaExtractor._convert_pydantic_schema(prop_schema)

            return Schema(
                type="object",
                properties=properties if properties else None,
                required=pydantic_schema.get("required"),
                description=pydantic_schema.get("description"),
            )

        # Handle array type
        elif schema_type == "array":
            items = None
            if "items" in pydantic_schema:
                items = SchemaExtractor._convert_pydantic_schema(pydantic_schema["items"])

            return Schema(
                type="array",
                items=items,
                description=pydantic_schema.get("description"),
            )

        # Handle primitive types
        else:
            return Schema(
                type=schema_type,
                format=pydantic_schema.get("format"),
                description=pydantic_schema.get("description"),
                enum=pydantic_schema.get("enum"),
                default=pydantic_schema.get("default"),
                minimum=pydantic_schema.get("minimum"),
                maximum=pydantic_schema.get("maximum"),
                min_length=pydantic_schema.get("minLength"),
                max_length=pydantic_schema.get("maxLength"),
                pattern=pydantic_schema.get("pattern"),
            )

    @staticmethod
    def extract_from_type(type_hint: Any) -> Schema:
        """Extract schema from Python type hint

        Args:
            type_hint: Python type hint

        Returns:
            Schema object
        """
        # Handle None
        if type_hint is None or type_hint is type(None):
            return Schema(type="null")

        # Handle basic types
        if type_hint == int:
            return Schema(type="integer", format="int32")
        elif type_hint == float:
            return Schema(type="number", format="float")
        elif type_hint == bool:
            return Schema(type="boolean")
        elif type_hint == str:
            return Schema(type="string")
        elif type_hint == dict:
            return Schema(type="object")
        elif type_hint == list:
            return Schema(type="array", items=Schema(type="string"))

        # Handle Optional, Union, List, Dict
        origin = getattr(type_hint, '__origin__', None)
        if origin is Union:
            # Handle Optional (Union with None)
            args = getattr(type_hint, '__args__', ())
            if len(args) == 2 and type(None) in args:
                # Optional type
                non_none_type = args[0] if args[1] is type(None) else args[1]
                schema = SchemaExtractor.extract_from_type(non_none_type)
                schema.nullable = True
                return schema

        elif origin is list:
            args = getattr(type_hint, '__args__', ())
            item_type = args[0] if args else str
            return Schema(
                type="array",
                items=SchemaExtractor.extract_from_type(item_type),
            )

        elif origin is dict:
            return Schema(type="object")

        # Try to extract from class
        if inspect.isclass(type_hint):
            # Try Pydantic first
            try:
                from pydantic import BaseModel
                if issubclass(type_hint, BaseModel):
                    return SchemaExtractor.extract_from_pydantic(type_hint)
            except ImportError:
                pass

            # Try DRF serializer
            try:
                from rest_framework import serializers
                if issubclass(type_hint, serializers.Serializer):
                    return SchemaExtractor.extract_from_serializer(type_hint)
            except ImportError:
                pass

            # Try Django model
            try:
                from django.db import models
                if issubclass(type_hint, models.Model):
                    return SchemaExtractor.extract_from_model(type_hint)
            except ImportError:
                pass

            # Try dataclass
            if is_dataclass(type_hint):
                return SchemaExtractor.extract_from_dataclass(type_hint)

        # Default to string
        return Schema(type="string")

    @staticmethod
    def extract_from_dataclass(dataclass_type: type) -> Schema:
        """Extract schema from dataclass

        Args:
            dataclass_type: Dataclass type

        Returns:
            Schema object
        """
        if not is_dataclass(dataclass_type):
            return Schema(type="object")

        properties = {}
        required = []

        # Get type hints
        hints = get_type_hints(dataclass_type)

        for field_name, field_type in hints.items():
            field_schema = SchemaExtractor.extract_from_type(field_type)
            properties[field_name] = field_schema

            # Check if field has no default (required)
            for field_info in dataclass_type.__dataclass_fields__.values():
                if field_info.name == field_name:
                    if field_info.default is dataclass_type.__dataclass_fields__[field_name].default_factory is None:
                        required.append(field_name)

        return Schema(
            type="object",
            properties=properties,
            required=required if required else None,
        )


def extract_schema(obj: Any) -> Schema:
    """Extract schema from any supported object type

    Args:
        obj: Object to extract schema from (serializer, model, type, etc.)

    Returns:
        Schema object
    """
    if obj is None:
        return Schema(type="object")

    # Try DRF serializer
    try:
        from rest_framework import serializers
        if inspect.isclass(obj) and issubclass(obj, serializers.Serializer):
            return SchemaExtractor.extract_from_serializer(obj)
    except ImportError:
        pass

    # Try Pydantic model
    try:
        from pydantic import BaseModel
        if inspect.isclass(obj) and issubclass(obj, BaseModel):
            return SchemaExtractor.extract_from_pydantic(obj)
    except ImportError:
        pass

    # Try Django model
    try:
        from django.db import models
        if inspect.isclass(obj) and issubclass(obj, models.Model):
            return SchemaExtractor.extract_from_model(obj)
    except ImportError:
        pass

    # Try dataclass
    if is_dataclass(obj):
        return SchemaExtractor.extract_from_dataclass(obj)

    # Try type hint
    return SchemaExtractor.extract_from_type(obj)
