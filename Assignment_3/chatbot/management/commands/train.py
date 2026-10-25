"""`python manage.py train` - (re)train the chatbot from training_data.py."""
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from django.core.management.base import BaseCommand

from chatbot.bot import build_chatbot
from chatbot.training_data import CONVERSATIONS, CORPUS_PATHS


class Command(BaseCommand):
    help = "Clear the chatbot's stored conversations and train it again."

    def handle(self, *args, **options):
        bot = build_chatbot(read_only=False)

        # Start from an empty knowledge base so retraining never duplicates data.
        bot.storage.drop()

        # General small talk from the official ChatterBot corpus first...
        corpus_trainer = ChatterBotCorpusTrainer(bot, show_training_progress=False)
        corpus_trainer.train(*CORPUS_PATHS)

        # ...then the project-specific dialogs, including the brief's sample.
        list_trainer = ListTrainer(bot, show_training_progress=False)
        for conversation in CONVERSATIONS:
            list_trainer.train(conversation)

        self.stdout.write(
            self.style.SUCCESS(
                f"Trained on {len(CORPUS_PATHS)} corpus sections and "
                f"{len(CONVERSATIONS)} custom conversations."
            )
        )
