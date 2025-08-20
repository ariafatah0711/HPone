# 🍯 HPone Honey Pot One

> **Advanced Docker Template Manager for Honeypot Deployment**

A powerful, modular Python application for managing Docker honeypot templates with an organized codebase structure. HPone simplifies the deployment, configuration, and management of various honeypot tools through a clean command-line interface.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [📚 Usage Guide](#-usage-guide)
- [🔧 Development](#-development)
- [🧪 Testing](#-testing)
- [🤝 Contributing](#-contributing)

## ✨ Features

- 🐳 **Docker Integration** - Seamless Docker Compose management
- 📁 **Template Management** - Import, configure, and deploy honeypot templates
- ⚙️ **Configuration Parsing** - Automatic YAML parsing and environment generation
- 🔄 **Lifecycle Management** - Start, stop, and monitor honeypot containers
- 📊 **Status Monitoring** - Real-time container status and health checks
- 🎯 **Modular Design** - Clean, maintainable codebase structure

## 🏗️ Architecture

### Project Structure
```
HPone/
├── 📁 core/                    # Core functionality modules
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration parsing utilities
│   ├── constants.py           # Application constants
│   ├── docker.py              # Docker operations
│   ├── utils.py               # Utility functions
│   └── yaml.py                # YAML file operations
├── 📁 scripts/                 # Command implementations
│   ├── __init__.py            # Package initialization
│   ├── check.py               # Dependency checking
│   ├── error_handlers.py      # Error handling utilities
│   ├── file_ops.py            # File operations
│   ├── import_cmd.py          # Import command logic
│   ├── inspect.py             # Inspection utilities
│   ├── list.py                # Listing commands
│   └── remove.py              # Removal operations
├── 📁 tools/                   # Honeypot tool configurations
│   ├── adbhoney.yml           # ADB honeypot config
│   ├── ciscoasa.yml           # Cisco ASA honeypot config
│   ├── conpot.yml             # Conpot honeypot config
│   └── cowrie.yml             # Cowrie SSH honeypot config
├── 📁 template/                # Docker template files
├── 📁 docker/                  # Generated Docker configurations
├── 🐍 app.py                   # Main application entry point
├── 📋 requirements.txt         # Python dependencies
└── 📖 README.md               # This file
```

### Core Modules

#### `core/` Package
- **`config.py`** - Configuration parsing and validation
- **`constants.py`** - Application-wide constants and paths
- **`docker.py`** - Docker container operations and management
- **`utils.py`** - General utility functions and helpers
- **`yaml.py`** - YAML file loading and manipulation

#### `scripts/` Package
- **`check.py`** - Dependency verification and system checks
- **`error_handlers.py`** - Centralized error handling
- **`file_ops.py`** - File and directory operations
- **`import_cmd.py`** - Template import functionality
- **`inspect.py`** - Tool inspection and information display
- **`list.py`** - Tool listing and status display
- **`remove.py`** - Tool removal and cleanup

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose
- Git

### Quick Install
```bash
# Clone the repository
git clone https://github.com/ariafatah0711/hpone.git
cd hpone

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python app.py --help
```

### Docker Installation
```bash
# Ensure Docker is running
docker --version
docker-compose --version

# Test Docker access
docker ps
```

## 🚀 Quick Start

### 1. List Available Tools
```bash
python app.py list
```

### 2. Import a Honeypot Tool
```bash
# Import Cowrie SSH honeypot
python app.py import cowrie

# Import all enabled tools
python app.py import --all
```

### 3. Start the Honeypot
```bash
# Start specific tool
python app.py up cowrie

# Start all imported tools
python app.py up --all
```

### 4. Monitor Status
```bash
# Check tool status
python app.py inspect cowrie

# List running tools
python app.py list -a
```

## 📚 Usage Guide

### Command Reference

#### 🔍 **List Commands**
```bash
# Basic tool listing
python app.py list

# Detailed listing with ports and descriptions
python app.py list -a
```

#### 📥 **Import Commands**
```bash
# Import specific tool
python app.py import <tool_name>

# Import all enabled tools
python app.py import --all

# Force overwrite existing import
python app.py import <tool_name> --force
```

#### 🚀 **Control Commands**
```bash
# Start tool
python app.py up <tool_name>

# Start all imported tools
python app.py up --all

# Stop tool
python app.py down <tool_name>

# Stop all tools
python app.py down --all
```

#### ⚙️ **Configuration Commands**
```bash
# Enable tool
python app.py enable <tool_name>

# Disable tool
python app.py disable <tool_name>

# Inspect tool configuration
python app.py inspect <tool_name>
```

#### 🗑️ **Management Commands**
```bash
# Remove specific tool
python app.py remove <tool_name>

# Remove all imported tools
python app.py remove --all

# Check system dependencies
python app.py check
```

### Tool Configuration

Each honeypot tool has a YAML configuration file in the `tools/` directory:

```yaml
# Example: tools/cowrie.yml
name: "Cowrie SSH Honeypot"
description: "Medium interaction SSH honeypot"
enabled: true
ports:
  - "2222:2222"
volumes:
  - "./logs:/cowrie/log"
environment:
  - COWRIE_LOG_LEVEL=INFO
```

## 🔧 Development

### Setting Up Development Environment
```bash
# Clone and setup
git clone https://github.com/yourusername/hpone.git
cd hpone

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .
```

### Code Structure Guidelines

#### 1. **Adding New Features**
- Place core functionality in `core/` package
- Place command implementations in `scripts/` package
- Update `__init__.py` files for proper exports
- Add comprehensive error handling

#### 2. **Modifying Existing Features**
- Maintain backward compatibility
- Update related tests and documentation
- Follow existing code style and patterns

#### 3. **Code Organization**
- Keep related functions together
- Use descriptive module and function names
- Maintain clear separation of concerns
- Document complex functions with docstrings

## 🧪 Testing

### Test Import Script
Use the included test script to verify all imports work correctly:

```bash
# Run comprehensive import test
python test_import.py
```

### Manual Testing
```bash
# Test basic functionality
python app.py list
python app.py check

# Test tool operations
python app.py import cowrie
python app.py inspect cowrie
python app.py remove cowrie
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 1. **Fork & Clone**
```bash
git clone https://github.com/yourusername/hpone.git
cd hpone
```

### 2. **Create Feature Branch**
```bash
git checkout -b feature/amazing-feature
```

### 3. **Make Changes**
- Follow existing code style
- Add tests for new functionality
- Update documentation

### 4. **Submit Pull Request**
- Describe your changes clearly
- Include test results
- Reference any related issues

### Development Workflow
1. **Plan** - Discuss changes in issues
2. **Code** - Implement with tests
3. **Test** - Ensure all tests pass
4. **Document** - Update README and docs
5. **Submit** - Create pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Honeypot Community** - For inspiration and feedback
- **Docker Team** - For excellent containerization tools
- **Python Community** - For amazing ecosystem and libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/hpone/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/hpone/discussions)
- **Wiki**: [Project Wiki](https://github.com/yourusername/hpone/wiki)

---

<div align="center">

**Made with ❤️ by ariafatah0711**

*Advanced Honeypot Management Made Simple*

</div>
