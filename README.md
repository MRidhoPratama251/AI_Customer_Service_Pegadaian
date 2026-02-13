# AI Customer Service - Gadai Emas & Elektronik

Sistem AI Customer Service berbasis Telegram untuk layanan gadai barang elektronik dan emas, dilengkapi dengan dashboard admin untuk monitoring dan verifikasi pesanan.

## Arsitektur Sistem

Aplikasi ini terdiri dari beberapa service dalam Docker:

- **Dashboard Admin** (FastAPI + React): Monitoring & verifikasi pesanan
- **n8n**: Workflow automation & AI agent
- **Ollama**: LLM engine (mendukung model cloud)
- **PostgreSQL**: Database utama
- **Qdrant**: Vector database untuk RAG
- **Ngrok**: Tunneling untuk webhook Telegram

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac/Linux)
- [Git](https://git-scm.com/downloads)
- Akun [Ngrok](https://ngrok.com/) (gratis)
- Akun [Ollama](https://ollama.com/) (untuk cloud models)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-username/AI_Customer_Service_Pegadaian.git
cd AI_Customer_Service_Pegadaian
```

### 2. Setup Environment Variables

Copy template `.env.docker` menjadi `.env`:

```bash
# Windows
copy .env.docker .env

# Linux/Mac
cp .env.docker .env
```

Edit file `.env` dan isi dengan kredensial Anda:

```ini
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=pg_n8n_gadaielektronik

# Email Configuration (Gmail App Password)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
APPS_KEY=your_secret_key

# n8n Configuration
N8N_HOST=localhost

# Ngrok Configuration
NGROK_AUTHTOKEN=your_ngrok_authtoken
NGROK_DOMAIN=your-domain.ngrok-free.app

# Ollama Configuration
OLLAMA_MODEL=qwen3-vl:235b-instruct-cloud
```

**Cara mendapatkan kredensial:**

- **Gmail App Password**: [Google Account → Security → 2-Step Verification → App passwords](https://myaccount.google.com/apppasswords)
- **Ngrok Token**: [Dashboard Ngrok → Your Authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)
- **Ngrok Domain**: [Dashboard Ngrok → Domains → Create Domain](https://dashboard.ngrok.com/cloud-edge/domains)

### 3. Build & Run

```bash
docker-compose up -d --build
```

Tunggu beberapa menit untuk download image dan build aplikasi.

### 4. Setup Ollama (Cloud Models)

Jika menggunakan Ollama cloud model, Anda perlu login sekali:

```bash
docker exec -it gadai_ollama ollama login
```

Ikuti instruksi di terminal, lalu download model:

```bash
docker exec -it gadai_ollama ollama pull qwen3-vl:235b-instruct-cloud
```

### 5. Import Workflow n8n

1. Buka n8n via URL Ngrok atau `http://localhost:5679`
2. Buat akun owner saat pertama kali (hanya sekali)
3. Pilih menu **"Import from File"**
4. Browse ke `/home/node/workflows/ai_pegadaian.json` (sudah di-mount otomatis)

## Akses Aplikasi

| Service | URL | Keterangan |
|---------|-----|------------|
| **Dashboard Admin** | http://localhost:2026 | Monitoring & verifikasi order |
| **n8n (Local)** | http://localhost:5679 | Workflow automation UI |
| **n8n (Public)** | https://your-domain.ngrok-free.app | Webhook untuk Telegram |
| **Qdrant UI** | http://localhost:6335/dashboard | Vector database dashboard |
| **PostgreSQL** | `localhost:5433` | Database (port 5433) |
| **Ollama API** | http://localhost:11435 | LLM API endpoint |

## Konfigurasi n8n

Setelah import workflow, update kredensial berikut di n8n:

1. **Ollama Node**: Ubah host menjadi `http://ollama:11434`
2. **Qdrant Node**: Ubah host menjadi `http://qdrant:6333`
3. **PostgreSQL Node**: 
   - Host: `db`
   - Port: `5432`
   - User/Password/Database: Sesuai `.env`

## Struktur Project

```
.
├── ai_agent_flow_n8n/          # n8n workflow JSON
├── web_dashboard/              # Frontend React (Vite)
│   └── src/
│       ├── pages/Dashboard.tsx
│       └── api.ts
├── utils/                      # Backend FastAPI
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── router.py          # API endpoints
│   │   ├── scheduler.py       # Background jobs
│   │   ├── models/            # Database models
│   │   └── service/           # Business logic
│   ├── static/                # Built frontend (auto-generated)
│   └── requirements.txt
├── docker-compose.yml         # Orchestration
├── Dockerfile                 # Multi-stage build
├── .env.docker               # Template environment
└── README.md
```

## Development

### Update Frontend

```bash
cd web_dashboard
npm install
npm run dev  # Development server di port 5173
```

### Rebuild & Deploy

Setelah edit code, rebuild image:

```bash
docker-compose up -d --build
```

### View Logs

```bash
# Semua services
docker-compose logs -f

# Service tertentu
docker logs gadai_app -f
docker logs gadai_n8n -f
```

### Stop & Clean

```bash
# Stop semua container
docker-compose down

# Stop & hapus volume (HATI-HATI: Data akan hilang!)
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

Jika ada error "port already allocated", ubah host port di `docker-compose.yml`.

### Ngrok Restarting Loop

Pastikan:
- `NGROK_DOMAIN` **tidak** ada `https://` dan **tidak** pakai tanda kutip
- Format benar: `NGROK_DOMAIN=your-domain.ngrok-free.app`

### Ollama Cloud Model Tidak Ada

Jalankan login + pull model seperti di Step 4.

### Database Connection Error

Pastikan `.env` sudah benar, lalu restart:

```bash
docker-compose restart gadai_app
```

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - Silakan digunakan untuk keperluan komersial maupun non-komersial.

## Contact

Project Link: [https://github.com/your-username/AI_Customer_Service_Pegadaian](https://github.com/your-username/AI_Customer_Service_Pegadaian)
