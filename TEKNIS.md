# Dokumentasi Teknis - AI Customer Service Pegadaian

## Daftar Isi

1. [Arsitektur Sistem](#arsitektur-sistem)
2. [Backend (FastAPI)](#backend-fastapi)
3. [Frontend (React + Vite)](#frontend-react--vite)
4. [Database Schema](#database-schema)
5. [API Documentation](#api-documentation)
6. [Deployment](#deployment)

---

## Arsitektur Sistem

### Tech Stack

**Backend:**
- FastAPI 0.115.12 (Python web framework)
- SQLAlchemy 2.0.43 (ORM)
- PostgreSQL 15 (Database)
- Uvicorn (ASGI server)
- Yagmail (Email service)
- APScheduler (Background tasks)

**Frontend:**
- React 19.0.0
- TypeScript
- Vite 6.0.11 (Build tool)
- Tailwind CSS 3.4.17 (Styling)
- Recharts 2.15.0 (Data visualization)
- Axios 1.7.9 (HTTP client)

**Infrastructure:**
- Docker & Docker Compose
- Ngrok (Tunneling)
- n8n (Workflow automation)
- Ollama (LLM engine)
- Qdrant (Vector database)

### Deployment Model

Aplikasi ini menggunakan arsitektur **static file serving**, di mana:
1. Frontend di-build menjadi file statis (HTML, CSS, JS)
2. Backend FastAPI melayani API sekaligus static files
3. Semua service berjalan dalam Docker containers

---

## Backend (FastAPI)

### Struktur Direktori

```
utils/
├── app/
│   ├── main.py              # Entry point aplikasi
│   ├── router.py            # Dashboard API routes
│   ├── scheduler.py         # Background cleanup task
│   ├── models/
│   │   └── db_models.py     # SQLAlchemy models
│   └── service/
│       ├── database.py      # Database operations
│       ├── email_builder.py # Email service
│       └── scraper.py       # Web scraping (legacy)
├── static/                  # Built frontend files
├── requirements.txt
└── .env                     # Environment variables
```

### Core Components

#### 1. main.py

Entry point aplikasi yang mengkonfigurasi:
- CORS middleware untuk cross-origin requests
- Static file serving dari `/` endpoint
- Router inclusion untuk `/dashboard` prefix
- Background scheduler initialization

**Key Functions:**
- `startup_event()`: Inisialisasi database tables
- `start_scheduler()`: Memulai background cleanup task

**Endpoints:**
- `POST /api/scrape`: Web scraping endpoint (legacy)
- `POST /api/insert-orders`: Batch insert orders
- `/dashboard/*`: Dashboard API routes
- `GET /{path}`: Static file serving

#### 2. router.py

Dashboard API routes dengan prefix `/dashboard`.

**Dependencies:**
- `get_db()`: Dependency injection untuk database session

**Endpoints:**

**GET /dashboard/orders**
- Mengambil daftar order aktif (status: On Process, On Verification, Verified)
- Response: List of Order objects

**POST /dashboard/verification/{order_id}**
- Mengirim email verifikasi ke customer
- Validasi: Order tidak boleh sudah Verified atau On Verification
- Generate kode unik 6 karakter (alphanumeric)
- Kirim email via yagmail
- Simpan ke tabel `verifications`
- Update status order menjadi "On Verification"

**POST /dashboard/verify**
- Endpoint untuk verifikasi kode unik dari customer
- Payload: `{"kode_unik": "string"}`
- Cari kode di tabel verifications
- Update status order menjadi "Verified"
- Hapus record verifikasi

**DELETE /dashboard/order/{order_id}**
- Hapus order dan verifikasi terkait
- Cascade delete untuk data verifikasi

#### 3. scheduler.py

Background task menggunakan APScheduler.

**Task: cleanup_expired_verifications()**
- Interval: Setiap 1 jam
- Logika:
  - Query verifikasi yang berusia > 24 jam
  - Hapus order terkait
  - Hapus record verifikasi
- Tujuan: Membersihkan data pending verification yang expired

#### 4. models/db_models.py

SQLAlchemy ORM models.

**Engine Configuration:**
- Database URL dari environment variable `DATABASE_URL`
- Connection pooling dengan `pool_pre_ping=True`
- Pool recycle setiap 30 menit

**Model: Order**
- Table: `orders`
- Fields:
  - `id` (PK, autoincrement)
  - `status` (String): "On Process" | "On Verification" | "Verified"
  - `nama_customer`, `email`, `nama_barang`, `jenis_barang`
  - `jumlah_barang` (Integer)
  - `estimasi_nilai_barang` (Integer)
  - `wilayah` (String)
  - `id_percakapan` (String, legacy)
- Relationships:
  - `verifications`: One-to-many ke Verifikasi model

**Model: Verifikasi**
- Table: `verifications`
- Fields:
  - `id_verifikasi` (PK, autoincrement)
  - `id_order` (FK ke `orders.id`)
  - `kode_unik` (String, unique)
  - `created_at` (DateTime, default=now)
- Relationships:
  - `order`: Many-to-one ke Order model

#### 5. service/email_builder.py

Email service menggunakan yagmail.

**Environment Variables:**
- `EMAIL_USER`: Gmail address
- `EMAIL_PASSWORD`: Gmail app password

**generate_unique_code(length=6)**
- Generate random alphanumeric code
- Menggunakan `secrets.choice()` untuk keamanan

**send_verification_email(email, order_id, unique_code)**
- Subject: "Kode Verifikasi Peminjaman Anda"
- Body: HTML formatted dengan:
  - Greeting
  - Order ID
  - Kode verifikasi (bold, large font)
  - Instruksi penggunaan
  - Footer dengan branding
- SMTP: Gmail via yagmail

#### 6. service/database.py

Database utility functions.

**init_db()**
- Create all tables jika belum ada
- Dipanggil saat startup

**insert_order(order_data)**
- Validasi required fields
- Create Order object
- Set initial status = "On Process"
- Commit ke database
- Return order ID

---

## Frontend (React + Vite)

### Struktur Direktori

```
web_dashboard/
├── src/
│   ├── pages/
│   │   └── Dashboard.tsx    # Main dashboard page
│   ├── api.ts               # API client
│   └── index.css            # Global styles
├── public/
├── index.html
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

### Core Components

#### 1. Dashboard.tsx

Main dashboard component dengan state management lokal.

**State Variables:**
- `orders`: Array of Order objects
- `loading`: Boolean untuk loading indicator
- `sendingEmailId`: Number untuk tracking email sending per order
- `deletingId`: Number untuk tracking deletion per order

**useEffect Hooks:**
- Auto-fetch orders on mount
- Auto-refresh setiap 30 detik

**Key Functions:**

**fetchOrders()**
- Call `getOrders()` dari API client
- Update state `orders`
- Handle loading state

**handleSendVerification(orderId)**
- Call `sendVerification(orderId)`
- Set loading state untuk button tertentu
- Success: Refresh order list
- Error: Show alert

**handleDeleteOrder(orderId)**
- Show confirmation dialog
- Call `deleteOrder(orderId)`
- Set loading state
- Success: Remove from local state
- Error: Show alert

**UI Sections:**

1. **Header**
   - Title & description

2. **Stats Cards**
   - Total Orders
   - On Process (yellow)
   - On Verification (orange)
   - Verified (green)

3. **Pie Chart**
   - Distribusi order berdasarkan wilayah
   - Colors: Dynamic dari Recharts

4. **Orders Table**
   - Columns: Customer, Email, Item, Type, Quantity, Value, Region, Status, Actions
   - Status Badge: Color-coded (yellow/orange/green)
   - Action Buttons:
     - "Kirim Verifikasi": Disabled jika sudah Verified/On Verification
     - "Hapus": Delete dengan konfirmasi

#### 2. api.ts

Axios-based API client.

**Base Configuration:**
- `baseURL`: Relative path `/dashboard` (untuk static serving)
- Content-Type: application/json

**Functions:**

**getOrders()**
- GET /dashboard/orders
- Return: Order[]

**sendVerification(orderId)**
- POST /dashboard/verification/{orderId}
- Return: Success message

**deleteOrder(orderId)**
- DELETE /dashboard/order/{orderId}
- Return: Success message

#### 3. Styling

**Tailwind Configuration:**
- Custom color palette
- Responsive breakpoints
- Dark mode support (optional)

**Global Styles (index.css):**
- Font: System fonts stack
- Base colors dari Tailwind
- Smooth transitions

---

## Database Schema

### Table: orders

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, Auto | Order ID |
| status | String | NOT NULL | Order status |
| nama_customer | String | NOT NULL | Customer name |
| email | String | NOT NULL | Customer email |
| nama_barang | String | NOT NULL | Item name |
| jenis_barang | String | NOT NULL | Item category |
| jumlah_barang | Integer | NOT NULL | Item quantity |
| estimasi_nilai_barang | Integer | NOT NULL | Estimated value (IDR) |
| wilayah | String | NOT NULL | Region |
| id_percakapan | String | NULLABLE | Legacy conversation ID |

**Indexes:**
- Primary key pada `id`

### Table: verifications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id_verifikasi | Integer | PK, Auto | Verification ID |
| id_order | Integer | FK, NOT NULL | Reference to orders.id |
| kode_unik | String | UNIQUE, NOT NULL | 6-char verification code |
| created_at | DateTime | NOT NULL, Default=NOW | Creation timestamp |

**Indexes:**
- Primary key pada `id_verifikasi`
- Foreign key pada `id_order` → `orders.id`
- Unique constraint pada `kode_unik`

**Relationships:**
- One order can have multiple verifications (historical)
- One verification belongs to one order

---

## API Documentation

### Base URL

```
Production: http://localhost:2026
Development: http://localhost:2026
```

### Authentication

Tidak ada authentication untuk dashboard API (internal use).

### Endpoints

#### 1. Get Orders

**Request:**
```http
GET /dashboard/orders
```

**Response:**
```json
[
  {
    "id": 1,
    "status": "On Process",
    "nama_customer": "John Doe",
    "email": "john@example.com",
    "nama_barang": "iPhone 14",
    "jenis_barang": "Elektronik",
    "jumlah_barang": 1,
    "estimasi_nilai_barang": 10000000,
    "wilayah": "Jakarta",
    "id_percakapan": "123456"
  }
]
```

**Status Codes:**
- 200: Success
- 500: Internal server error

---

#### 2. Send Verification Email

**Request:**
```http
POST /dashboard/verification/{order_id}
```

**Path Parameters:**
- `order_id` (integer, required): Order ID

**Response:**
```json
{
  "message": "Email verifikasi telah dikirim ke customer@example.com",
  "kode_unik": "A1B2C3",
  "order_id": 1
}
```

**Status Codes:**
- 200: Email sent successfully
- 400: Order sudah verified/on verification
- 404: Order not found
- 500: Email sending failed

**Error Response:**
```json
{
  "detail": "Order sudah verified atau sedang dalam proses verifikasi"
}
```

---

#### 3. Verify Code

**Request:**
```http
POST /dashboard/verify
Content-Type: application/json

{
  "kode_unik": "A1B2C3"
}
```

**Response:**
```json
{
  "message": "Order berhasil diverifikasi",
  "order_id": 1
}
```

**Status Codes:**
- 200: Verification successful
- 404: Kode tidak valid
- 500: Internal server error

---

#### 4. Delete Order

**Request:**
```http
DELETE /dashboard/order/{order_id}
```

**Path Parameters:**
- `order_id` (integer, required): Order ID

**Response:**
```json
{
  "message": "Order berhasil dihapus"
}
```

**Status Codes:**
- 200: Deletion successful
- 404: Order not found
- 500: Internal server error

---

## Deployment

### Docker Configuration

**Multi-stage Dockerfile:**

**Stage 1: Frontend Build**
- Base: `node:18-alpine`
- Install dependencies via npm
- Build production bundle (`npm run build`)
- Output: `dist/` folder

**Stage 2: Backend Setup**
- Base: `python:3.10-slim`
- Install system dependencies (gcc, libpq-dev)
- Install Python packages dari requirements.txt
- Copy backend code
- Copy frontend build dari Stage 1 ke `/app/static`

**docker-compose.yml Services:**

1. **db**: PostgreSQL 15
   - Port: 5433:5432
   - Volume: postgres_data

2. **app**: Main application
   - Build from Dockerfile
   - Port: 2026:2026
   - Depends on: db
   - Environment: DATABASE_URL, EMAIL credentials

3. **n8n**: Workflow automation
   - Port: 5679:5678
   - Volume: n8n_data, workflow mount
   - Depends on: db, ollama

4. **ollama**: LLM engine
   - Port: 11435:11434
   - Volume: ollama_data
   - GPU support (optional)

5. **qdrant**: Vector database
   - Port: 6335-6336:6333-6334
   - Volume: qdrant_data

6. **ngrok**: Tunneling
   - Command: `http n8n:5678 --url=https://${NGROK_DOMAIN}`
   - Environment: NGROK_AUTHTOKEN

### Environment Variables

**Required Variables (.env):**

```ini
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=pg_n8n_gadaielektronik

# Email
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=gmail_app_password
APPS_KEY=secret_key

# n8n
N8N_HOST=localhost

# Ngrok
NGROK_AUTHTOKEN=your_token
NGROK_DOMAIN=your-domain.ngrok-free.app

# Ollama
OLLAMA_MODEL=qwen3-vl:235b-instruct-cloud
```

### Build & Run

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Static File Serving

Frontend files disajikan oleh FastAPI dari endpoint root (`/`):

```python
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

Request flow:
1. Browser request `http://localhost:2026/`
2. FastAPI serve `static/index.html`
3. Browser load JS/CSS dari `static/assets/`
4. Frontend call API via `/dashboard/*`
5. FastAPI process API request

### Port Mapping

| Service | Container Port | Host Port | Konflik? |
|---------|----------------|-----------|----------|
| Dashboard | 2026 | 2026 | No |
| PostgreSQL | 5432 | 5433 | Yes (local PG) |
| n8n | 5678 | 5679 | Yes (existing n8n) |
| Ollama | 11434 | 11435 | Yes (existing ollama) |
| Qdrant | 6333-6334 | 6335-6336 | Yes (existing qdrant) |
| Ngrok | - | - | No (tunnel only) |

---

## Development Workflow

### Backend Development

1. Activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run: `uvicorn app.main:app --reload --port 2026`

### Frontend Development

1. Navigate: `cd web_dashboard`
2. Install: `npm install`
3. Dev server: `npm run dev` (port 5173)
4. Build: `npm run build`
5. Deploy: Copy `dist/*` ke `utils/static/`

### Database Migrations

Currently using auto-create via SQLAlchemy (`Base.metadata.create_all()`).
For production, consider using Alembic for migrations.

### Testing

Not implemented yet. Recommendations:
- Backend: pytest + pytest-asyncio
- Frontend: Vitest + React Testing Library
- E2E: Playwright

---

## Security Considerations

1. **Email Credentials**: Stored in environment variables, never in code
2. **Database Password**: Environment variable, Docker secrets recommended
3. **CORS**: Configured untuk specific origins (production)
4. **Input Validation**: Pydantic models untuk API payloads
5. **SQL Injection**: Protected via SQLAlchemy ORM
6. **Rate Limiting**: Not implemented (TODO)
7. **HTTPS**: Handled by ngrok tunnel for n8n webhooks

---

## Performance Optimization

1. **Database Connection Pooling**: SQLAlchemy pool with pre-ping
2. **Frontend Build**: Vite production build dengan minification
3. **Static File Caching**: Browser cache headers (TODO)
4. **API Response**: Lazy loading untuk large datasets (TODO)
5. **Background Tasks**: APScheduler untuk cleanup, tidak blocking request

---

## Monitoring & Logging

**Current State:**
- Docker logs via `docker logs {container}`
- SQLAlchemy echo untuk SQL queries (development only)
- Console logs di frontend

**Recommendations:**
- Implement structured logging (loguru)
- Add health check endpoints
- Integrate monitoring (Prometheus + Grafana)
- Error tracking (Sentry)

---

## Future Enhancements

1. **Authentication & Authorization**
   - User roles (admin, operator)
   - JWT-based auth
   
2. **Real-time Updates**
   - WebSocket untuk live order updates
   - Server-Sent Events (SSE)

3. **Advanced Features**
   - Order search & filtering
   - Export ke Excel/PDF
   - Email templates customization
   - Multi-language support

4. **Testing**
   - Unit tests untuk backend
   - Integration tests
   - E2E tests dengan Playwright

5. **CI/CD**
   - GitHub Actions untuk automated testing
   - Docker image build & push
   - Automated deployment

---

## Troubleshooting

### Common Issues

**1. Database Connection Error**
- Check: DATABASE_URL di .env
- Check: PostgreSQL container running
- Solution: Restart app container

**2. Email Sending Failed**
- Check: EMAIL_USER, EMAIL_PASSWORD di .env
- Check: Gmail "Less secure app access" atau App Password
- Solution: Generate new App Password

**3. Frontend Not Loading**
- Check: Static files di `utils/static/`
- Solution: Rebuild frontend (`npm run build`)

**4. Port Already in Use**
- Check: `docker ps -a`
- Solution: Change host ports di docker-compose.yml

**5. ngrok Restarting Loop**
- Check: NGROK_DOMAIN format (tanpa https://)
- Check: NGROK_AUTHTOKEN valid
- Solution: Update .env, restart container
