"""
AI QR Code Generator
Hands-On Assignment 2 - Advanced Artificial Intelligence (MSCS-633-M20)

Generates a QR code image from a user-supplied URL using the `qrcode`
library, saves it to disk, and displays it.
"""

import sys

import qrcode


def generate_qr_code(url, output_path="output/qr_code.png"):
    """Create a QR code image for the given URL and save it to output_path."""
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # high error tolerance
        box_size=10,  # pixel size of each QR module
        border=4,  # thickness of the quiet-zone border
    )
    qr.add_data(url)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    image.save(output_path)
    print(f"QR code saved to: {output_path}")

    image.show()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else input("Enter the URL to encode: ").strip()
    generate_qr_code(url)
