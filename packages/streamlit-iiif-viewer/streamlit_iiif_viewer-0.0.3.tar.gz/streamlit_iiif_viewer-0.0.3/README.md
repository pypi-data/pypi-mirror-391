# Streamlit IIIF viewer

[![Supported Python versions](https://img.shields.io/pypi/pyversions/pypistats.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/streamlit-iiif-viewer/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Code style: Black](https://img.shields.io/badge/code%20style-Black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/streamlit-iiif-viewer)](https://pypi.org/project/streamlit-iiif-viewer/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/streamlit-iiif-viewer)](https://pypi.org/project/streamlit-iiif-viewer/)


Streamlit component for fast <img src="./assets/iiif.png" width="25px"> viewers integration.

[IIIF](https://iiif.io/) (International Image Interoperability Framework) is a set of open standards for delivering
high-quality images and metadata over the web.
It is widely used in digital humanities and by cultural heritage institutions (but not only!) to share, annotate, and
study digitized materials.

Currently, this component supports the following IIIF-compliant viewers:

- [Mirador](https://projectmirador.org/) (Apache-2.0 License)
- [Tify](https://tify.rocks/) (GNU Affero General Public License v3.0)

## Features

- Display IIIF v3 manifests
- port for document-focused viewer (e.g. Tify) and multi-window scholarly viewer (e.g. Mirador)
- Accepts either a remote manifest URL or a local JSON object
- Optional viewers configuration via options (language, theme, default window settings, etc.)
- Automatically resizes within the Streamlit layout
- Works seamlessly with Python dict IIIF manifests generated in the app

## Installation

```bash
pip install streamlit-iiif-viewer
```

## Quickstart

Display a remote manifest

```python
import streamlit as st
from streamlit_iiif_viewer import iiif_viewer

st.title("My IIIF Viewer (remote)")

manifest_url = "https://iiif.io/api/cookbook/recipe/0009-book-1/manifest.json"

iiif_viewer(
    viewer="tify",  # or any IIIF viewers available like "mirador"
    manifest=manifest_url,
    height=800,
    options={"language": "fr"},  # optional viewer configuration
)
```

Display a local JSON manifest

```python
import streamlit as st
from streamlit_iiif_viewer import iiif_viewer

st.title("My IIIF Viewer (local)")

manifest = {
    "@context": "http://iiif.io/api/presentation/3/context.json",
    "id": "https://example.org/manifest/demo",
    "type": "Manifest",
    "label": {"en": ["Local Demo"]},
    "items": [],
}

iiif_viewer(
    viewer="tify",  # or any IIIF viewers available like "mirador"
    manifest=manifest,
    height=700,
)
```

## Viewer Configuration

You can customize the behavior of each viewer using the options argument.
Full configuration guides are available in the official documentation:

- [Mirador Configuration](https://github.com/ProjectMirador/mirador/wiki)
- [Tify Configuration](https://github.com/tify-iiif-viewer/tify#configuration)

> [!IMPORTANT]  
> For now, Mirador plugins like text-overlay or image-tools are not includes.

### Tify Example

```python
options = {
    "language": "de",
    "pageLabelFormat": "P (L)",
    "pages": [2, 3],
    "pan": {"x": ".45", "y": " .6"},
    "zoom": "1.2"
}
```

### Mirador Example

```python
options = {
"selectedTheme":"dark",
"language":"fr",
  "workspace": {
    "type": "mosaic"
  },
  "workspaceControlPanel": {
    "enabled": true
  },
  "theme": {
    "palette": {
      "type": "light"
    }
  }
}
```

## Development

> [!NOTE] 
> These steps are required for development purposes or to modify the component code only.

1. Clone this repository:

``` bash
git clone 
cd streamlit_iiif_viewer
```

2. Install the Python dependencies:

```bash
# create a virtual environment
python3.11 -m venv .venv
# activate it
. .venv/bin/activate
# install dependencies
pip3 install -r requirements.txt
```

3. Install frontend dependencies

```bash
cd streamlit_iiif_viewer/frontend
yarn install
npm install mirador # sometimes needed to explicitly install mirador (for build)
```

4. Making changes

To make changes, first go to `streamlit_iiif_viewer/__init__.py` and make sure the
variable `_RELEASE` is set to `False`. This will make the component use the local
version of the frontend code, and not the built project.

Then start the dev server for frontend: 

```bash
cd streamlit_iiif_viewer/frontend/
yarn dev
```
this start VITE server at `http://localhost:5173/`.

Open another terminal and run the Streamlit app to test the component:

```bash
cd streamlit_iiif_viewer/
streamlit run __init__.py
```

## References

#### Specific IIIF References

- IIIF Presentation API v3 – https://iiif.io/api/presentation/3.0/
- IIIF Cookbook (example manifests) – https://iiif.io/api/cookbook/

This template is based on these canvas/example projects:

- [streamlit-component-vue-vite-template](https://github.com/gabrieltempass/streamlit-component-vue-vite-template)
- [streamlit-drawable-canvas](https://github.com/andfanilo/streamlit-drawable-canvas)
- [streamlit-calendar](https://github.com/im-perativa/streamlit-calendar/tree/master)

and streamlit documentation:

- Streamlit Components – https://docs.streamlit.io/library/components

