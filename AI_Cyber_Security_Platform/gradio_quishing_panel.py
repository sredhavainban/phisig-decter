"""
Gradio demo for QR Quishing Detection

This panel uses `gr.Image(type="filepath")` and passes the filepath directly
into `analyze_qr_quishing` (no preview/resizing or PIL conversions in the UI).

Run (PowerShell):
& .venv/Scripts/python.exe AI_Cyber_Security_Platform/gradio_quishing_panel.py
Then open the local Gradio URL shown in the terminal.
"""
from pathlib import Path
import json

import gradio as gr

from services.quishing_detector import analyze_qr_quishing


def _format_result(res: dict) -> str:
    if not res:
        return 'No result'
    if res.get('decoded_url') is None:
        return (
            f"Decoded URL: None\n"
            f"Risk Level: {res.get('risk_level')}\n\n"
            f"{res.get('user_warning', '')}\n\n"
            f"Explanation: {res.get('security_explanation', '')}"
        )

    lines = [f"Decoded URL: {res.get('decoded_url')}"]
    lines.append(f"Final URL: {res.get('final_url')}")
    lines.append(f"Redirect Count: {res.get('redirect_count')}")
    lines.append(f"Risk Level: {res.get('risk_level')}")
    if res.get('redirect_chain'):
        lines.append('\nRedirect Chain:')
        for u in res.get('redirect_chain'):
            lines.append(f"- {u}")
    if res.get('reason_for_risk'):
        lines.append(f"\nReason for risk: {res.get('reason_for_risk')}")
    if res.get('user_warning'):
        lines.append(f"User warning: {res.get('user_warning')}")
    if res.get('security_explanation'):
        lines.append(f"\nExplanation: {res.get('security_explanation')}")
    return "\n".join(lines)


def analyze_filepath(image_path: str):
    """Gradio will pass a filepath when `type='filepath'` is used.

    We pass that path directly to the detector without any UI-side processing.
    """
    if not image_path:
        return 'No file uploaded', None
    # Defensive: ensure file exists
    p = Path(image_path)
    if not p.exists():
        return 'File not found: ' + str(image_path), None

    try:
        res = analyze_qr_quishing(str(p))
    except Exception as e:
        return f'Internal error: {e}', str(p)

    return _format_result(res), str(p)


with gr.Blocks() as demo:
    gr.Markdown("# PhishGuard — QR Quishing Demo")
    gr.Markdown("Upload a QR image file. The UI passes the file path directly to the detector (no resizing or PIL conversion). Use original image files for best results.")

    with gr.Row():
        inp = gr.Image(label="Upload QR Image", type="filepath")
        out_text = gr.Textbox(label="Analysis Result", lines=20)

    with gr.Row():
        btn = gr.Button("Analyze")
        preview = gr.Image(label="Uploaded Image Preview")

    btn.click(fn=analyze_filepath, inputs=inp, outputs=[out_text, preview])

if __name__ == '__main__':
    demo.launch()
