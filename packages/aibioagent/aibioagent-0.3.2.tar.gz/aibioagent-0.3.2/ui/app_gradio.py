"""
app_gradio.py
--------------
Gradio front-end that plugs into the Router for multi-agent orchestration.
- Input textbox on the LEFT
- Image drop + PDF drop on the RIGHT
- Shows the user's message instantly, then streams the final response
- Keeps per-session memory via a session_id passed into Router

Run:
    python app_gradio.py

Requirements:
    pip install gradio Pillow

Notes:
- This file expects your project modules (router, agents, core, config, etc.)
  to be importable in PYTHONPATH. If you launch from project root it should work.
"""

from __future__ import annotations
import os
import uuid
import tempfile
from typing import Generator, List, Tuple, Optional

# UI
import gradio as gr
from PIL import Image

# --- App wiring: import your Router -------------------------------
try:
    # If router.py is in the same directory as this file
    from core.router import Router  # type: ignore
except Exception as e:
    Router = None  # type: ignore
    _router_import_error = e
else:
    _router_import_error = None


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------

def _ensure_router() -> "Router":
    """Create a Router instance or raise a helpful error if import failed."""
    if Router is None:
        raise ImportError(
            "Could not import Router from router.py. Original error: "
            f"{repr(_router_import_error)}\n"
            "Make sure router.py and its dependencies (core.*, agents.*, config.*) "
            "are importable (check PYTHONPATH and your working directory)."
        )
    return Router()


def _maybe_save_image(pil_img: Optional[Image.Image]) -> Optional[str]:
    """Save PIL image to a temp path and return the path, or None if no image."""
    if pil_img is None:
        return None
    os.makedirs("./.gradio_uploads", exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        dir="./.gradio_uploads", delete=False, suffix=".png"
    )
    pil_img.save(tmp.name)
    tmp.close()
    return tmp.name


def _maybe_file_path(f) -> Optional[str]:
    """Try to extract a real filesystem path from a Gradio File value."""
    if f is None:
        return None
    # gr.File can return a str (path), a dict with 'name', or an object with .name
    if isinstance(f, str):
        return f
    if isinstance(f, dict) and "name" in f:
        return f["name"]
    try:
        return f.name  # type: ignore[attr-defined]
    except Exception:
        return None


# ---------------------------------------------------------------
# Core chat function (generator so the UI updates instantly)
# ---------------------------------------------------------------

def chat_fn(
    message: str,
    image: Optional[Image.Image],
    pdf_file,
    history: List[Tuple[str, str]],
    session_id: str,
) -> Generator[List[Tuple[str, str]], None, None]:
    """
    Gradio event handler for sending a message.
    Yields twice:
      1) Immediately show the user's message
      2) After routing finishes, show the assistant response
    """
    # 1) Echo user message instantly
    history = history + [(message, None)]
    yield history

    # 2) Route + respond
    try:
        router = _ensure_router()
        image_path = _maybe_save_image(image)
        pdf_path = _maybe_file_path(pdf_file)
        print(image_path)
        # Try calling route_query with pdf_path (if supported); otherwise fall back
        try:
            response, label = router.route_query(
                query=message,
                session_id=session_id,
                image_path=image_path,
                pdf_path=pdf_path,
            )
        except TypeError:
            # Older Router without pdf_path support
            response, label = router.route_query(
                query=message,
                session_id=session_id,
                image_path=image_path,
            )
        assistant_text = f"[Routed to: {label}]\n\n{response}"
    except Exception as e:
        assistant_text = (
            "There was an error running the router.\n\n"
            f"Details: {repr(e)}\n\n"
            "Tips: Ensure your working directory is the project root so that\n"
            "`agents`, `core`, and `config` packages are importable, and that\n"
            "router.py references the correct module paths."
        )

    history[-1] = (history[-1][0], assistant_text)
    yield history


# ---------------------------------------------------------------
# Build UI
# ---------------------------------------------------------------

def build_interface() -> gr.Blocks:
    with gr.Blocks(title="AI Scientist – Gradio UI", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# 🧪 AI Scientist (Gradio)\n"
            "Ask questions about imaging, papers, or analysis. "
            "Upload an image or a PDF paper for routing."
        )

        # Keep a consistent session across messages for memory
        session_state = gr.State(str(uuid.uuid4()))

        # Chat history across full width
        chatbot = gr.Chatbot(height=450, show_copy_button=True, avatar_images=None)

        # Two-column composer: left=text, right=uploads
        with gr.Row():
            with gr.Column(scale=7):
                txt = gr.Textbox(
                    label="Your message",
                    placeholder="e.g., 'Design a watershed workflow for these nuclei'",
                    lines=2,
                    autofocus=True,
                )
                with gr.Row():
                    send = gr.Button("Send", variant="primary")
                    clear = gr.ClearButton([chatbot, txt])
            with gr.Column(scale=5):
                image = gr.Image(
                    label="Optional image (routes to Image Analyst)",
                    type="pil",
                    height=200,
                    image_mode="RGB",
                    sources=["upload"],
                    interactive=True,
                )
            with gr.Column(scale=2):
                pdf_file = gr.File(
                    label="Optional PDF (paper, protocol, etc.)",
                    file_count="single",
                    height=200,
                    file_types=[".pdf"],
                )
        # Add a progress / wait indicator
        with gr.Row():
            wait_label = gr.Markdown("", visible=False)

        def show_waiting():
            return gr.update(value="⏳ *Processing... please wait...*", visible=True)

        def hide_waiting():
            return gr.update(value="", visible=False)

        # Wire events — no `_js` arguments to avoid the Gradio 4 error
        # send.click(
        #     chat_fn,
        #     inputs=[txt, image, pdf_file, chatbot, session_state],
        #     outputs=[chatbot],
        # )
        # txt.submit(
        #     chat_fn,
        #     inputs=[txt, image, pdf_file, chatbot, session_state],
        #     outputs=[chatbot],
        # )

        send.click(show_waiting, outputs=[wait_label]) \
            .then(
                chat_fn,
                inputs=[txt, image, pdf_file, chatbot, session_state],
                outputs=[chatbot],
            ) \
            .then(hide_waiting, outputs=[wait_label])\
            .then(lambda: "", None, txt) \
            .then(lambda: None, None, image) \
            .then(lambda: None, None, pdf_file)

        # Hitting Enter (submit) behaves the same way
        txt.submit(show_waiting, outputs=[wait_label]) \
            .then(
                chat_fn,
                inputs=[txt, image, pdf_file, chatbot, session_state],
                outputs=[chatbot],
            ) \
            .then(hide_waiting, outputs=[wait_label]) \
            .then(lambda: "", None, txt) \
            .then(lambda: None, None, image) \
            .then(lambda: None, None, pdf_file)

        # After send, clear the textbox only (keep uploads so users can iterate)
        #send.click(lambda: "", None, txt)
        #txt.submit(lambda: "", None, txt)

        # Dedicated clear button wipes everything
        clear.click(lambda: None, None, chatbot)
        clear.click(lambda: "", None, txt)
        clear.click(lambda: None, None, image)
        clear.click(lambda: None, None, pdf_file)

    return demo


# ---------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------
if __name__ == "__main__":
    demo = build_interface()
    demo.queue(status_update_rate=0.1).launch(debug=True)