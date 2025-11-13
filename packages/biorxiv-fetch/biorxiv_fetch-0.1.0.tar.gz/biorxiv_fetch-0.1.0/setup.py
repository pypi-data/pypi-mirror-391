from pathlib import Path
from setuptools import setup, find_packages


HERE = Path(__file__).parent
readme_path = HERE / "README.md"
requirements_path = HERE / "requirements.txt"
license_path = HERE / "LICENSE"

long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

install_requires = []
if requirements_path.exists():
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        install_requires.append(line)

setup(
    name="biorxiv-fetch",
    version="0.1.0",
    description="Fetch bioRxiv MECA archives by DOI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src", exclude=("tests", "notebooks")),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.8",
    license="MIT",
    license_files=["LICENSE"] if license_path.exists() else None,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


