from tts_webui.utils.manage_model_state import manage_model_state


def preprocess_text(text, language="auto"):
    from valle_x.utils.generation import (
        text_tokenizer,
        lang2token,
        langid,
    )

    language = get_lang(language)
    text = text.replace("\n", "").strip(" ")
    # detect language
    if language == "auto":
        language = langid.classify(text)[0]
    lang_token = lang2token[language]
    text = lang_token + text + lang_token
    return str(text_tokenizer.tokenize(text=f"_{text}".strip()))


@manage_model_state("valle_x")
def preload_models_if_needed(checkpoints_dir):
    from valle_x.utils.generation import preload_models

    preload_models(checkpoints_dir=checkpoints_dir)
    return "Loaded"  # workaround because preload_models returns None


def get_lang(language):
    from valle_x.utils.generation import langdropdown2token, token2lang

    lang = token2lang[langdropdown2token[language]]
    return lang if lang != "mix" else "auto"


def tts(text, prompt, language, accent, mode):
    from valle_x.utils.generation import (
        SAMPLE_RATE,
        generate_audio,
        generate_audio_from_long_text,
    )

    preload_models_if_needed("./data/models/vall-e-x/")
    lang = get_lang(language)

    prompt = prompt if prompt != "" else None
    generate_fn = generate_audio if mode == "short" else generate_audio_from_long_text
    audio_array = generate_fn(
        text=text,
        prompt=prompt,
        language=lang,
        accent=accent,
        **({"mode": mode} if mode != "short" else {}),
    )
    return {"audio_out": (SAMPLE_RATE, audio_array)}
