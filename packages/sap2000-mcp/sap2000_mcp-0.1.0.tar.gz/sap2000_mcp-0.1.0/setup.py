from setuptools import setup, find_packages
from pathlib import Path
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="sap2000-mcp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["mcp>=1.0.0", "comtypes>=1.4.0"],
    entry_points={
        "console_scripts": ["sap2000-mcp=sap2000_mcp.server:main"],
    },
    python_requires=">=3.10",
    author="Kazem",
    description="Minimal MCP server to operate SAP2000 from AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    license_files=["LICENSE"],
)
