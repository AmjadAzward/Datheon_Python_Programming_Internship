import json
import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "faq.json"
HISTORY_FILE = BASE_DIR / "chat_history.txt"

DEFAULT_FAQS = [
    {
        "intent": "business_hours",
        "patterns": [
            r"\b(opening|business|working)\s+hours?\b",
            r"\bwhen are you open\b",
            r"\bwhat time do you close\b",
            r"\bopening time\b"
        ],
        "keywords": ["hours", "open", "opening", "close", "closing"],
        "response": (
            "Our business hours are Monday to Friday, 9:00 AM to 5:00 PM. "
            "We are closed on weekends and public holidays."
        )
    },
    {
        "intent": "location",
        "patterns": [
            r"\b(where are you located|your location|your address)\b",
            r"\bhow can i find you\b"
        ],
        "keywords": ["location", "address", "located", "directions"],
        "response": (
            "Our main office is at 25 Main Street. Please contact our team "
            "for directions or additional location information."
        )
    },
    {
        "intent": "delivery",
        "patterns": [
            r"\b(delivery|shipping)\s+(time|status|cost|fee)\b",
            r"\bwhen will (my|the) order arrive\b",
            r"\btrack (my )?order\b"
        ],
        "keywords": ["delivery", "shipping", "shipment", "tracking", "order"],
        "response": (
            "Standard delivery usually takes 3-5 business days. "
            "Delivery time may vary by location. Contact support with "
            "your order number for an update."
        )
    },
    {
        "intent": "payment",
        "patterns": [
            r"\b(payment|paying)\s+(methods?|options?)\b",
            r"\bhow can i pay\b",
            r"\bdo you accept (cards|cash)\b"
        ],
        "keywords": ["payment", "pay", "card", "cash", "billing"],
        "response": (
            "We accept major debit and credit cards and cash payments "
            "where available. Please confirm accepted methods when ordering."
        )
    },
    {
        "intent": "returns",
        "patterns": [
            r"\b(return|refund|exchange)\s+(policy|a product|an item)\b",
            r"\bhow (do|can) i return\b",
            r"\bcan i get a refund\b"
        ],
        "keywords": ["return", "refund", "exchange", "replace"],
        "response": (
            "Eligible unused products can be returned within 14 days "
            "of delivery with proof of purchase. Contact support to begin "
            "a return request."
        )
    },
    {
        "intent": "products",
        "patterns": [
            r"\b(product|products|items)\s+(available|catalog|list)\b",
            r"\bwhat do you sell\b",
            r"\btell me about (your )?products\b"
        ],
        "keywords": ["product", "products", "catalog", "items", "available"],
        "response": (
            "We offer a range of products. Tell me the product name or "
            "category you are interested in, and I can help with general "
            "information."
        )
    },
    {
        "intent": "contact",
        "patterns": [
            r"\b(contact|support)\s+(number|details|email)\b",
            r"\bhow can i contact you\b",
            r"\bcustomer service\b"
        ],
        "keywords": ["contact", "support", "email", "phone", "telephone"],
        "response": (
            "You can contact our customer support team at "
            "support@example.com or call +1 555 0100."
        )
    },
    {
        "intent": "thanks",
        "patterns": [
            r"\b(thank you|thanks|much appreciated)\b"
        ],
        "keywords": ["thanks", "thank"],
        "response": "You're welcome! I'm happy to help."
    }
]

GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
EXIT_WORDS = {"bye", "goodbye", "exit", "quit"}
HELP_WORDS = {"help", "menu", "options"}


def load_faqs():
    if not FAQ_FILE.exists():
        return DEFAULT_FAQS

    try:
        with FAQ_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list) and all(
            isinstance(item, dict)
            and {"intent", "patterns", "keywords", "response"} <= item.keys()
            for item in data
        ):
            return data

        print("Warning: FAQ file format is invalid. Using built-in FAQs.")
        return DEFAULT_FAQS

    except (json.JSONDecodeError, OSError) as error:
        print(f"Warning: Could not load FAQ file: {error}")
        return DEFAULT_FAQS


def normalize_text(message):
    return re.sub(r"\s+", " ", message.lower().strip())


def similarity_score(message, keyword):
    return SequenceMatcher(None, message, keyword).ratio()


def match_intents(message, faqs):
    normalized = normalize_text(message)
    matches = []

    for faq in faqs:
        score = 0

        for pattern in faq.get("patterns", []):
            try:
                if re.search(pattern, normalized, flags=re.IGNORECASE):
                    score += 3
            except re.error:
                continue

        for keyword in faq.get("keywords", []):
            keyword = keyword.lower()

            if re.search(r"\b" + re.escape(keyword) + r"\b", normalized):
                score += 1
            elif len(keyword) >= 4 and similarity_score(normalized, keyword) >= 0.88:
                score += 0.5

        if score > 0:
            matches.append((score, faq))

    matches.sort(key=lambda item: item[0], reverse=True)
    return matches


def write_history(speaker, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with HISTORY_FILE.open("a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {speaker}: {message}\n")
    except OSError as error:
        print(f"Warning: Could not save conversation history: {error}")


def get_response(message, faqs):
    normalized = normalize_text(message)

    if normalized in GREETINGS:
        return "Hello! Welcome to our customer support assistant. How can I help you today?"

    if normalized in HELP_WORDS:
        return (
            "You can ask me about business hours, location, delivery, "
            "payments, returns, products or contact information."
        )

    matches = match_intents(message, faqs)

    if not matches:
        return (
            "I'm sorry, I didn't understand that question. "
            "You can ask about our business hours, products, delivery, "
            "payments, returns or contact details."
        )

    best_score = matches[0][0]
    best_matches = [
        faq for score, faq in matches
        if score == best_score
    ]

    if len(best_matches) == 1:
        return best_matches[0]["response"]

    responses = [faq["response"] for faq in best_matches]
    return "\n".join(f"- {response}" for response in responses)


def collect_feedback():
    rating = input("\nWould you like to rate this chat? (1-5, or Enter to skip): ").strip()

    if not rating:
        return

    if rating in {"1", "2", "3", "4", "5"}:
        write_history("FEEDBACK", f"Customer rating: {rating}/5")
        print("Thank you for your feedback!")
    else:
        print("Invalid rating. Feedback skipped.")


def main():
    faqs = load_faqs()

    print("\n" + "=" * 55)
    print("             CUSTOMER SUPPORT CHATBOT")
    print("=" * 55)
    print("Hello! I'm your virtual support assistant.")
    print("Type 'help' to see topics or 'bye' to end the chat.")
    print("-" * 55)

    write_history("SYSTEM", "Conversation started")

    while True:
        message = input("\nYou: ").strip()

        if not message:
            print("Bot: Please enter a question.")
            continue

        write_history("CUSTOMER", message)
        normalized = normalize_text(message)

        if normalized in EXIT_WORDS:
            response = "Thank you for chatting with us. Have a great day!"
            print(f"Bot: {response}")
            write_history("BOT", response)
            break

        response = get_response(message, faqs)
        print(f"Bot: {response}")
        write_history("BOT", response)

    collect_feedback()
    write_history("SYSTEM", "Conversation ended")


if __name__ == "__main__":
    main()
