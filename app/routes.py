from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import Response

from app.utils import validate_image, remove_background, _session_ready

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "model_ready": _session_ready.is_set()}


@router.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    if not _session_ready.is_set():
        raise HTTPException(status_code=503, detail="Model is still loading, please try again in a moment.")

    validate_image(file)

    contents = await file.read()
    output = remove_background(contents)

    return Response(content=output, media_type="image/png")
