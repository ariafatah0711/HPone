<div align="center">

# 🍯 HPone - Docker Honeypot Manager

<p align="center">
  <strong>A powerful Docker honeypot management tool with auto-import capabilities</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=for-the-badge" alt="License">
</p>

</div>

---

## 🎯 Overview

**HPone** is a comprehensive Docker-based honeypot management platform that simplifies the deployment, monitoring, and maintenance of security honeypots. With intelligent auto-import features and streamlined command interfaces, HPone makes honeypot management accessible for both production and development environments.

### ✨ Key Features

- 🚀 **Auto-Import System** - Seamless honeypot template deployment
- 🐳 **Docker Integration** - Containerized honeypot environments
- 📊 **Real-time Monitoring** - Live log streaming and status tracking
- 🔧 **Flexible Configuration** - YAML-based honeypot definitions
- 🛡️ **Multi-Honeypot Support** - Manage multiple honeypot types simultaneously
- 💻 **Interactive CLI** - User-friendly command-line interface with bash completion
- ✏️ **Built-in Editor** - Edit configurations directly from command line

## 🎬 Quick Demo

*Demo video coming soon - showing HPone's key features in action!*

<!-- TODO: Add demo video here showing:
- Installation process
- Basic honeypot setup
- Monitoring and logs
- Configuration editing
-->

---

## 📁 Project Structure

```
📦 HPone/
┣ 🚀 app.py                     # Main launcher script
┣ 📂 hpone/                     # Core application directory
┃ ┣ 🎯 app.py                   # Application entry point
┃ ┣ ⚙️ config.py               # Configuration management
┃ ┣ 📂 completion/              # Bash completion scripts
┃ ┣ 📂 core/                    # Core functionality modules
┃ ┗ 📂 scripts/                 # Command implementations
┣ 📂 honeypots/                 # 🍯 YAML honeypot definitions
┣ 📂 template/docker/           # 📋 Base Docker templates
┣ 📂 conf/                      # 🔧 Persistent configurations
┣ 📂 docker/                    # 🐳 Generated build outputs (temp)
┗ 📂 data/                      # 💾 Runtime data & logs
┗ 📋 requirements.txt           # Python dependencies
```

## ⚙️ Configuration

Configure HPone behavior by editing the configuration file:

- **📦 Debian Package Installation:** `/opt/hpone/hpone/config.py`
- **🔧 Source Installation:** `hpone/config.py` (in your project directory)

<details>
<summary><strong>📋 View Configuration Options</strong></summary>

```python
# 🎭 Behavior Mode
ALWAYS_IMPORT = True              # Auto-import vs Manual control

# 📍 Path Configuration
HONEYPOT_MANIFEST_DIR = PROJECT_ROOT / "honeypots"    # YAML definitions
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"  # Base templates
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"           # Build outputs
DATA_DIR = PROJECT_ROOT / "data"                      # Runtime data

# 🖥️  Display Configuration
LIST_BASIC_MAX_WIDTH = 80         # Basic list width
LIST_DETAILED_MAX_WIDTH = 30      # Detailed list width
STATUS_TABLE_MAX_WIDTH = 40       # Status table width

# 📝 Logging Configuration
USE_EPHEMERAL_LOGGING = True      # Real-time vs Simple output
```

</details>

## 🚀 Quick Setup

### 📦 Debian Package Installation (Recommended)

```bash
# Download and install the latest .deb package
wget https://github.com/ariafatah0711/HPone/releases/latest/download/hpone_all.deb

sudo apt install -f ./hpone_all.deb
sudo usermod -aG docker $USER

# 🔄 IMPORTANT: Restart your shell session to activate changes
exec $SHELL # Restart current shell with: logout and login again, OR open a new terminal window
```

**📍 Installation Location:** When installed via Debian package, HPone is located at `/opt/hpone/`

<details>
<summary><strong>📂 Debian Package Directory Structure</strong></summary>

```
📦 /opt/hpone/                   # Main installation directory
┣ 🚀 app.py                     # Main application entry point
┣ 📂 hpone/                     # Core application directory
┃ ┣ 🎯 app.py                   # Application launcher
┃ ┣ ⚙️ config.py               # Configuration management
┃ ┣ 📂 completion/              # Bash completion scripts
┃ ┣ 📂 core/                    # Core functionality modules
┃ ┗ 📂 scripts/                 # Command implementations
┣ 📂 honeypots/                 # 🍯 YAML honeypot definitions
┣ 📂 template/docker/           # 📋 Base Docker templates
┣ 📂 conf/                      # 🔧 Persistent configurations
┣ 📂 docker/                    # 🐳 Generated build outputs (temp)
┣ 📂 data/                      # 💾 Runtime data & logs
┗ 📋 requirements.txt           # Python dependencies
```

