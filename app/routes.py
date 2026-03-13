from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import Response

from app.utils import validate_image, remove_background

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    validate_image(file)

    contents = await file.read()
    output = remove_background(contents)

    return Response(content=output, media_type="image/png")
