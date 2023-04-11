import setuptools
from pathlib import Path

version_path = Path(__file__).parent / "duplicate/__version__.py"
version_info = {}
exec(version_path.read_text(), version_info)
long_description = Path("README.md").read_text()
requirements = Path('requirements.txt').read_text().splitlines()
# pip install rich Send2Trash

setuptools.setup(
    name='duplicate',
    version=version_info['__version__'],
    author="streanger",
    description="files duplicate viewer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/streanger/duplicate",
    packages=['duplicate',],
    install_requires=requirements,
    include_package_data=True,
    package_data={},
    entry_points={
        "console_scripts": [
            "duplicate=duplicate:duplicate_entrypoint",
        ]
    },
)