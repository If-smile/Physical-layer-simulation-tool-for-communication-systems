"""Validate the contents and metadata of built release archives."""

from __future__ import annotations

import argparse
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path, PurePosixPath

from pyberlab import __version__

PROJECT_NAME = "pyberlab"
EXPECTED_URLS = {
    "Changelog",
    "Documentation",
    "Homepage",
    "Issues",
    "Repository",
}
EXPECTED_DEPENDENCIES = {"matplotlib", "numpy", "scipy"}


def require(condition: bool, message: str) -> None:
    """Raise a readable validation error when *condition* is false."""
    if not condition:
        raise RuntimeError(message)


def single_match(paths: list[Path], label: str) -> Path:
    """Return the only matching archive or raise an error."""
    require(len(paths) == 1, f"expected one {label}, found {len(paths)}")
    return paths[0]


def validate_metadata(metadata_text: str) -> None:
    """Check core metadata fields rendered by the build backend."""
    metadata = Parser().parsestr(metadata_text)
    require(metadata["Name"] == PROJECT_NAME, "unexpected distribution name")
    require(metadata["Version"] == __version__, "distribution version mismatch")
    require(metadata["Requires-Python"] == ">=3.9", "unexpected Python requirement")
    require(metadata["License-Expression"] == "MIT", "missing SPDX license")
    require(
        metadata["Description-Content-Type"] == "text/markdown",
        "README is not marked as Markdown",
    )

    url_labels = {
        value.split(",", maxsplit=1)[0]
        for value in metadata.get_all("Project-URL", [])
    }
    require(url_labels == EXPECTED_URLS, "project URL metadata is incomplete")

    requirements = {
        value.split(" ", maxsplit=1)[0].split(">", maxsplit=1)[0]
        for value in metadata.get_all("Requires-Dist", [])
        if "; extra ==" not in value
    }
    require(
        EXPECTED_DEPENDENCIES <= requirements,
        "runtime dependency metadata is incomplete",
    )


def validate_wheel(path: Path) -> None:
    """Validate wheel layout and embedded core metadata."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        require(len(metadata_names) == 1, "wheel must contain one METADATA file")
        validate_metadata(archive.read(metadata_names[0]).decode("utf-8"))

        require("pyberlab/__init__.py" in names, "wheel is missing pyberlab")
        require(
            any(name.endswith(".dist-info/licenses/LICENSE") for name in names),
            "wheel is missing its license file",
        )
        unexpected = ("docs/", "examples/", "scripts/", "tests/")
        require(
            not any(name.startswith(unexpected) for name in names),
            "wheel contains development-only top-level files",
        )


def validate_sdist(path: Path) -> None:
    """Validate source archive layout and embedded core metadata."""
    root = f"{PROJECT_NAME}-{__version__}"
    required = {
        "CHANGELOG.md",
        "LICENSE",
        "MANIFEST.in",
        "README.md",
        "docs/index.rst",
        f"docs/releases/{__version__}.rst",
        "examples/bpsk_awgn.ipynb",
        "pyberlab/__init__.py",
        "pyproject.toml",
        "scripts/release_smoke_test.py",
        "tests/test_simulation.py",
    }

    with tarfile.open(path, "r:gz") as archive:
        names = {PurePosixPath(name).as_posix() for name in archive.getnames()}
        missing = {name for name in required if f"{root}/{name}" not in names}
        require(not missing, f"sdist is missing files: {sorted(missing)}")

        metadata_name = f"{root}/PKG-INFO"
        require(metadata_name in names, "sdist is missing PKG-INFO")
        metadata_file = archive.extractfile(metadata_name)
        require(metadata_file is not None, "could not read sdist metadata")
        validate_metadata(metadata_file.read().decode("utf-8"))


def main() -> None:
    """Validate exactly one wheel and one source distribution."""
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path, help="directory containing archives")
    args = parser.parse_args()

    wheel = single_match(sorted(args.directory.glob("*.whl")), "wheel")
    sdist = single_match(sorted(args.directory.glob("*.tar.gz")), "sdist")
    require(__version__ in wheel.name, "wheel filename does not contain version")
    require(__version__ in sdist.name, "sdist filename does not contain version")

    validate_wheel(wheel)
    validate_sdist(sdist)
    print(f"Validated {wheel.name} and {sdist.name}")


if __name__ == "__main__":
    main()
