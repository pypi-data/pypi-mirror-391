import os
import streamlit.components.v1 as STcomponents

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = True


# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component = STcomponents.declare_component(
        # Set the name of your component.
        # Set the url to tell to Streamlit where the component is hosted for local dev.
        "streamlit_iiif_viewer",
        url="http://localhost:5173",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component = STcomponents.declare_component("streamlit_iiif_viewer", path=build_dir)


def iiif_viewer(
    viewer: str = "tify",
    manifest: dict | str = None,
    height: int = 800,
    options: dict = None,
    key: str = None,
):
    """Create a IIIF Viewer component.

    :param viewer: The IIIF viewer to use. Supported: Mirador, Tify.
    :type viewer: str
    :param manifest: The IIIF manifest to display. This can be either a URL (str)
        or a manifest object (dict).
    :type manifest: dict | str
    :param height: The height of the component in pixels.
    :type height: int
    :param options: A dict of options to pass to the viewer.
    :type options: dict
    :param key: An optional key that uniquely identifies this component.
    :type key: str
    :return: None
    :rtype: None
    """
    if isinstance(manifest, dict):
        payload = {"kind": "json", "value": manifest}
    elif isinstance(manifest, str):
        payload = {"kind": "url", "value": manifest}
    else:
        raise TypeError("manifest must be a dict or str")
    return _component(
        viewer=viewer,
        manifest=payload,
        options=options or {},
        height=height,
        key=key,
        default=None,
    )

## Test code
if not _RELEASE:
    import json
    import streamlit as st

    st.title("IIIF Viewer component — Test")

    viewer = st.selectbox("Viewer", ["tify", "mirador"], index=0)

    src = st.radio("Manifest source", ["URL", "Upload JSON", "Dict (JSON)"], index=0)

    height = st.number_input("Height (px)", 300, 1600, 600, step=50)

    placeholder_opts = (
        '{"language":"fr"}'
        if viewer == "tify"
        else '{"selectedTheme":"light", "language":"en"}'
    )
    options_text = st.text_area(
        "Viewer options (JSON)",
        value=placeholder_opts,
        height=120,
    )

    manifest = None

    if src == "URL":
        url = st.text_input(
            "IIIF Manifest URL",
            "https://iiif.io/api/cookbook/recipe/0009-book-1/manifest.json",
        )
        if url.strip():
            manifest = url

    elif src == "Upload JSON":
        up = st.file_uploader("Upload IIIF manifest (.json)", type=["json"])
        if up is not None:
            try:
                manifest = json.load(up)
            except Exception as e:
                st.error(f"Error loading JSON: {e}")

    elif src == "Dict (JSON)":
        dict_text = st.text_area(
            "IIIF Manifest (JSON)",
            value='{\n  "@context": "http://iiif.io/api/presentation/2/context.json",\n  "@type": "sc:Manifest",\n  "@id": "https://iiif.io/api/cookbook/recipe/0009-book-1/manifest.json"\n}',
            height=200,
        )
        try:
            manifest = json.loads(dict_text)
        except Exception as e:
            st.error(f"Error parsing JSON: {e}")

    if manifest:
        try:
            options = json.loads(options_text)
        except Exception as e:
            st.error(f"Error parsing options JSON: {e}")
            options = {}

        iiif_viewer(
            viewer=viewer,
            manifest=manifest,
            height=height,
            options=options,
        )