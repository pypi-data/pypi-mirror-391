
""" 文件工具 """
import importlib
import yaml


def load_inpackage_file(package_name: str, file_name: str, file_type="yaml"):
    """load config"""
    with importlib.resources.open_text(package_name, file_name) as f:
        if file_type == "yaml":
            return yaml.safe_load(f)
        else:
            return f.read()

import toml

def get_pyproject_toml():
    # 从文件读取
    try:
        with open('pyproject.toml', 'r', encoding='utf-8') as f:
            data = toml.load(f)
        print("--- Loaded TOML data ---")
        print(data)
        print("\n--- Accessing data ---")
        print(f"Project name: {data['project']['name']}")
        print(f"Dependencies: {data['project']['dependencies']}")
        print(f"UV cache dir: {data['tool']['uv']['cache-dir']}")
        print(f"Lint check imports: {data['tool']['lint']['check-imports']}")

    except FileNotFoundError:
        print("pyproject.toml not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # 从字符串读取
    toml_string = """
    [user]
    name = "Alice"
    age = 30
    is_active = true
    """
    parsed_string_data = toml.loads(toml_string)
    print("\n--- Parsed string data ---")
    print(parsed_string_data)
    print(f"User name: {parsed_string_data['user']['name']}")