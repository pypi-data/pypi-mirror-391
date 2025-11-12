from os.path import (dirname,
                     join)
import setuptools

def readme() -> str:
    """Utility function to read the README file.
    :return: content of README.md
    :rtype: str
    """
    return open(join(dirname(__file__), "README.md")).read()

setuptools.setup(
    name="streamlit-iiif-viewer",
    version="0.0.3",
    author="Lucas Terriel",
    author_email="contact@lterriel.com",
    description="A Streamlit component for show IIIF viewers.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="",
    license="MIT",
    keywords="streamlit-component streamlit iiif viewer",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.9",
    install_requires=[
        "streamlit >= 1.34.0",
    ],
)
