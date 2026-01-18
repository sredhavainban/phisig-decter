# PhishGuard — QR Quishing Detector

This project (PhishGuard) includes an independent, modular QR Redirection Chain Analyzer added to the pipeline.

Overview
- URL Phishing Detection
- Website HTML Analysis
- Screenshot OCR Detection
- Spam Message Detection
- QR Redirection Chain Analyzer (new)

Design principles
- No model retraining required.
- No changes to existing modules or ensemble logic.
- Independent: the QR detector is implemented as `services/quishing_detector.py` and exposed via a Flask route `/qr-quishing`.

Quick test (PowerShell)
1. Activate the virtualenv:

```powershell
& .venv\Scripts\Activate.ps1
```

2. Install dependencies (if not already installed):

```powershell
& .venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Generate a test QR (example uses httpbin to create redirects):

```powershell
& .venv\Scripts\python.exe -c "import qrcode; qrcode.make('https://httpbin.org/redirect/2').save('AI_Cyber_Security_Platform/static/uploads/test_qr.png'); print('QR written')"
```

4. Run the detector CLI on the generated image:

```powershell
& .venv\Scripts\python.exe AI_Cyber_Security_Platform\services\quishing_detector.py AI_Cyber_Security_Platform\static\uploads\test_qr.png
```

5. Or open the web UI:

```powershell
& .venv\Scripts\python.exe AI_Cyber_Security_Platform\app.py
# then visit http://localhost:7860/qr-quishing
```

Notes
- The detector uses OpenCV (`opencv-python`) to decode QR codes and `requests` to follow redirections.
- The Flask route is `GET/POST /qr-quishing` and saves uploaded images under `static/uploads`.
- The service is CPU-only and suitable for local or Hugging Face Spaces deployment.

If you want, I can add a small Gradio demo file `gradio_quishing_panel.py` for HF Spaces.
