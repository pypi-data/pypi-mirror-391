import os
import tarfile
from pathlib import Path


def create_server_config_templates_archive():
    """Create a compressed archive of server config template files during package installation."""
    templates_dir = Path(".server-config")
    if not templates_dir.exists():
        print("Templates directory not found, skipping archive creation")
        return

    archive_name = "server-config.tar.gz"
    with tarfile.open(archive_name, "w:gz") as tar:
        # Add each directory in .server-config to the archive
        for item in templates_dir.iterdir():
            if item.is_dir():
                tar.add(item, arcname=item.name)

    # Move the archive to the artefacts directory
    archive_dir = Path("source/artefacts")
    archive_dir.mkdir(exist_ok=True)
    os.rename(archive_name, archive_dir / archive_name)
    print(f"✓ Created archive: {archive_dir / archive_name}")


# Poetry build hook - runs before build
def build(setup_kwargs=None):
    """Poetry build hook that runs before packaging.
    
    This is called by Poetry's build system when [tool.poetry.build] script is configured.
    We create the server config archive before the package is built so it's included.
    
    Args:
        setup_kwargs: Optional dictionary that can be modified (for setuptools compatibility)
    """
    print("🔨 Running Poetry build hook...")
    create_server_config_templates_archive()


if __name__ == "__main__":
    create_server_config_templates_archive()
