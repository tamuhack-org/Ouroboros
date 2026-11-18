import json
from io import BytesIO

import pyqrcode

from application.models import Application

QR_SCALE = 5


def qr_payload(app: Application) -> str:
    """Build the JSON scanned by volunteers at check-in and meals."""
    return json.dumps(
        {
            "first_name": app.first_name,
            "last_name": app.last_name,
            "email": app.user.email,
            "university": app.school.name if app.school else "",
        }
    )


def qr_png_bytes(app: Application) -> bytes:
    stream = BytesIO()
    pyqrcode.create(qr_payload(app)).png(stream, scale=QR_SCALE)
    return stream.getvalue()


def qr_png_base64(app: Application) -> str:
    return pyqrcode.create(qr_payload(app)).png_as_base64_str(scale=QR_SCALE)
