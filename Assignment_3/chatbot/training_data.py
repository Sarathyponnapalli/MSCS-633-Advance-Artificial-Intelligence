"""
Conversations the bot is trained on.

CORPUS_PATHS are sections of the official chatterbot-corpus English data,
giving the bot broad small-talk coverage. CONVERSATIONS are project-specific
dialogs; each is an ordered list, and ChatterBot's ListTrainer learns every
line as the response to the line before it.
"""

CORPUS_PATHS = [
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations",
    "chatterbot.corpus.english.humor",
    "chatterbot.corpus.english.emotion",
    "chatterbot.corpus.english.ai",
    "chatterbot.corpus.english.computers",
    "chatterbot.corpus.english.food",
    "chatterbot.corpus.english.botprofile",
    "chatterbot.corpus.english.science",
    "chatterbot.corpus.english.sports",
    "chatterbot.corpus.english.movies",
    "chatterbot.corpus.english.literature",
    "chatterbot.corpus.english.history",
    "chatterbot.corpus.english.trivia",
    "chatterbot.corpus.english.health",
]

CONVERSATIONS = [
    # Sample dialog from the assignment brief
    [
        "Good morning! How are you doing?",
        "I am doing very well, thank you for asking.",
        "You're welcome.",
        "Do you like hats?",
    ],
    [
        "Hello",
        "Hi there! How can I help you today?",
    ],
    [
        "Hi",
        "Hello! What would you like to talk about?",
    ],
    [
        "How are you?",
        "I am doing well. How about you?",
        "I am fine, thanks.",
        "Glad to hear it.",
    ],
    [
        "What is your name?",
        "I am Assignment3Bot, a simple Q&A chatbot.",
    ],
    [
        "Who created you?",
        "I was built with Python, Django, and ChatterBot for MSCS-633.",
    ],
    [
        "What is ChatterBot?",
        "ChatterBot is a machine-learning based conversational dialog engine built in Python.",
    ],
    [
        "What is Django?",
        "Django is a high-level Python web framework that I use to store my conversations.",
    ],
    # Follow-ups to the bot's "Do you like hats?" question
    [
        "Do you like hats?",
        "Yes",
        "Me too! A good hat can finish off any outfit. What kind do you wear?",
        "Black ones",
        "Black hats go with everything. Classic choice!",
    ],
    [
        "What kind do you wear?",
        "Baseball caps",
        "Baseball caps are great for sunny days. Do you follow any baseball team?",
    ],
    [
        "What kind do you wear?",
        "Beanies",
        "Beanies are perfect for cold weather. Cozy choice!",
    ],
    [
        "Do you like hats?",
        "Yes I like them",
        "Great taste! Baseball caps, beanies, or something fancier?",
    ],
    [
        "Do you like hats?",
        "No",
        "That's fair, not everyone is a hat person.",
    ],
    [
        "lol",
        "Glad I could make you laugh!",
    ],
    [
        "haha",
        "I'm happy you find me funny.",
    ],
    [
        "What can you do?",
        "I can chat, tell jokes, and answer simple questions, including math like 'What is 7 times 6?'.",
    ],
    [
        "What is your favorite movie?",
        "I like The Matrix. A movie about computers feels relatable to me!",
    ],
    [
        "Do you like sports?",
        "I enjoy watching soccer and basketball. Do you play any sports?",
    ],
    [
        "Thank you",
        "You're welcome!",
    ],
    [
        "Goodbye",
        "Goodbye! Have a great day.",
    ],
]
