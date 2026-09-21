# AI QR Code Generator

Hands-On Assignment 2 — Advanced Artificial Intelligence (MSCS-633-M20)
University of the Cumberlands

A simple Python script that generates a QR code image from a user-supplied
URL, using the [`qrcode`](https://pypi.org/project/qrcode/) library. Tested
against [Biox Systems](https://www.bioxsystems.com/).

## Output

![QR code for bioxsystems.com](output/qr_code.png)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python qr_code_generator.py https://www.bioxsystems.com/
```

Or run without arguments to be prompted for a URL:

```bash
python qr_code_generator.py
```

The QR code is saved to `output/qr_code.png` and opened automatically.

## Project structure

```text
Assignment_2/
├── README.md
├── qr_code_generator.py    # source code
├── requirements.txt        # dependency manifest
├── output/qr_code.png      # sample output
└── docs/Assignment_2.md    # assignment brief
```

## Author

Parthasarathi Ponnapalli
