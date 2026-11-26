# Datheon Python Programming Internship Projects

A collection of four Python command-line applications developed as part of the Datheon Python Programming Internship.

## Projects

| Project | Description | Run command |
|---|---|---|
| [Hangman](Task1_Hangman/) | Play a category-based word guessing game with difficulty levels, hints, and ASCII graphics. | `python3 Task1_Hangman/hangman.py` |
| [Portfolio Tracker](Task2_Portfolio_Tracker/) | Manage stock holdings and calculate investment value, gains/losses, returns, and CSV summaries. | `python3 Task2_Portfolio_Tracker/portfolio.py` |
| [File Organizer](Task3_File_Organizer/) | Sort files into category folders, preview changes, review organization history, and undo the latest operation. | `python3 Task3_File_Organizer/organizer.py` |
| [Customer Chatbot](Task4_Customer_Chatbot/) | Answer common customer-service questions with intent matching and save conversation history. | `python3 Task4_Customer_Chatbot/chatbot.py` |

## Requirements

- Python 3
- A terminal or command prompt
- No third-party Python packages

## Getting Started

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd Datheon_Python_Programming_Internship
```

Run any project using the commands in the table above. Alternatively, change into a project folder and run its Python file directly:

```bash
cd Task1_Hangman
python3 hangman.py
```

## Project Structure

```text
Datheon_Python_Programming_Internship/
├── README.md
├── Task1_Hangman/
│   └── hangman.py
├── Task2_Portfolio_Tracker/
│   ├── portfolio.py
│   └── portfolio_data.json
├── Task3_File_Organizer/
│   └── organizer.py
└── Task4_Customer_Chatbot/
    ├── chatbot.py
    └── chat_history.txt
```

## Notes

- The portfolio tracker stores data locally in `Task2_Portfolio_Tracker/portfolio_data.json` and can export a CSV summary.
- The file organizer prompts for a directory and includes a dry-run mode before moving files.
- The chatbot stores conversation and feedback entries in `Task4_Customer_Chatbot/chat_history.txt`.

## Author

Datheon Python Programming Internship project collection.
