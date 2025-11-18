import gradio as gr
from .magnet.magnet_tab import magnet_tab
from .musicgen.musicgen_tab import musicgen_tab


def ui():
    magnet_tab()
    musicgen_tab()


def extension__tts_generation_webui():
    ui()
    
    return {
        "package_name": "extension_audiocraft",
        "name": "Audiocraft",
        "requirements": "git+https://github.com/rsxdalv/extension_audiocraft@main",
        "description": "Audiocraft provides MusicGen and MAGNeT models for high-quality music and audio generation",
        "extension_type": "interface",
        "extension_class": "audio-music-generation",
        "author": "Facebook",
        "extension_author": "rsxdalv",
        "license": "MIT",
        "website": "https://github.com/facebookresearch/audiocraft",
        "extension_website": "https://github.com/rsxdalv/extension_audiocraft",
        "extension_platform_version": "0.0.1",
    }


if __name__ == "__main__":
    if "demo" in locals():
        demo.close()  # type: ignore
    with gr.Blocks() as demo:
        ui()

    demo.launch(
        server_port=7771,
    )
