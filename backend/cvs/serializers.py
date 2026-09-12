from pathlib import Path

from rest_framework import serializers

from .models import CV


class CVFileField(serializers.FileField):
    """
    File field for CV uploads.

    Upload:
        Works normally with Django/DRF.

    Serialization:
        Returns only the stored file name/path.
        It NEVER calls storage.url(), which is important
        because production CV files are stored as private
        Vercel Blob objects.
    """

    def to_representation(self, value):
        if not value:
            return None

        # IMPORTANT:
        # Do NOT use value.url here.
        # Private Vercel Blob storage intentionally does not
        # expose a public URL.
        try:
            return value.name
        except Exception:
            return str(value)


class CVSerializer(serializers.ModelSerializer):
    file = CVFileField(
        required=True,
    )

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

        extension = (
            Path(value.name)
            .suffix
            .lower()
        )

        allowed_extensions = {
            ".pdf",
            ".docx",
        }

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only PDF and DOCX files are allowed."
            )

        # Keep uploads below Vercel's request-body limit.
        max_size = 4 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "File size must not exceed 4 MB."
            )

        return value