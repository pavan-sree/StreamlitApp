import streamlit as st
import base64

def get_base64_of_audio(audio_file):
    with open(audio_file, 'rb') as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode('utf-8')
sound_file = 'bell.mp3'
error_file = 'error.mp3'
move_file = 'tap.mp3' 

