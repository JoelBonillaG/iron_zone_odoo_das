import sys
from io import BytesIO
import base64
with open("/home/david/Desktop/projects/university/das-odoo/seeds/IronZone.png", "rb") as f:
    header = f.read(30)
    print("PNG" in str(header))
