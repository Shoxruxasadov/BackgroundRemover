import io

from fastapi import HTTPException, UploadFile
from PIL import Image
from rembg import remove

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}


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


def remove_background(image_bytes: bytes) -> bytes:
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")

    try:
        output_bytes = remove(image_bytes)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process image.")

    image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
