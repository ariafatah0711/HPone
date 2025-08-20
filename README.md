# HPone Docker Template Manager - Modular Version

Aplikasi modular yang menggunakan helpers package untuk mengelola Docker templates dengan struktur kode yang lebih terorganisir.

## 🏗️ Struktur Modular

```
HPone/
├── manage.py              # File original (tidak dihapus)
├── app.py                 # File baru yang modular
├── helpers/               # Package helpers
│   ├── __init__.py        # Package initialization
│   ├── yaml_helpers.py    # YAML file management
│   ├── docker_helpers.py  # Docker container operations
│   ├── file_helpers.py    # File and directory operations
│   ├── config_helpers.py  # Configuration parsing
│   ├── list_helpers.py    # Tool listing functions
│   ├── utils.py           # Utility functions
│   ├── display_helpers.py # Output display functions
│   └── import_helpers.py  # Tool import functions
├── tools/                 # Tool configurations
├── template/              # Docker templates
└── docker/                # Generated Docker files
```

## 📦 Helpers Package

### `yaml_helpers.py`
- **`load_tool_yaml_by_filename()`** - Load YAML config berdasarkan nama file atau field `name`
- **`find_tool_yaml_path()`** - Temukan path YAML untuk tool ID
- **`set_tool_enabled()`** - Set field `enabled` pada YAML
- **`is_tool_enabled()`** - Check apakah tool enabled

### `docker_helpers.py`
- **`is_tool_running()`** - Check status Docker container
- **`run_compose_action()`** - Jalankan docker compose command
- **`up_tool()`** - Start tool container
- **`down_tool()`** - Stop tool container

### `file_helpers.py`
- **`ensure_destination_dir()`** - Buat direktori tujuan
- **`find_template_dir()`** - Temukan direktori template
- **`copy_template_to_destination()`** - Copy template ke direktori tujuan
- **`remove_tool()`** - Hapus direktori tool

### `config_helpers.py`
- **`parse_ports()`** - Parse konfigurasi ports
- **`parse_volumes()`** - Parse konfigurasi volumes
- **`parse_env()`** - Parse environment variables
- **`normalize_host_path()`** - Normalisasi path host
- **`generate_env_file()`** - Generate file .env
- **`ensure_volume_directories()`** - Buat direktori volume
- **`rewrite_compose_with_env()`** - Rewrite docker-compose.yml

### `list_helpers.py`
- **`list_enabled_tool_ids()`** - List tool yang enabled dan imported
- **`list_all_enabled_tool_ids()`** - List semua tool yang enabled
- **`list_imported_tool_ids()`** - List tool yang sudah diimport
- **`resolve_tool_dir_id()`** - Resolve tool directory ID

### `utils.py`
- **`to_var_prefix()`** - Konversi nama tool ke prefix ENV
- **`_format_table()`** - Format output table

### `display_helpers.py`
- **`list_tools()`** - Tampilkan daftar tools
- **`inspect_tool()`** - Tampilkan detail tool

### `import_helpers.py`
- **`import_tool()`** - Import template tool

## 🚀 Cara Penggunaan

### 1. Menggunakan `app.py` (Modular)
```bash
# Import tool
python app.py import cowrie
python app.py import --all

# List tools
python app.py list
python app.py list -a

# Inspect tool
python app.py inspect cowrie

# Remove tool
python app.py remove cowrie
python app.py remove --all

# Enable/Disable tool
python app.py enable cowrie
python app.py disable cowrie

# Start/Stop tool
python app.py up cowrie
python app.py up --all
python app.py down cowrie
python app.py down --all
```

### 2. Menggunakan `manage.py` (Original)
```bash
# Semua command yang sama seperti sebelumnya
python manage.py import cowrie
python manage.py list -a
python manage.py inspect cowrie
# dst...
```

## 🔧 Keuntungan Struktur Modular

### ✅ **Maintainability**
- Kode terorganisir dalam modul yang spesifik
- Mudah menemukan dan memperbaiki bug
- Fungsi-fungsi yang terkait dikelompokkan bersama

### ✅ **Reusability**
- Helper functions bisa digunakan di file lain
- Tidak ada duplikasi kode
- Mudah untuk testing individual modules

### ✅ **Scalability**
- Mudah menambah fitur baru
- Mudah memodifikasi existing functionality
- Struktur yang jelas untuk development team

### ✅ **Testing**
- Bisa test individual modules
- Mock dependencies dengan mudah
- Unit testing yang lebih efektif

## 🧪 Testing

```bash
# Test individual modules
python -m pytest helpers/yaml_helpers.py
python -m pytest helpers/docker_helpers.py

# Test specific functions
python -c "from helpers.yaml_helpers import is_tool_enabled; print(is_tool_enabled('cowrie'))"
```

## 🔄 Migration

### Dari `manage.py` ke `app.py`
1. **Kedua file bisa digunakan bersamaan**
2. **Fungsi yang sama persis**
3. **Tidak ada breaking changes**
4. **Bisa migrate secara bertahap**

### Contoh Migration
```python
# Sebelum (manage.py)
from manage import list_tools, import_tool

# Sesudah (app.py)
from helpers import list_tools, import_tool
# atau
from app import list_tools, import_tool
```

## 📝 Development Guidelines

### 1. **Adding New Features**
- Buat helper function di module yang sesuai
- Update `__init__.py` untuk export function
- Test function secara individual
- Integrate ke `app.py`

### 2. **Modifying Existing Features**
- Edit helper function yang sesuai
- Update tests jika ada
- Test integration dengan `app.py`

### 3. **Code Organization**
- Keep related functions together
- Use descriptive module names
- Maintain clear separation of concerns
- Document complex functions

## 🎯 Next Steps

1. **Add Unit Tests** untuk setiap helper module
2. **Add Type Hints** yang lebih comprehensive
3. **Add Logging** untuk debugging
4. **Add Configuration Management** untuk settings
5. **Add Plugin System** untuk extensibility

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add/modify helpers sesuai kebutuhan
4. Update `__init__.py` exports
5. Test dengan `app.py`
6. Submit pull request

---

**Note**: File `manage.py` original tetap dipertahankan untuk backward compatibility. Semua fitur yang ada di `manage.py` tersedia di `app.py` dengan struktur yang lebih modular.
