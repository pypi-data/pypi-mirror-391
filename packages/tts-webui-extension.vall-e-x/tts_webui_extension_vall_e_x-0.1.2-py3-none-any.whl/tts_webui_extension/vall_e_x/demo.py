import gradio as gr
from main import extension__tts_generation_webui

with gr.Blocks() as demo:
    extension__tts_generation_webui()

demo.launch()
