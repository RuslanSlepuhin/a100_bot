import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
from bot import bot_variables as variables

class QRCodeCreateAndRead:

    def qr_create(self, data):
        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(variables.qrcode_create_path)
        return variables.qrcode_create_path

    def read(self, image_path):
        image_path = variables.qrcode_read_path if not image_path else image_path
        d = decode(Image.open(image_path))
        return d[0].data.decode('utf-8') if d else False


