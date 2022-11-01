import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='duplicate',
    version='0.1.0',
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
            "duplicate=duplicate:gui",
        ]
    },
)
