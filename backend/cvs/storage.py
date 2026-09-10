import mimetypes
import os

from django.core.files.storage import FileSystemStorage
from django.core.files.storage.base import Storage

from vercel.blob import BlobClient


class CVFileStorage(Storage):
    """
    Storage backend for CV files.

    Local development:
        Uses Django's normal FileSystemStorage.

    Production on Vercel:
        Uses Vercel Blob with private access.

    The CV database field stores the Blob pathname.
    """

    def __init__(self):
        self.local_storage = FileSystemStorage()

    @property
    def use_vercel_blob(self):
        """
        Use Vercel Blob when deployed with Blob credentials.

        Vercel's Blob setup normally provides
        BLOB_READ_WRITE_TOKEN for the project.
        """
        return bool(
            os.getenv("BLOB_READ_WRITE_TOKEN")
        )

    def _save(self, name, content):
        """
        Save uploaded content either locally or
        to Vercel Blob.
        """

        if not self.use_vercel_blob:
            return self.local_storage._save(
                name,
                content,
            )

        name = name.replace("\\", "/")

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
            add_random_suffix=True,
            content_type=content_type,
        )

        return blob.pathname

    def exists(self, name):
        """
        Local filesystem collision handling.

        Vercel Blob uses a random suffix, so a new pathname
        is already unique.
        """

        if not self.use_vercel_blob:
            return self.local_storage.exists(name)

        return False

    def url(self, name):
        """
        Return the Blob URL for serialization.

        Note:
        Private Blob URLs require authenticated access.
        The URL is therefore not a public downloadable URL.
        """

        if not self.use_vercel_blob:
            return self.local_storage.url(name)

        store_id = os.getenv(
            "VERCEL_BLOB_STORE_ID",
            "",
        ).strip()

        if store_id:
            return (
                "https://"
                f"{store_id}.private.blob.vercel-storage.com/"
                f"{name.lstrip('/')}"
            )

        # Fallback: return the stored pathname.
        return name

    def path(self, name):
        """
        There is no persistent local filesystem path
        for Vercel Blob files.
        """

        if not self.use_vercel_blob:
            return self.local_storage.path(name)

        raise NotImplementedError(
            "Vercel Blob files do not have a local "
            "filesystem path."
        )

    def open(self, name, mode="rb"):
        """
        Local files can use normal Django open behavior.

        Production Blob reads should go through an
        authenticated download endpoint.
        """

        if not self.use_vercel_blob:
            return self.local_storage.open(
                name,
                mode,
            )

        raise NotImplementedError(
            "Vercel Blob files must be read through "
            "the authenticated Blob API."
        )

    def delete(self, name):
        """
        Keep normal local deletion behavior.

        Blob deletion can be added later through the
        Vercel Blob API when CV deletion is implemented.
        """

        if not self.use_vercel_blob:
            return self.local_storage.delete(name)

        return None