**🔗 Global Access:** The `hpone` command is available system-wide via `/usr/bin/hpone`

</details>

### 🔧 Source Installation

```bash
# Clone and setup HPone
git clone https://github.com/ariafatah0711/HPone hpone
cd hpone

# 🔧 Setup with global installation & bash completion
chmod +x setup.sh
./setup.sh install

# 🔄 IMPORTANT: Restart your shell session to activate changes
exec $SHELL # Restart current shell with: logout and login again, OR open a new terminal window
```

---

## 🛠 Manual Installation

<details>
<summary><strong>📦 Dependencies & Libraries</strong></summary>

### 🔍 Install Required Dependencies

```bash
# 🐍 Install Python dependencies
pip3 install -r requirements.txt

# 🐳 Install Docker Engine
sudo apt install docker.io
sudo usermod -aG docker $USER

# 📦 Install Docker Compose
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.0/docker-compose-linux-x86_64 \
  -o $DOCKER_CONFIG/cli-plugins/docker-compose

# 🔒 Set executable permissions
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
# Alternative system-wide installation
# sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# ✅ Verify installation
docker compose version
```

</details>

<details>
<summary><strong>🌐 Global Installation</strong></summary>

### 🔗 Make HPone Available System-Wide

```bash
# 🔒 Set executable permissions
chmod +x app.py

# 🔗 Create symbolic link for global access
sudo ln -s $(pwd)/app.py /usr/local/bin/hpone

# ✅ Test global installation
hpone -h
```

</details>

<details>
<summary><strong>⌨️ Bash Completion Setup</strong></summary>

```bash
# Quick setup
chmod +x hpone/completion/install.sh
./hpone/completion/install.sh
exec $SHELL  # Restart shell
```

🎨 **Tab completion works for all commands and honeypot names!**

</details>

---

## 🗑️ Uninstall

### 📦 Debian Package Removal

```bash
sudo apt remove hpone # Remove the installed package
sudo apt purge hpone # Optional: Remove configuration files

# 🔄 **IMPORTANT:** Restart your shell session after removal:
exec $SHELL # Restart current shell with: logout and login again, OR open a new terminal window
```

### 🔄 Source Installation Removal

```bash
# 🧹 Uninstall global installation & bash completion
chmod +x setup.sh
./setup.sh uninstall

# 🔄 IMPORTANT: Restart your shell session after uninstallation
exec $SHELL                       # Restart current shell

# 🗂️ Optional: Remove project directory
cd ..
rm -rf hpone
```

## 🎯 Getting Started

### 🚀 **Quick Start**

#### ⚙️ **Setup**
```bash
hpone enable cowrie medpot conpot # Enable multiple honeypots
hpone up --all                    # Start all enabled honeypots
```

#### 📈 **Monitor**
```bash
hpone list -a                 # Check status
hpone logs cowrie             # View logs
```

#### 💻 **Manage**
```bash
hpone edit cowrie             # Edit configuration
hpone shell cowrie            # Container access
hpone clean --all --data      # Stop & cleanup
```

## 🔧 Command Reference

### 📊 **Core Commands**

| Command | Description | Options | Example |
|---------|-------------|---------|----------|
| 🔍 `check` | Verify dependencies | - | `hpone check` |
| 📋 `list` | Show honeypots | `-a` | `hpone list -a` |
| 📈 `status` | Runtime status | - | `hpone status` |
| 🔎 `inspect` | Honeypot details | - | `hpone inspect cowrie` |
| ✏️ `edit` | Edit configurations | `<honeypot>`, `--config`, `--completion` | `hpone edit cowrie` |

**✨ Edit Features:** Smart editor detection • SSH-aware • YAML validation • Interactive recovery • Tab completion

### 🏃 **Lifecycle Commands**

