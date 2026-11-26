
import random
from pathlib import Path

MAX_ATTEMPTS = 6

HANGMAN_STAGES = [
    """
     +---+
     |   |
         |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
     |   |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|   |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
    =========
    """
]

WORD_CATEGORIES = {
    "Animals": [
        "elephant",
        "giraffe",
        "kangaroo",
        "dolphin",
        "penguin",
        "butterfly"
    ],
    "Technology": [
        "python",
        "computer",
        "keyboard",
        "software",
        "algorithm",
        "programming"
    ],
    "Nature": [
        "mountain",
        "waterfall",
        "rainbow",
        "forest",
        "sunshine",
        "ocean"
    ],
    "Food": [
        "chocolate",
        "pineapple",
        "sandwich",
        "hamburger",
        "strawberry",
        "pancake"
    ]
}

DIFFICULTIES = {
    "1": ("Easy", 8),
    "2": ("Medium", 6),
    "3": ("Hard", 4)
}


def load_words():
    word_file = Path(__file__).with_name("words.txt")

    if word_file.exists():
        try:
            with word_file.open("r", encoding="utf-8") as file:
                words = [
                    line.strip().upper()
                    for line in file
                    if line.strip().isalpha()
                ]

            if words:
                return {"Custom Words": words}

        except OSError:
            print("Could not read words.txt. Using built-in words.")

    return WORD_CATEGORIES


def choose_difficulty():
    print("\nChoose your difficulty:")
    print("1. Easy   - 8 incorrect guesses")
    print("2. Medium - 6 incorrect guesses")
    print("3. Hard   - 4 incorrect guesses")

    while True:
        choice = input("Enter 1, 2, or 3: ").strip()

        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]

        print("Invalid choice. Please enter 1, 2, or 3.")


def choose_word(word_categories):
    category = random.choice(list(word_categories.keys()))
    secret_word = random.choice(word_categories[category])

    return category, secret_word.upper()


def display_game(
    secret_word,
    guessed_letters,
    wrong_guesses,
    max_attempts,
    category
):
    print("\n" + "=" * 40)
    print("              HANGMAN")
    print("=" * 40)

    stage = round(wrong_guesses * MAX_ATTEMPTS / max_attempts)
    print(HANGMAN_STAGES[stage])

    masked_word = " ".join(
        letter if letter in guessed_letters else "_"
        for letter in secret_word
    )

    print("Category:", category)
    print("Word:", masked_word)

    print(
        "Guessed letters:",
        " ".join(sorted(guessed_letters))
        if guessed_letters else "None"
    )

    print(f"Incorrect guesses: {wrong_guesses}/{max_attempts}")
    print(f"Attempts remaining: {max_attempts - wrong_guesses}")

    print("-" * 40)
    print("Enter a letter to guess.")
    print("Enter ? to use a hint.")
    print("-" * 40)


def use_hint(secret_word, guessed_letters):
    available_letters = [
        letter for letter in set(secret_word)
        if letter not in guessed_letters
    ]

    if not available_letters:
        print("There are no letters left to reveal!")
        return None

    hint_letter = random.choice(available_letters)

    print(f"\nHint: The word contains the letter '{hint_letter}'.")

    return hint_letter


def play_game(word_categories, difficulty):
    difficulty_name, max_attempts = difficulty

    category, secret_word = choose_word(word_categories)

    guessed_letters = set()
    wrong_guesses = 0
    hint_used = False

    while wrong_guesses < max_attempts:

        display_game(
            secret_word,
            guessed_letters,
            wrong_guesses,
            max_attempts,
            category
        )

        if all(
            letter in guessed_letters
            for letter in secret_word
        ):
            print("\nCongratulations! You won!")
            print("Secret word:", secret_word)
            return True

        print("Hint available:", "No" if hint_used else "Yes")

        guess = input("\nYour guess: ").strip().upper()

        if not guess:
            print("Please enter a letter.")
            continue

        if guess == "?":
            if hint_used:
                print("You have already used your hint!")
                continue

            hint_letter = use_hint(secret_word, guessed_letters)

            if hint_letter:
                guessed_letters.add(hint_letter)
                hint_used = True
                wrong_guesses += 1
                print("Hint used! One attempt deducted.")

            continue

        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single alphabetic letter.")
            continue

        if guess in guessed_letters:
            print(f"You already guessed '{guess}'. Try another letter.")
            continue

        guessed_letters.add(guess)

        if guess in secret_word:
            print(f"Correct! '{guess}' is in the word.")
        else:
            wrong_guesses += 1
            print(f"Sorry! '{guess}' is not in the word.")

    display_game(
        secret_word,
        guessed_letters,
        wrong_guesses,
        max_attempts,
        category
    )

    print("\nGame over! You ran out of attempts.")
    print("The secret word was:", secret_word)

    return False


def main():
    word_categories = load_words()

    games_played = 0
    games_won = 0

    print("=" * 40)
    print("       WELCOME TO HANGMAN")
    print("=" * 40)

    print("\nGuess the hidden word one letter at a time.")
    print("Choose a difficulty and try to save the stick figure!")

    while True:
        difficulty = choose_difficulty()

        won = play_game(word_categories, difficulty)

        games_played += 1

        if won:
            games_won += 1

        win_percentage = (games_won / games_played) * 100

        print("\n" + "=" * 40)
        print("          GAME STATISTICS")
        print("=" * 40)

        print("Games played:", games_played)
        print("Games won:", games_won)
        print("Games lost:", games_played - games_won)
        print(f"Win percentage: {win_percentage:.1f}%")

        print("=" * 40)

        while True:
            play_again = input(
                "\nWould you like to play again? (y/n): "
            ).strip().lower()

            if play_again in ("y", "yes", "n", "no"):
                break

            print("Please enter y or n.")

        if play_again in ("n", "no"):
            print("\nThank you for playing Hangman!")
            print("Keep practicing your Python skills!")
            break


if __name__ == "__main__":
    main()
