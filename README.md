# HPone - Docker Honeypot Manager

**HPone** adalah tool untuk mengelola Docker honeypot templates dengan fitur **auto-import** yang memudahkan deployment dan management.

## 🚀 Fitur Utama: ALWAYS_IMPORT Mode

### **Mode Otomatis (ALWAYS_IMPORT=true)**
- ✅ **Auto-import** tools saat startup
- ✅ **Command simplified** - tidak ada import/remove manual
- ✅ **Production ready** - minimal human intervention
- ✅ **Smart management** - tools dikelola otomatis

### **Mode Manual (ALWAYS_IMPORT=false)**
- 🔧 **Full control** - import/remove/update manual
- 🔧 **Development friendly** - debugging dan testing
- 🔧 **Template management** - update dan maintenance

## 📁 Struktur Project

```
HPone/
├── app.py                 # Launcher script (dari folder lain)
├── hpone/                 # Main application
│   ├── app.py            # Main application
│   ├── config.py         # Configuration file
│   ├── core/             # Core modules
│   └── scripts/          # Command scripts
├── tools/                 # YAML honeypot files
├── template/docker/       # Docker templates
└── docker/               # Output Docker files
└── data/                 # folder for volume container
```

## ⚙️ Konfigurasi

Edit `hpone/config.py`:

```python
# Behavior mode
ALWAYS_IMPORT = True          # True: auto-import, False: manual control

# Path configuration
TOOLS_DIR = PROJECT_ROOT / "tools"
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"

# List display settings
LIST_BASIC_MAX_WIDTH = 80
LIST_DETAILED_MAX_WIDTH = 30
```

## 🎯 Cara Pakai

### **1. Quick Start (ALWAYS_IMPORT=true)**

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

# paksa up tool yang tidak enable
./app.py up conpot --force
```

### **2. Manual Mode (ALWAYS_IMPORT=false)**

```bash
# Import tools
./app.py import cowrie
./app.py import --all

# Update templates
./app.py update

# Start tools
./app.py up cowrie
./app.py up --all --update

# Stop tools
./app.py down --all

# Remove tools
./app.py remove cowrie
./app.py remove --all
```

## 🔧 Command Reference

### **Available Commands (ALWAYS_IMPORT=true)**
- `check` - Check dependencies
- `list` - List tools
- `status` - Show running status
- `inspect` - Show tool details
- `enable/disable` - Enable/disable tools
- `up/down` - Start/stop tools (auto-import)

### **Hidden Commands (ALWAYS_IMPORT=true)**
- ❌ `import` - Disabled (auto-import)
- ❌ `remove` - Disabled (auto-managed)
- ❌ `update` - Disabled (auto-update)

### **All Commands (ALWAYS_IMPORT=false)**
- Semua command tersedia seperti biasa

## 📊 Tool Management

### **Enable/Disable Tools**
```bash
# Enable tool
./app.py enable cowrie

# Disable tool
./app.py disable wordpot

# Check status
./app.py list
```

### **Tool Information**
```bash
# Basic list
./app.py list

# Detailed list
./app.py list -a

# Tool details
./app.py inspect cowrie
```

## 🔍 Troubleshooting

### **Check Dependencies**
```bash
./app.py check
```

### **Force Start Non-enabled Tool**
```bash
./app.py up wordpot --force
```

### **View Logs**
```bash
# Check Docker logs
docker logs cowrie

# Check compose status
docker-compose -f docker/cowrie/docker-compose.yml ps

cat data/cowrie/*
```

## 📝 Notes

- **ALWAYS_IMPORT=true**: Mode production, minimal command, auto-management
- **ALWAYS_IMPORT=false**: Mode development, full control, manual management
- Tools yang **disabled** tidak akan auto-start
- Gunakan `--force` untuk override enabled status
- Semua path bisa dikustomisasi di `config.py`

## 🤝 Contributing

1. Fork project
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

Proyek ini dilisensikan di bawah GNU General Public License v3.0 (GPL-3.0). Lihat berkas `LICENSE`.
