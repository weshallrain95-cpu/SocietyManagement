"""Owner photos, videos and proof documents: checks, processing and short-lived signed links.

Files are private. A link is signed for one file and expires (OB_MEDIA_URL_TTL_S); whoever
builds the link has already decided the viewer may see it.
"""

import io
import time

from django.conf import settings
from django.core import signing
from django.core.files.base import ContentFile
from django.urls import reverse
from PIL import Image, ImageOps, UnidentifiedImageError

Image.MAX_IMAGE_PIXELS = 60_000_000  # ~60 MP phone photos; larger is rejected as a decompression bomb

VIDEO_TYPES = {"video/mp4": "mp4", "video/quicktime": "mov", "video/webm": "webm", "video/3gpp": "3gp"}
PHOTO_MAX_SIDE = 2048
THUMB_SIDE = 480


class MediaError(Exception):
    pass


def _jpeg(img: Image.Image, side: int) -> tuple[bytes, int, int]:
    im = img.copy()
    im.thumbnail((side, side))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85, optimize=True)  # re-encoding drops EXIF (GPS, phone model)
    return buf.getvalue(), im.width, im.height


def process_photo(upload) -> dict:
    """Validate a photo and return a clean JPEG plus thumbnail (EXIF stripped, upright)."""
    if upload.size > settings.OB_MAX_PHOTO_MB * 1024 * 1024:
        raise MediaError(f"Photos can be up to {settings.OB_MAX_PHOTO_MB} MB")
    try:
        img = Image.open(upload)
        img.verify()
        upload.seek(0)
        img = ImageOps.exif_transpose(Image.open(upload)).convert("RGB")
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError) as e:
        raise MediaError("That file is not a photo we can read (use JPG, PNG or HEIC saved as JPG)") from e
    full, w, h = _jpeg(img, PHOTO_MAX_SIDE)
    thumb, _, _ = _jpeg(img, THUMB_SIDE)
    return {
        "file": ContentFile(full, name="photo.jpg"),
        "thumb": ContentFile(thumb, name="thumb.jpg"),
        "content_type": "image/jpeg",
        "size_bytes": len(full),
        "width": w,
        "height": h,
    }


def _sniff_video(head: bytes) -> bool:
    return head[4:8] == b"ftyp" or head[:4] == b"\x1a\x45\xdf\xa3"  # MP4/MOV/3GP, or WebM


def process_video(upload) -> dict:
    ctype = (upload.content_type or "").split(";")[0].strip().lower()
    if ctype not in VIDEO_TYPES:
        raise MediaError("Videos must be MP4, MOV, WebM or 3GP")
    if upload.size > settings.OB_MAX_VIDEO_MB * 1024 * 1024:
        raise MediaError(f"Videos can be up to {settings.OB_MAX_VIDEO_MB} MB — trim it to a 1–2 minute walkthrough")
    head = upload.read(12)
    upload.seek(0)
    if not _sniff_video(head):
        raise MediaError("That file doesn't look like a video")
    return {"file": upload, "content_type": ctype, "size_bytes": upload.size}


def process_document(upload) -> dict:
    """Proof of ownership: a photo of the document, or a PDF."""
    head = upload.read(5)
    upload.seek(0)
    if head == b"%PDF-":
        if upload.size > 10 * 1024 * 1024:
            raise MediaError("PDFs can be up to 10 MB")
        return {"file": upload, "content_type": "application/pdf", "size_bytes": upload.size}
    return process_photo(upload)


def kind_for(upload) -> str:
    ctype = (upload.content_type or "").lower()
    return "video" if ctype.startswith("video/") else "photo"


def _sig(pk, variant: str, exp: int) -> str:
    return signing.Signer(salt="ob-media").signature(f"{pk}:{variant}:{exp}")


def signed_path(media, variant: str = "full") -> str:
    exp = int(time.time()) + settings.OB_MEDIA_URL_TTL_S
    exp -= exp % 300  # stable for 5 minutes so the app's image cache works
    return f"{reverse('media-file', args=[media.pk, variant])}?e={exp}&s={_sig(media.pk, variant, exp)}"


def check_signature(pk, variant: str, exp: str, sig: str) -> bool:
    if not exp.isdigit() or int(exp) < time.time():
        return False
    return signing.constant_time_compare(sig, _sig(pk, variant, int(exp)))


def media_json(media, request) -> dict:
    url = request.build_absolute_uri(signed_path(media))
    return {
        "id": str(media.pk),
        "kind": media.kind,
        "state": media.state,
        "uploaded_by": media.uploaded_by_org.name if media.uploaded_by_org_id else "Owner",
        "url": url,
        "thumb_url": request.build_absolute_uri(signed_path(media, "thumb")) if media.thumb else url,
        "content_type": media.content_type,
        "width": media.width,
        "height": media.height,
        "caption": media.caption,
        "created_at": media.created_at.isoformat(),
    }
