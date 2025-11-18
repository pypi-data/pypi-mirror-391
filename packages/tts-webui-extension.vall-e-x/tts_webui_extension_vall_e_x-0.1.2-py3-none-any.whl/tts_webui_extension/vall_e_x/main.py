import gradio as gr

from tts_webui.decorators.gradio_dict_decorator import dictionarize
from tts_webui.utils.randomize_seed import randomize_seed_ui
from tts_webui.utils.list_dir_models import unload_model_button
from tts_webui.decorators.decorator_apply_torch_seed import decorator_apply_torch_seed
from tts_webui.decorators.decorator_log_generation import decorator_log_generation
from tts_webui.decorators.decorator_save_metadata import decorator_save_metadata
from tts_webui.decorators.decorator_save_wav import decorator_save_wav
from tts_webui.decorators.decorator_add_base_filename import decorator_add_base_filename
from tts_webui.decorators.decorator_add_date import decorator_add_date
from tts_webui.decorators.decorator_add_model_type import decorator_add_model_type
from tts_webui.decorators.log_function_time import log_function_time
from tts_webui.extensions_loader.decorator_extensions import (
    decorator_extension_outer,
    decorator_extension_inner,
)

from .api import tts, preprocess_text


@decorator_extension_outer
@decorator_apply_torch_seed
@decorator_save_metadata
@decorator_save_wav
@decorator_add_model_type("valle_x")
@decorator_add_base_filename
@decorator_add_date
@decorator_log_generation
@decorator_extension_inner
@log_function_time
def generate_audio_gradio(text, prompt, language, accent, mode, **kwargs):
    return tts(text=text, prompt=prompt, language=language, accent=accent, mode=mode)


def split_text_into_sentences(text):
    from valle_x.utils.sentence_cutter import split_text_into_sentences

    return "###\n".join(split_text_into_sentences(text))


def ui():
    gr.Markdown(f"# Vall-E-X")
    gr.Markdown(
        """
    Multilingual text-to-speech model supporting English, Chinese, and Japanese
    """
    )
    with gr.Row():
        inner_ui()


def inner_ui():
    with gr.Column():
        text = gr.Textbox(label="Text", lines=3, placeholder="Enter text here...")
        generate_button = gr.Button("Generate", variant="primary")
        prompt = gr.Textbox(label="Prompt", visible=False, value="")

        with gr.Accordion("Analyze text", open=False):
            split_text_into_sentences_button = gr.Button("Preview sentences")
            split_text = gr.Textbox(label="Text after split")

            split_text_into_sentences_button.click(
                fn=split_text_into_sentences,
                inputs=[text],
                outputs=[split_text],
                api_name="vall_e_x_split_text_into_sentences",
            )

            split_text_into_tokens_button = gr.Button("Preview tokens")
            tokens = gr.Textbox(label="Tokens")

        gr.Markdown(
            """
            For longer audio generation, two extension modes are available:

            - (Default) short: This will only generate as long as the model's context length.
            - fixed-prompt: This mode will keep using the same prompt the user has provided, and generate audio sentence by sentence.
            - sliding-window: This mode will use the last sentence as the prompt for the next sentence, but has some concern on speaker maintenance.
        """
        )
        with gr.Row():
            language = gr.Radio(
                ["English", "中文", "日本語", "Mix"],
                label="Language",
                value="Mix",
            )

            accent = gr.Radio(
                ["English", "中文", "日本語", "no-accent"],
                label="Accent",
                value="no-accent",
            )

            mode = gr.Radio(
                ["short", "fixed-prompt", "sliding-window"],
                label="Mode",
                value="short",
            )

        seed, randomize_seed_callback = randomize_seed_ui()
        unload_model_button("valle_x")

    with gr.Column():
        audio_out = gr.Audio(label="Generated audio")

        split_text_into_tokens_button.click(
            fn=preprocess_text,
            inputs=[text, language],
            outputs=[tokens],
            api_name="vall_e_x_tokenize",
        )

        input_dict = {
            text: "text",
            prompt: "prompt",
            language: "language",
            accent: "accent",
            mode: "mode",
            seed: "seed",
        }

        output_dict = {
            "audio_out": audio_out,
            "metadata": gr.JSON(visible=False),
            "folder_root": gr.Textbox(visible=False),
        }

        generate_button.click(
            **randomize_seed_callback,
        ).then(
            **dictionarize(
                fn=generate_audio_gradio,
                inputs=input_dict,
                outputs=output_dict,
            ),
            api_name="vall_e_x_generate",
        )


def extension__tts_generation_webui():
    ui()
    return {
        "package_name": "extension_vall_e_x",
        "name": "Vall-E-X",
        "requirements": "git+https://github.com/rsxdalv/extension_vall_e_x@main",
        "description": "Multilingual text-to-speech model supporting English, Chinese, and Japanese",
        "extension_type": "interface",
        "extension_class": "text-to-speech",
        "author": "Plachtaa",
        "extension_author": "rsxdalv",
        "license": "MIT",
        "website": "https://github.com/Plachtaa/VALL-E-X",
        "extension_website": "https://github.com/rsxdalv/extension_vall_e_x",
        "extension_platform_version": "0.0.1",
    }


if __name__ == "__main__":
    if "demo" in locals():
        locals()["demo"].close()
    with gr.Blocks() as demo:
        ui()
    demo.launch(
        server_port=7771,
    )
