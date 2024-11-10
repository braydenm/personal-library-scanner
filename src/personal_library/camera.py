# src/personal_library/camera.py
import streamlit as st

def camera_input():
    """Simplest possible camera implementation"""
    img_file_buffer = st.camera_input("Take a picture")

    if img_file_buffer is not None:
        # Return the image in a format we can use
        return img_file_buffer

    return None
