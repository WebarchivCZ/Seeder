from django.utils import timezone

from chunked_upload.models import ChunkedUpload
from chunked_upload.settings import EXPIRATION_DELTA


def cleanup_expired_chunked_uploads():
    """
    Delete expired chunked uploads (DB rows + temp files on disk).

    This is intended to run from daily cron and prevents abandoned partial
    uploads from consuming storage indefinitely.
    """
    expire_before = timezone.now() - EXPIRATION_DELTA
    stale_uploads = ChunkedUpload.objects.filter(
        created_on__lte=expire_before).order_by("created_on")

    removed = 0
    reclaimed_bytes = 0
    for upload in stale_uploads.iterator():
        reclaimed_bytes += upload.offset or 0
        upload.delete()
        removed += 1

    print(
        "Removed {} expired chunk uploads, reclaimed ~{} bytes".format(
            removed, reclaimed_bytes)
    )
