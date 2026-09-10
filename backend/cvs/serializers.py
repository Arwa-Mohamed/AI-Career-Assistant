from pathlib import Path

from rest_framework import serializers

from .models import CV


class CVFileField(serializers.FileField):
    """
    File field that keeps upload behavior but does not call
    storage.url() when serializing a private Vercel Blob file.

    For private cloud storage, returning the stored pathname is safer
    than attempting to expose a public URL.
    """

    def to_representation(self, value):
        if not value:
            return None

        return value.name


class CVSerializer(serializers.ModelSerializer):
    file = CVFileField()

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

        # Vercel Functions have a 4.5 MB request-body
        # limit for server uploads, so keep CV files
        # safely below that threshold.
        max_size = 4 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "File size must not exceed 4 MB."
            )

        return value