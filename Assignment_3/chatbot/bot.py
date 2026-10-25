"""Builds the ChatterBot instance shared by the train and chat commands."""
from chatterbot import ChatBot

BOT_NAME = "Assignment3Bot"

# ChatterBot picks one of these at random when nothing it knows is close
# enough, so the conversation keeps going instead of repeating one apology.
DEFAULT_RESPONSES = [
    "Interesting! Tell me more.",
    "I'm still learning. Could you put that another way?",
    "That's new to me. What else would you like to talk about?",
    "Hmm, I'm not sure. Try asking me for a joke or a math question!",
]


def build_chatbot(read_only: bool = True) -> ChatBot:
    """
    Create a ChatBot backed by Django's database.

    :param read_only: When True the bot answers without learning from what
        the user types, so its replies stay consistent between sessions.
    """
    return ChatBot(
        BOT_NAME,
        storage_adapter="chatterbot.storage.DjangoStorageAdapter",
        # Every adapter answers; the reply with the highest confidence wins.
        # BestMatch is listed first so it wins ties at zero confidence.
        logic_adapters=[
            {
                # Picks the known statement closest to the input and
                # returns the response it was trained with.
                "import_path": "chatterbot.logic.BestMatch",
                "default_response": DEFAULT_RESPONSES,
                "maximum_similarity_threshold": 0.90,
            },
            {
                # Answers arithmetic questions such as "What is 7 times 6?".
                "import_path": "chatterbot.logic.MathematicalEvaluation",
            },
        ],
        read_only=read_only,
    )
