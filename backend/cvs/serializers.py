from pathlib import Path

from rest_framework import serializers

from .models import CV


class CVFileField(serializers.FileField):
    """
    Handles CV uploads normally, but never calls storage.url()
    when serializing a private Vercel Blob file.
    """

    def to_representation(self, value):
        if not value:
            return None

        try:
            return value.name
        except Exception:
            return str(value)


class CVSerializer(serializers.ModelSerializer):
    file = CVFileField(required=True)

    class Meta:
        model = CV

        fields = [
            "id",
            "title",
            "file",
            "extracted_text",
            "parsed_data",
            "uploaded_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "extracted_text",
            "parsed_data",
            "uploaded_at",
            "updated_at",
        ]

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError(
                "A CV file is required."
            )

        extension = Path(value.name).suffix.lower()

        allowed_extensions = {
            ".pdf",
            ".docx",
        }

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only PDF and DOCX files are allowed."
            )

        max_size = 4 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "File size must not exceed 4 MB."
            )

        return value

    def to_representation(self, instance):
        """
        Explicitly serialize the CV object without allowing DRF's
        default FileField representation to call value.url.

        This is required because CV files are stored as private
        Vercel Blob objects.
        """

        data = {}

        for field_name, field in self.fields.items():

            # IMPORTANT:
            # Never let DRF serialize the private FileField itself.
            if field_name == "file":
                continue

            attribute = field.get_attribute(instance)

            if attribute is None:
                data[field_name] = None
            else:
                data[field_name] = field.to_representation(
                    attribute
                )

        # Return the stored pathname instead of storage.url()
        if instance.file:
            try:
                data["file"] = instance.file.name
            except Exception:
                data["file"] = None
        else:
            data["file"] = None

        return data