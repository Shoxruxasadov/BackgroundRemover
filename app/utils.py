import io
import threading

from fastapi import HTTPException, UploadFile
from PIL import Image

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

_session = None
_session_lock = threading.Lock()
_session_ready = threading.Event()


def _load_session():
    global _session
    from rembg import new_session
    session = new_session("u2net")
    with _session_lock:
        _session = session
    _session_ready.set()


threading.Thread(target=_load_session, daemon=True).start()


def get_session():
    return _session


def validate_image(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: jpg, jpeg, png, webp.",
        )

    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum allowed size is 10 MB.",
        )


OUTPUT_SIZE = 512
MAX_OUTPUT_BYTES = 500 * 1024  # 500 KB


def _tight_crop(image: Image.Image) -> Image.Image:
    """Crop to the bounding box of non-transparent pixels, then fit into a square."""
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return image
    cropped = image.crop(bbox)

    w, h = cropped.size
    side = max(w, h)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(cropped, ((side - w) // 2, (side - h) // 2))
    return square


def _compress_png(image: Image.Image, max_bytes: int) -> bytes:
    """Save as PNG, reducing colors if needed to stay under max_bytes."""
    buf = io.BytesIO()
    image.save(buf, format="PNG", optimize=True)
    if buf.tell() <= max_bytes:
        return buf.getvalue()

    quantized = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=0)
    quantized = quantized.convert("RGBA")
    buf = io.BytesIO()
    quantized.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def remove_background(image_bytes: bytes) -> bytes:
    from rembg import remove

    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")

    try:
        output_bytes = remove(image_bytes, session=get_session())
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process image.")

    image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
    image = _tight_crop(image)
    image = image.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)

    return _compress_png(image, MAX_OUTPUT_BYTES)
