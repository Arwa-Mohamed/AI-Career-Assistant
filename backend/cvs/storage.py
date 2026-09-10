import mimetypes
import os

from django.core.files.storage import FileSystemStorage
from django.core.files.storage.base import Storage
from django.utils.deconstruct import deconstructible

from vercel.blob import BlobClient


@deconstructible
class CVFileStorage(Storage):
    """
    Hybrid storage for CV files.

    Local development:
        Django FileSystemStorage -> media/cvs/

    Production on Vercel:
        Vercel Blob -> private object storage.
    """

    def __init__(self):
        self.local_storage = FileSystemStorage()

    @property
    def use_vercel_blob(self):
        """
        Use Vercel Blob when the Blob token exists.
        Otherwise use normal Django local storage.
        """
        return bool(
            os.getenv(
                "BLOB_READ_WRITE_TOKEN"
            )
        )

    def _save(self, name, content):
        """
        Save the uploaded CV locally during development
        or to Vercel Blob in production.
        """

        if not self.use_vercel_blob:
            return self.local_storage._save(
                name,
                content,
            )

        name = name.replace(
            "\\",
            "/",
        )

        file_data = content.read()

        content_type = (
            getattr(
                content,
                "content_type",
                None,
            )
            or mimetypes.guess_type(name)[0]
            or "application/octet-stream"
        )

        client = BlobClient()

        blob = client.put(
            name,
            file_data,
            access="private",
            content_type=content_type,
            add_random_suffix=True,
        )

        return blob.pathname

    def exists(self, name):
        if not self.use_vercel_blob:
            return self.local_storage.exists(
                name
            )

        return False

    def url(self, name):
        if not self.use_vercel_blob:
            return self.local_storage.url(
                name
            )

        raise NotImplementedError(
            "Private Vercel Blob files must be "
            "served through an authenticated endpoint."
        )

    def path(self, name):
        if not self.use_vercel_blob:
            return self.local_storage.path(
                name
            )

        raise NotImplementedError(
            "Vercel Blob files do not have a "
            "persistent local filesystem path."
        )

    def open(self, name, mode="rb"):
        if not self.use_vercel_blob:
            return self.local_storage.open(
                name,
                mode,
            )

        raise NotImplementedError(
            "Private Vercel Blob files must be "
            "read through an authenticated endpoint."
        )

    def delete(self, name):
        if not self.use_vercel_blob:
            return self.local_storage.delete(
                name
            )

        return None