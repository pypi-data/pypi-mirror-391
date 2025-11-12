import streamlit as st

from st_zoom_buttons import st_zoom_buttons

st.title("Zoom buttons")


for font_size in range(10, 20):
    st.write(f"Font size {font_size}")
    clicked_button = st_zoom_buttons(key=f"szb-br0-{font_size}", font_size=f"{font_size}px")
    st.write(f"Clicked: {clicked_button}")
    clicked_button = st_zoom_buttons(key=f"szb-br8-{font_size}", border_radius=12, font_size=f"{font_size}px")
    st.write(f"Clicked: {clicked_button}")

st.subheader("Disabling buttons")
font_size = 20
clicked_button = st_zoom_buttons(
    key=f"szb-br0-dis-{font_size}", border_radius=12, font_size=f"{font_size}px", disabled=["zoom_reset"]
)
st.write(f"Clicked: {clicked_button}")

st_zoom_buttons(
    key=f"szb-br0-disabled-all-{font_size}",
    border_radius=12,
    font_size=f"{font_size}px",
    disabled=["zoom_reset", "zoom_in", "zoom_out"],
)
