from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    """Django app holding the chatbot's training data and terminal commands."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"
