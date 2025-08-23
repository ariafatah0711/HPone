# HPone - Docker Honeypot Manager

**HPone** is a honeypot tool for managing Docker honeypot templates with **auto-import** features that simplify deployment and management.

## 🔑 Operational Modes

HPone can be run in two main modes:

### **Automatic Mode (ALWAYS_IMPORT=true)**
- ✅ **Auto-import** honeypots at startup
- ✅ **Command simplified** - no manual import/update required
- ✅ **Production ready** - minimal human intervention
- ✅ **Smart management** - honeypots managed automatically
- ✅ **Ephemeral logging** - clean real-time log display

### **Manual Mode (ALWAYS_IMPORT=false)**
- 🔧 **Full control** - manual import/update
- 🔧 **Development friendly** - debugging and testing
- 🔧 **Template management** - update and maintenance

## 📁 Project Structure

```
HPone/
├── app.py                 # Launcher script
├── hpone/                 # Main application
│   ├── app.py              # Main application
│   ├── config.py           # Configuration file
│   ├── completion/         # Bash completion scripts
│   ├── core/               # Core modules
│   └── scripts/            # Command scripts
├── honeypots/             # YAML honeypot files
├── template/docker/       # Base templates for generating Dockerfiles and related configs
├── conf/                  # Custom persistent configuration (stored on host)
├── docker/                # Generated Docker build output (temporary, not persistent)
└── data/                  # Container volume for logs and runtime data
```

## ⚙️ Configuration

Edit `hpone/config.py`:

```python
# Behavior mode
ALWAYS_IMPORT = True          # True: auto-import (hide import/update), False: manual control

# Path configuration
HONEYPOT_MANIFEST_DIR = PROJECT_ROOT / "honeypots"
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"
DATA_DIR = PROJECT_ROOT / "data"   # mount location for container log data (safe to delete during folder clean)

# Display configuration
LIST_BASIC_MAX_WIDTH = 80      # Max width for basic list
LIST_DETAILED_MAX_WIDTH = 30   # Max width for list -a (detailed)
STATUS_TABLE_MAX_WIDTH = 40    # Max width for status table columns

# Logging configuration
USE_EPHEMERAL_LOGGING = True  # True: real-time logs, False: simple output
```

## 🚀 Fast Setup (auto install)
```bash
git clone https://github.com/ariafatah0711/HPone hpone
cd hpone

# setup Global Installation, and Bash Completion
chmod +x setup.sh
./setup.sh install # restart shell after execution

# Uninstall Global Installation, and Bash Completion
./setup.sh uninstall # restart shell after execution
```

## 🛠 Manual Install
### 📦 Install Library & Dependencies
```bash
# install library
pip3 install requirements.txt

# install docker.io
sudo apt install docker.io

# install docker compose
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose

chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
# or
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# verify
docker compose version
```

### ⚙️ Global Installation (Run Anywhere)

To run `hpone` from anywhere without `./app.py`:

```bash
chmod +x app.py
sudo ln -s $(pwd)/app.py /usr/local/bin/hpone

hpone -h
```

## ⌨️ Bash Completion

For ease of use, HPone provides bash completion.

### **Installation**
```bash
chmod +x hpone/completion/install.sh
./hpone/completion/install.sh # restart shell required

# or manually
source hpone/completion/hpone-completion.bash
```

### **Usage**
```bash
./app.py <TAB>                    # Complete command
./app.py inspect <TAB>            # Complete honeypot name
./app.py logs <TAB>               # Complete honeypot name
./app.py up <TAB>                 # Complete honeypot or --all

hpone <TAB>                       # Complete command
hpone clean <TAB>              # Complete honeypot name
hpone logs <TAB>               # Complete honeypot name
hpone up <TAB>                 # Complete honeypot or --all
```

### **Uninstall**
```bash
chmod +x hpone/completion/uninstall.sh
./hpone/completion/uninstall.sh
```

See `hpone/completion/README.md` for complete information.

## 🎯 How to Use

### **Quick Start (ALWAYS_IMPORT=true)**

```bash
# Enable required honeypots
hpone enable cowrie
hpone enable medpot

# Start honeypots (auto-import + up)
hpone up cowrie
hpone up medpot

# Start all enabled honeypots
hpone up --all

# Check status
hpone list
hpone status

# View logs interactively
hpone logs cowrie
hpone logs medpot

# Stop honeypots
hpone down cowrie
hpone down --all

# Open shell in container
hpone shell cowrie

# Clean honeypots (stop + remove)
hpone clean cowrie
hpone clean --all --data
```

## 🔧 Command Reference

### **Available Commands**
- `check` - Check dependencies
- `list` - List honeypots (`-a` for details)
- `status` - Show running status
- `inspect <honeypot>` - Show honeypot details
- `enable/disable <honeypot>` - Enable/disable honeypots
- `up <honeypot>` - Start honeypot (auto-import)
- `up --all` - Start all enabled honeypots
- `down <honeypot>` - Stop honeypot
- `down --all` - Stop all honeypots
- `shell <honeypot>` - Open shell (bash/sh) in running container
- `logs <honeypot>` - Interactive log viewer with file browsing
- `clean <honeypot>` - Stop + remove honeypot
- `clean --all` - Stop + remove all honeypots
- `clean --data` - Also remove data volumes
- `clean --image` - Also remove images
- `clean --volume` - Also remove volumes

### **Examples**

```bash
# Basic workflow
hpone enable cowrie
hpone up cowrie
hpone logs cowrie    # Interactive log viewer
hpone shell cowrie
hpone down cowrie

# Check status
hpone list
hpone status

# Log viewing features
hpone logs cowrie    # Interactive menu with:
                     # - Recent Docker logs (last 30 lines)
                     # - Follow live logs (tail -f)
                     # - Browse log files in data directories
                     # - View, search, and follow individual files

# Clean everything
hpone clean --all --data --image --volume

# Force start disabled honeypot
hpone up wordpot --force
```

## 🔍 Troubleshooting

### **Check Dependencies**
```bash
hpone check
```

### **View Logs**
```bash
# Check Docker logs
docker logs cowrie

# Check compose status
docker-compose -f docker/cowrie/docker-compose.yml ps
```

### **Ephemeral Logging**
HPone uses ephemeral logging for clean real-time display:

```
[22:48:02] [INFO] Starting cowrie containers ...
[22:48:05] [INFO] Docker network created
[22:48:06] [INFO] Building cowrie image
[22:48:10] [INFO] Container cowrie started
[UP] cowrie OK (2.3s)
```

If there are issues, set `USE_EPHEMERAL_LOGGING = False` in `config.py`.

## 📝 Notes

- **ALWAYS_IMPORT=true**: Production mode, minimal commands, auto-management
- **ALWAYS_IMPORT=false**: Development mode, full control, manual management
- **Disabled** tools will not auto-start
- Use `--force` to override enabled status
- `shell` command requires a running container

## 🤝 Contributing

1. Fork project
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the `LICENSE` file.
