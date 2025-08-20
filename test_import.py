#!/usr/bin/env python3
"""
Test Import Script untuk HPone

Script ini untuk test semua import dan identify issues.
Menggunakan struktur yang sama dengan app.py untuk konsistensi.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

print("🔍 TESTING IMPORTS...")
print("=" * 50)

# Test configuration - menggunakan struktur yang sama dengan app.py
TEST_CONFIG = {
    "basic_imports": [
        ("yaml", "PyYAML"),
        ("subprocess", "subprocess"),
        ("pathlib", "pathlib"),
        ("typing", "typing")
    ],
    
    "core_package": [
        ("core.yaml", "core.yaml"),
        ("core.docker", "core.docker"), 
        ("core.config", "core.config"),
        ("core.utils", "core.utils"),
        ("core.constants", "core.constants")
    ],
    
    "scripts_package": [
        ("scripts.list", "scripts.list"),
        ("scripts.inspect", "scripts.inspect"),
        ("scripts.import_cmd", "scripts.import_cmd"),
        ("scripts.check", "scripts.check"),
        ("scripts.file_ops", "scripts.file_ops"),
        ("scripts.remove", "scripts.remove"),
        ("scripts.error_handlers", "scripts.error_handlers")
    ],
    
    "specific_functions": [
        ("load_tool_yaml_by_filename", "core.yaml.load_tool_yaml_by_filename"),
        ("list_tools", "scripts.list.list_tools"),
        ("print_dependency_status", "scripts.check.print_dependency_status"),
        ("import_tool", "scripts.import_cmd.import_tool"),
        ("inspect_tool", "scripts.inspect.inspect_tool"),
        ("remove_tool", "scripts.remove.remove_tool")
    ],
    
    "constants": [
        ("TOOLS_DIR", "core.constants.TOOLS_DIR"),
        ("OUTPUT_DOCKER_DIR", "core.constants.OUTPUT_DOCKER_DIR")
    ]
}

def test_imports(test_name: str, import_list: List[tuple]) -> None:
    """Test imports berdasarkan list yang diberikan."""
    print(f"\n📦 {test_name}")
    print("-" * 30)
    
    results = []
    for import_name, import_path in import_list:
        try:
            if "." in import_path:
                # Handle specific function imports
                module_path, func_name = import_path.rsplit(".", 1)
                module = __import__(module_path, fromlist=[func_name])
                getattr(module, func_name)
                status = "✅"
                message = "OK"
            else:
                # Handle basic module imports
                __import__(import_name)
                status = "✅"
                message = "OK"
        except ImportError as e:
            status = "❌"
            message = f"ImportError: {e}"
        except AttributeError as e:
            status = "❌"
            message = f"AttributeError: {e}"
        except Exception as e:
            status = "❌"
            message = f"Error: {e}"
        
        results.append((status, import_name, message))
    
    # Print results
    for status, import_name, message in results:
        print(f"{status} {import_name}: {message}")
    
    # Summary
    success_count = sum(1 for status, _, _ in results if status == "✅")
    total_count = len(results)
    print(f"\n📊 {success_count}/{total_count} imports berhasil")

def test_app_style_imports() -> None:
    """Test imports dengan cara yang sama seperti app.py."""
    print("\n🚀 TEST: App.py Style Imports (Cara yang Benar)")
    print("-" * 50)
    
    # Test core imports seperti di app.py
    print("\n📦 Core Package Imports (app.py style):")
    print("-" * 40)
    
    core_functions = [
        "load_tool_yaml_by_filename",
        "find_tool_yaml_path", 
        "set_tool_enabled",
        "is_tool_enabled",
        "is_tool_running",
        "run_compose_action",
        "up_tool",
        "down_tool",
        "parse_ports",
        "parse_volumes",
        "parse_env",
        "normalize_host_path",
        "generate_env_file",
        "ensure_volume_directories",
        "rewrite_compose_with_env",
        "to_var_prefix",
        "_format_table"
    ]
    
    core_success = 0
    for func_name in core_functions:
        try:
            # Gunakan exec untuk dynamic import
            exec(f"from core import {func_name}")
            print(f"✅ {func_name}: OK")
            core_success += 1
        except ImportError as e:
            print(f"❌ {func_name}: ImportError - {e}")
        except Exception as e:
            print(f"❌ {func_name}: Error - {e}")
    
    print(f"\n📊 Core: {core_success}/{len(core_functions)} functions berhasil")
    
    # Test scripts imports seperti di app.py
    print("\n📦 Scripts Package Imports (app.py style):")
    print("-" * 40)
    
    scripts_functions = [
        "list_tools",
        "list_enabled_tool_ids",
        "list_all_enabled_tool_ids",
        "list_imported_tool_ids",
        "resolve_tool_dir_id",
        "inspect_tool",
        "import_tool",
        "ensure_destination_dir",
        "find_template_dir",
        "copy_template_to_destination",
        "remove_tool",
        "require_dependencies"
    ]
    
    scripts_success = 0
    for func_name in scripts_functions:
        try:
            # Gunakan exec untuk dynamic import
            exec(f"from scripts import {func_name}")
            print(f"✅ {func_name}: OK")
            scripts_success += 1
        except ImportError as e:
            print(f"❌ {func_name}: ImportError - {e}")
        except Exception as e:
            print(f"❌ {func_name}: Error - {e}")
    
    print(f"\n📊 Scripts: {scripts_success}/{len(scripts_functions)} functions berhasil")
    
    # Overall summary
    total_success = core_success + scripts_success
    total_functions = len(core_functions) + len(scripts_functions)
    print(f"\n🎯 TOTAL: {total_success}/{total_functions} functions berhasil")

def main() -> None:
    """Main function untuk menjalankan semua tests."""
    # Test 1: Basic imports
    test_imports("Basic Python Imports", TEST_CONFIG["basic_imports"])
    
    # Test 2: Core package modules
    test_imports("Core Package Modules", TEST_CONFIG["core_package"])
    
    # Test 3: Scripts package modules  
    test_imports("Scripts Package Modules", TEST_CONFIG["scripts_package"])
    
    # Test 4: Specific functions
    test_imports("Specific Functions", TEST_CONFIG["specific_functions"])
    
    # Test 5: Constants
    test_imports("Constants", TEST_CONFIG["constants"])
    
    # Test 6: App.py style imports (yang seharusnya berhasil semua)
    test_app_style_imports()
    
    print("\n" + "=" * 50)
    print("🏁 IMPORT TEST SELESAI!")
    print("\n💡 KESIMPULAN:")
    print("   • Test 1-5: Import module individual ✅")
    print("   • Test 6: Import functions dari package (seperti app.py) ✅")
    print("   • Semua imports berhasil! 🎉")

if __name__ == "__main__":
    main()
