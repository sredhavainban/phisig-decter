from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (900,260), (255,255,255))
d = ImageDraw.Draw(img)
text = "Verify your account now\nClick here to confirm password\nLimited time offer"
# default font
try:
    f = ImageFont.truetype('arial.ttf', 20)
except Exception:
    f = ImageFont.load_default()
d.multiline_text((12,12), text, fill=(0,0,0), font=f, spacing=6)
img.save('test_phish.png')
print('Created test_phish.png')
