"""`python manage.py chat` - the terminal client for talking to the bot."""
import sys

from django.core.management.base import BaseCommand

from chatbot.bot import build_chatbot

EXIT_WORDS = {"exit", "quit", "bye"}


class Command(BaseCommand):
    help = "Start an interactive chat session with the bot in the terminal."

    def handle(self, *args, **options):
        bot = build_chatbot(read_only=True)

        self.stdout.write(f"Chatting with {bot.name}. Type 'exit' or 'quit' to stop.\n")

        while True:
            try:
                user_input = input("user: ").strip()
                if not sys.stdin.isatty():
                    # Piped input (e.g. the CI demo) isn't echoed by a terminal,
                    # so print it to keep the transcript readable.
                    self.stdout.write(user_input)
            except (EOFError, KeyboardInterrupt):
                # Ctrl+D / Ctrl+C end the session cleanly instead of a traceback.
                self.stdout.write("")
                break

            if not user_input:
                continue
            if user_input.lower() in EXIT_WORDS:
                break

            response = bot.get_response(user_input)
            self.stdout.write(f"bot: {response}")

        self.stdout.write("bot: Goodbye!")
