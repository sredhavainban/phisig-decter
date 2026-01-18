from pathlib import Path
import qrcode
out = Path(__file__).resolve().parent.parent / 'static' / 'uploads' / 'test_qr.png'
out.parent.mkdir(parents=True, exist_ok=True)
# Use httpbin redirect endpoint to produce a redirect chain for testing
data = 'https://httpbin.org/redirect/2'
img = qrcode.make(data)
img.save(out)
print('wrote', out)