| Command | Description | Options | Example |
|---------|-------------|---------|----------|
| ⚙️ `enable/disable` | Toggle honeypot(s) | - | `hpone enable cowrie medpot` |
| 🚀 `up` | Start honeypot | `--all`, `--force` | `hpone up --all` |
| 📏 `down` | Stop honeypot | `--all` | `hpone down cowrie` |
| 💻 `shell` | Container access | - | `hpone shell cowrie` |
| 📄 `logs` | Interactive logs | - | `hpone logs cowrie` |
| 🗑️ `clean` | Stop & remove | `--all`, `--data`, `--image`, `--volume` | `hpone clean --all --data` |

### 🎨 **Quick Examples**

```bash
# 🚀 Basic workflow
hpone enable cowrie conpot
hpone up --all
hpone logs cowrie     # Interactive log viewer
hpone shell cowrie    # Container access
hpone down cowrie

# 📝 Configuration
hpone edit cowrie     # Edit honeypot config
hpone edit --config   # Edit main settings

# 📊 Monitoring
hpone list -a         # Detailed status
hpone status          # Port mappings

# 🗑️ Cleanup
hpone clean --all --data --image --volume
```

## 🔍 Troubleshooting

### 🥾 **Dependency Check**
```bash
hpone check  # Comprehensive system validation
```

### 📂 **Accessing HPone Files**

**📦 Debian Package Installation:**
```bash
# Configuration files
sudo nano /opt/hpone/hpone/config.py

# View honeypot templates
ls /opt/hpone/honeypots/

# Check data directory
ls /opt/hpone/data/

# Access application files
cd /opt/hpone/
```

**🔧 Source Installation:**
```bash
# Configuration files
nano hpone/config.py

# All files are in your project directory
ls honeypots/
ls data/
```

### 📝 **Ephemeral Logging System**

HPone features **real-time ephemeral logging** for clean output:

```
[22:48:02] [INFO] Starting cowrie containers...
[22:48:05] [INFO] Docker network created
[22:48:06] [INFO] Building cowrie image
[22:48:10] [INFO] Container cowrie started
🚀 [UP] cowrie OK (2.3s)
```

**🐛 Issues?** Set `USE_EPHEMERAL_LOGGING = False` in `config.py` for detailed output.

---

## 📋 Creating Custom Honeypots

### 🎨 **YAML Configuration Template**

Create a new file in `honeypots/` directory:

```yaml
# 🍯 Custom Honeypot Definition
name: myhoneypot
description: "Custom honeypot for HTTP services"
enabled: true

# 📁 Optional: Custom template directory
template_dir: custom/template/path  # Relative or absolute path

# 🌐 Port Configuration
ports:
- host: 8080
  container: 80
  description: "HTTP service"
- host: 8443
  container: 443
  description: "HTTPS service"

# 🌍 Environment Variables (merged with template defaults)
env:
  MY_CUSTOM_VAR: "production_value"
  DEBUG_MODE: "false"
  LOG_LEVEL: "INFO"

# 💾 Volume Mounts
volumes:
- data/myhoneypot/logs:/app/logs           # Persistent logs
- conf/myhoneypot/config.yml:/app/config.yml  # Custom config override
```

### 🔑 **Key Configuration Fields**

| Field | Type | Description |
|-------|------|-------------|
| `template_dir` | Optional | Custom template path (relative to project or absolute) |
| `env` | Object | Environment variables (merged with template defaults) |
| `ports` | Array | Port mappings with optional descriptions |
| `volumes` | Array | Volume mounts for data persistence and configuration |

---

## 📝 Important Notes

### 🚀 **Operation Modes**

HPone has two modes configured in `hpone/config.py`:

- 🤖 **Auto Mode** (`ALWAYS_IMPORT=true`) - Production ready, auto-manages templates
- 🔧 **Manual Mode** (`ALWAYS_IMPORT=false`) - Development friendly, full control

### 📝 **Quick Tips**
- ⚠️ Disabled honeypots won't auto-start
- 👍 Use `--force` to override enabled status
- 💻 `shell` command requires running containers

---

## 🤝 Contributing

<div align="center">

**🎆 Help make HPone better!**

</div>

1. 🍴 **Fork** the project
2. 🌱 **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. 📝 **Commit** changes (`git commit -m 'Add amazing feature'`)
4. 🚀 **Push** to branch (`git push origin feature/amazing-feature`)
5. 📩 **Open** Pull Request

---

<div align="center">

## 📄 License

**HPone** is licensed under the **GNU General Public License v3.0** (GPL-3.0)
See the [`LICENSE`](LICENSE) file for details.

---

<p align="center">
  <strong>🍯 Made with ❤️ for cybersecurity enthusiasts</strong>
</p>

</div>
