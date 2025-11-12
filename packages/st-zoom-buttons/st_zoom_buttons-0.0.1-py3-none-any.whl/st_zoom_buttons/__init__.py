import os

import streamlit.components.v1 as components

_RELEASE = True

if os.getenv("_ST_ZOOM_BUTTONS_NOT_RELEASE_"):
    _RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "zoom_buttons",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_zoom_buttons", path=build_dir)


def st_zoom_buttons(
    key=None,
    font_size="10px",
    width="35px",
    border_radius: int = 0,
    disabled: list[str] | None = None,
):
    """Create a new instance of "zoom_buttons".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    font_size: str
        The font size of the buttons.
    width: str
        The width of the buttons.
    border_radius: int - buttons border radius in pixels
    disabled: list - list of buttons to disable, possible values are: zoom_out, zoom_reset, zoom_in
    Returns
    -------
    str
        Value of the key that been pressed.
        Values are: zoom_out, zoom_reset, zoom_in
        This is the value passed to `Streamlit.setComponentValue` on the
        frontend.



    """
    if disabled is None:
        disabled = []

    component_value = _component_func(
        key=key,
        font_size=font_size,
        width=width,
        border_radius=border_radius,
        disabled=disabled,
        default=None,
    )

    return component_value
