import random

jokes = ["When the window fell into the incinerator, it was a pane in the ash to retrieve.",
         "What's a pirate's favorite letter? It be the Sea",
         "How do you count cows? A 'Cow'culator",
         "Did you hear about the guy whose whole left side was cut off? He's all right now.",
         "I used to be a banker but I lost interest",
         "How do you find Will Smith in the snow? You look for the fresh prints.",
         "I had a dream that I was a muffler last night. I woke up exhausted.",
         "Why do bakers work so hard? They knead the dough."]


def generate_joke_prompt(prompt: str) -> str:
    random_joke = random.choice(jokes)
    return random_joke
