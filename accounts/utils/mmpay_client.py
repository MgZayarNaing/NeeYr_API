from django.conf import settings
from mmpay.client import MMPaySDK

# settings.py ထဲမှ MMPY_CONFIG ကို ယူ၍ SDK တည်ဆောက်ခြင်း
MMPay = MMPaySDK(settings.MMPAY_CONFIG)