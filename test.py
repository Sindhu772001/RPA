import os

def create_folders_and_files(base_dir):
    """
    Creates the folder structure and empty placeholder files for the project.
    """
    # Define folder structure
    folders = [
        f"{base_dir}/app",
        f"{base_dir}/app/api",
        f"{base_dir}/app/core",
        f"{base_dir}/app/services",
        f"{base_dir}/app/utils",
        f"{base_dir}/tracking_scripts",
        f"{base_dir}/tests",
    ]

    # Define files with initial content
    files = {
        f"{base_dir}/app/__init__.py": "",
        f"{base_dir}/app/main.py": "",
        f"{base_dir}/app/api/__init__.py": "",
        f"{base_dir}/app/api/routes.py": "",
        f"{base_dir}/app/api/schemas.py": "",
        f"{base_dir}/app/core/__init__.py": "",
        f"{base_dir}/app/core/config.py": "",
        f"{base_dir}/app/services/__init__.py": "",
        f"{base_dir}/app/services/tracking_service.py": "",
        f"{base_dir}/app/utils/__init__.py": "",
        f"{base_dir}/app/utils/logger.py": "",
        f"{base_dir}/tracking_scripts/.gitkeep": "",  # Use .gitkeep to track empty folders in Git
        f"{base_dir}/tests/__init__.py": "",
        f"{base_dir}/tests/test_main.py": "",
        f"{base_dir}/tests/test_services.py": "",
        f"{base_dir}/.env": "# Environment variables\n",
        f"{base_dir}/requirements.txt": "# List of dependencies\n",
        f"{base_dir}/Dockerfile": "# Docker configuration\n",
        f"{base_dir}/docker-compose.yml": "# Docker Compose configuration\n",
        f"{base_dir}/README.md": "# Project Documentation\n",
        f"{base_dir}/.gitignore": "__pycache__/\n.env\n*.pyc\n.DS_Store\n",
    }

    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Create files with initial content
    for file_path, content in files.items():
        with open(file_path, "w") as file:
            file.write(content)

if __name__ == "__main__":
    # Define the base directory for the project
    base_directory = "./"
    create_folders_and_files(base_directory)
    print(f"Project structure created successfully in '{base_directory}'")
