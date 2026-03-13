# Background Remover API

Coin rasmlaridan backgroundni olib tashlash va 512x512 PNG formatda qaytarish.

## API Endpoints

| Method | URL          | Description              |
|--------|-------------|--------------------------|
| GET    | `/health`   | Server holatini tekshirish |
| POST   | `/remove-bg`| Background olib tashlash  |

### POST `/remove-bg`

**Request:** `multipart/form-data` — `file` field (jpg, png, webp, max 10MB)

**Response:** `image/png` — 512x512, tight-cropped, ≤500KB

```bash
curl -X POST https://your-domain.com/remove-bg \
  -F "file=@coin.jpg" \
  -o result.png
```

## Hostinger VPS ga deploy qilish

### 1. VPS ga ulanish

```bash
ssh root@YOUR_VPS_IP
```

### 2. Docker o'rnatish

```bash
curl -fsSL https://get.docker.com | sh
```

### 3. Loyihani yuklash

```bash
git clone https://github.com/YOUR_USERNAME/BackgroundRemover.git
cd BackgroundRemover
```

### 4. Ishga tushirish

```bash
docker compose up -d --build
```

Birinchi marta build ~2-3 daqiqa davom etadi (model yuklanadi).

### 5. Tekshirish

```bash
curl http://localhost:8000/health
```

### 6. Nginx reverse proxy (HTTPS)

```bash
apt install -y nginx certbot python3-certbot-nginx
```

`/etc/nginx/sites-available/backgroundremover` faylini yarating:

```nginx
server {
    server_name your-domain.com;
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/backgroundremover /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
certbot --nginx -d your-domain.com
```

### Yangilash

```bash
cd BackgroundRemover
git pull
docker compose up -d --build
```
