# Background Remover API

A lightweight FastAPI service that removes backgrounds from images using [rembg](https://github.com/danielgatis/rembg). Designed to be consumed by mobile or web clients (e.g. React Native).

---

## Project Structure

```
BackgroundRemover/
├── app/
│   ├── main.py       # FastAPI app + CORS middleware
│   ├── routes.py     # API endpoints
│   └── utils.py      # Image validation & background removal
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Local Setup

### Prerequisites

- Python 3.10+
- pip

### Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

---

## Docker Setup

### Build the image

```bash
docker build -t background-remover .
```

### Run the container

```bash
docker run -p 8000:8000 background-remover
```

---

## API Endpoints

### `GET /health`

Returns the health status of the service.

**Response**

```json
{ "status": "ok" }
```

---

### `POST /remove-bg`

Removes the background from an uploaded image.

**Request**

| Field  | Type   | Description                          |
|--------|--------|--------------------------------------|
| `file` | binary | Image file (`multipart/form-data`)   |

**Constraints**

- Maximum file size: **10 MB**
- Supported formats: `jpg`, `jpeg`, `png`, `webp`

**Response**

- Content-Type: `image/png`
- Body: PNG image with transparent background

**Error Responses**

| Status | Reason                          |
|--------|---------------------------------|
| `400`  | Invalid or corrupted image      |
| `413`  | File exceeds 10 MB limit        |
| `415`  | Unsupported image format        |
| `500`  | Internal processing error       |

---

## Testing with curl

### Health check

```bash
curl http://localhost:8000/health
```

### Remove background

```bash
curl -X POST http://localhost:8000/remove-bg \
  -F "file=@image.jpg" \
  --output result.png
```

The processed image will be saved as `result.png` with a transparent background.

---

## Interactive API Docs

FastAPI provides built-in documentation:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
