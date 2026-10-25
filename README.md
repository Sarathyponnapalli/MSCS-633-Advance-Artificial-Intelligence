# MSCS-633 Advanced Artificial Intelligence

Coursework for MSCS-633-M20, Advanced Artificial Intelligence, at the University of the Cumberlands.

## Assignments

| Assignment | Topic | Folder |
| --- | --- | --- |
| Hands-On Assignment 2 | AI QR Code Generator (Python, `qrcode`) | [Assignment_2](Assignment_2/) |
| Hands-On Assignment 3 | Simple Q&A Chatbot (Django, ChatterBot, Docker) | [Assignment_3](Assignment_3/) |

## Repository layout

```text
.
├── README.md
├── .gitignore
├── Assignment_2/
│   ├── README.md               # setup and usage
│   ├── qr_code_generator.py    # source code
│   ├── requirements.txt        # dependency manifest
│   ├── output/qr_code.png      # sample output
│   └── docs/Assignment_2.md    # assignment brief
├── Assignment_3/
│   ├── README.md               # setup and usage
│   ├── manage.py               # Django entry point
│   ├── chatbot_project/        # Django settings
│   ├── chatbot/                # bot, training data, train/chat commands
│   ├── requirements.txt        # dependency manifest
│   ├── Dockerfile              # container build
│   ├── compose.yaml            # container run config
│   └── output/sample_chat.txt  # sample output
├── .github/workflows/
│   └── assignment3-chatbot.yml # builds, demos and publishes the Assignment 3 chatbot
└── .devcontainer/
    └── assignment3/            # GitHub Codespaces setup for Assignment 3
```

Each assignment lives in its own `Assignment_N/` folder with its own README, code, and dependency file.

## Try Assignment 3 without installing anything

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Sarathyponnapalli/MSCS-633-Advance-Artificial-Intelligence?devcontainer_path=.devcontainer/assignment3/devcontainer.json)

Then run `python /app/manage.py chat` in the Codespaces terminal. Other options are in [Assignment_3/README.md](Assignment_3/README.md#try-it).

## Author

Parthasarathi Ponnapalli
