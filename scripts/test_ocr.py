import sys, os
sys.path.insert(0, os.path.join(os.getcwd(),'AI_Cyber_Security_Platform'))
from models.webpage_phishing import ocr_utils
p = 'test_phish.png'
print('Calling OCR on', p)
try:
    txt = ocr_utils.extract_text_from_image(p)
    print('OCR result (repr):', repr(txt))
    print('LEN:', len(txt))
except Exception as e:
    print('OCR call failed:', e)
