# HPone - Docker Honeypot Manager

**HPone** adalah tool untuk mengelola Docker honeypot templates dengan fitur **auto-import** yang memudahkan deployment dan management.

## 🚀 Fitur Utama: ALWAYS_IMPORT Mode

### **Mode Otomatis (ALWAYS_IMPORT=true)**
- ✅ **Auto-import** tools saat startup
- ✅ **Command simplified** - tidak ada import/remove manual
- ✅ **Production ready** - minimal human intervention
- ✅ **Smart management** - tools dikelola otomatis
- ✅ **Ephemeral logging** - tampilan log real-time yang bersih

### **Mode Manual (ALWAYS_IMPORT=false)**
- 🔧 **Full control** - import/remove/update manual
- 🔧 **Development friendly** - debugging dan testing
- 🔧 **Template management** - update dan maintenance

## 📁 Struktur Project

```
HPone/
├── app.py                 # Launcher script
├── hpone/                 # Main application
│   ├── app.py            # Main application
│   ├── config.py         # Configuration file
│   ├── core/             # Core modules
│   └── scripts/          # Command scripts
├── tools/                 # YAML honeypot files
├── template/docker/       # Docker templates
├── docker/               # Output Docker files
├── data/                 # Volume data container
└── conf/                 # Config container custom (persistent)
```

## ⚙️ Konfigurasi

Edit `hpone/config.py`:

```python
# Behavior mode
ALWAYS_IMPORT = True          # True: auto-import (hide import/update), False: manual control

# Path configuration
TOOLS_DIR = PROJECT_ROOT / "tools"
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"
DATA_DIR = PROJECT_ROOT / "data"   # lokasi mount data log container (ini buat filter kalo folder clean ini aman di hapus)

# Logging configuration
USE_EPHEMERAL_LOGGING = True  # True: real-time logs, False: simple output
```

## 🎯 Cara Pakai

### **Quick Start (ALWAYS_IMPORT=true)**

```bash
# Enable tools yang dibutuhkan
./app.py enable cowrie
./app.py enable medpot

# Start tools (auto-import + up)
./app.py up cowrie
./app.py up medpot

# Start semua enabled tools
./app.py up --all

# Check status
./app.py list
./app.py status

# Stop tools
./app.py down cowrie
./app.py down --all

# Buka shell di container
./app.py shell cowrie

# Clean tools (stop + remove)
./app.py clean cowrie
./app.py clean --all --data
```

## 🔧 Command Reference

### **Available Commands**
- `check` - Check dependencies
- `list` - List tools (`-a` untuk detail)
- `status` - Show running status
- `inspect <tool>` - Show tool details
- `enable/disable <tool>` - Enable/disable tools
- `up <tool>` - Start tool (auto-import)
- `up --all` - Start all enabled tools
- `down <tool>` - Stop tool
- `down --all` - Stop all tools
- `shell <tool>` - Open shell (bash/sh) in running container
- `clean <tool>` - Stop + remove tool
- `clean --all` - Stop + remove all tools
- `clean --data` - Also remove data volumes
- `clean --image` - Also remove images
- `clean --volume` - Also remove volumes

### **Examples**

```bash
# Basic workflow
./app.py enable cowrie
./app.py up cowrie
./app.py shell cowrie
./app.py down cowrie

# Clean everything
./app.py clean --all --data --image --volume

# Force start disabled tool
./app.py up wordpot --force
```

## 🔍 Troubleshooting

### **Check Dependencies**
```bash
./app.py check
```

### **View Logs**
```bash
# Check Docker logs
docker logs cowrie

# Check compose status
docker-compose -f docker/cowrie/docker-compose.yml ps
```

### **Ephemeral Logging**
HPone menggunakan ephemeral logging untuk tampilan real-time yang bersih:

```
[22:48:02] [INFO] Starting cowrie containers ...
[22:48:05] [INFO] Docker network created
[22:48:06] [INFO] Building cowrie image
[22:48:10] [INFO] Container cowrie started
[UP] cowrie OK (2.3s)
```

Jika bermasalah, set `USE_EPHEMERAL_LOGGING = False` di `config.py`.

## 📝 Notes

- **ALWAYS_IMPORT=true**: Mode production, minimal command, auto-management
- **ALWAYS_IMPORT=false**: Mode development, full control, manual management
- Tools yang **disabled** tidak akan auto-start
- Gunakan `--force` untuk override enabled status
- Perintah `shell` membutuhkan container yang sedang running

## 🤝 Contributing

1. Fork project
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

Proyek ini dilisensikan di bawah GNU General Public License v3.0 (GPL-3.0). Lihat berkas `LICENSE`.
