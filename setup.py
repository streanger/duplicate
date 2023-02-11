import setuptools
from duplicate.__version__ import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='duplicate',
    version=__version__,
    author="streanger",
    description="files duplicate viewer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/streanger/duplicate",
    packages=['duplicate',],
    install_requires=['rich', 'Send2Trash'],
    include_package_data=True,
    package_data={},
    entry_points={
        "console_scripts": [
            "duplicate=duplicate:duplicate_entrypoint",
        ]
    },
)
