import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "organizer_history.json"
LOG_FILE = BASE_DIR / "organizer.log"

FILE_CATEGORIES = {
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx",
        ".xls", ".xlsx", ".csv", ".rtf", ".odt"
    ],
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".svg", ".webp", ".tiff", ".ico"
    ],
    "Videos": [
        ".mp4", ".mkv", ".mov", ".avi", ".wmv",
        ".flv", ".webm", ".mpeg"
    ],
    "Archives": [
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"
    ],
    "Code": [
        ".py", ".java", ".cpp", ".c", ".html",
        ".css", ".js", ".php", ".sql", ".json"
    ],
    "Audio": [
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"
    ]
}

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as error:
        logging.error("Could not load history: %s", error)
        print("Warning: Could not read the history file.")
        return []


def save_history(history):
    try:
        with HISTORY_FILE.open("w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)
    except OSError as error:
        logging.error("Could not save history: %s", error)
        print(f"Could not save history: {error}")


def get_category(extension):
    extension = extension.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return "Others"


def get_unique_path(destination, reserved=None):
    reserved = reserved if reserved is not None else set()

    if not destination.exists() and destination not in reserved:
        return destination

    counter = 1

    while True:
        new_destination = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )

        if not new_destination.exists() and new_destination not in reserved:
            return new_destination

        counter += 1


def get_files(folder):
    excluded_dirs = set(FILE_CATEGORIES.keys()) | {"Others"}
    excluded_files = {
        HISTORY_FILE.resolve(),
        LOG_FILE.resolve(),
        Path(__file__).resolve()
    }

    def handle_walk_error(error):
        logging.error("Directory access error: %s", error)

    for current_path, directories, filenames in os.walk(
        folder, onerror=handle_walk_error
    ):
        current = Path(current_path)

        if current == folder:
            directories[:] = [
                name for name in directories
                if name not in excluded_dirs
            ]

        for filename in filenames:
            file_path = current / filename

            try:
                if file_path.resolve() in excluded_files:
                    continue

                if file_path.is_symlink() or not file_path.is_file():
                    continue

                yield file_path

            except OSError as error:
                logging.error("Could not inspect %s: %s", file_path, error)


def organize_files(folder_path, dry_run=False):
    folder = Path(folder_path).expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        print("Error: Please provide an existing directory.")
        return

    batch = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "actions": []
    }

    reserved = set()
    processed = 0
    skipped = 0
    total_size = 0

    print("\nDRY-RUN MODE: No files will be moved." if dry_run
          else "\nStarting file organization...")

    for source in get_files(folder):
        try:
            category = get_category(source.suffix)
            destination_folder = folder / category
            destination = get_unique_path(
                destination_folder / source.name,
                reserved
            )
            reserved.add(destination)

            size = source.stat().st_size
            total_size += size

            if dry_run:
                print(f"[PREVIEW] {source} -> {destination}")
                processed += 1
                continue

            destination_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))

            batch["actions"].append({
                "original": str(source),
                "destination": str(destination)
            })

            logging.info("Moved %s to %s", source, destination)
            print(f"Moved: {source.name} -> {category}/")
            processed += 1

        except PermissionError:
            print(f"Permission denied: {source}")
            logging.warning("Permission denied: %s", source)
            skipped += 1

        except OSError as error:
            print(f"Could not move {source}: {error}")
            logging.error("Move failed for %s: %s", source, error)
            skipped += 1

    if not dry_run and batch["actions"]:
        history = load_history()
        history.append(batch)
        save_history(history)

    if dry_run:
        print("\nPreview completed. No changes were made.")

    print("\n" + "=" * 45)
    print("          ORGANIZATION SUMMARY")
    print("=" * 45)
    print(f"Files processed : {processed}")
    print(f"Files skipped   : {skipped}")
    print(f"Total size      : {total_size / (1024 * 1024):.2f} MB")
    print("=" * 45)


def undo_last_organization():
    history = load_history()

    if not history:
        print("\nNo organization history found.")
        return

    batch = history[-1]
    actions = batch.get("actions", [])
    restored = 0

    if not actions:
        print("\nThere are no files to restore in the latest operation.")
        history.pop()
        save_history(history)
        return

    print("\nUndoing the latest organization...")

    for action in reversed(actions.copy()):
        original = Path(action["original"])
        destination = Path(action["destination"])

        try:
            if not destination.exists():
                print(f"Cannot find: {destination}")
                continue

            original.parent.mkdir(parents=True, exist_ok=True)
            restore_path = get_unique_path(original)

            shutil.move(str(destination), str(restore_path))

            print(f"Restored: {restore_path.name}")
            logging.info("Restored %s", restore_path)

            actions.remove(action)
            restored += 1
            save_history(history)

        except (PermissionError, OSError) as error:
            print(f"Could not restore {destination}: {error}")
            logging.error("Undo failed: %s", error)

    if not actions:
        history.pop()
        save_history(history)

    print(f"\nFiles successfully restored: {restored}")


def show_statistics(folder_path):
    folder = Path(folder_path).expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        print("Error: Invalid directory.")
        return

    statistics = {}
    total_files = 0
    total_size = 0

    for file_path in get_files(folder):
        try:
            category = get_category(file_path.suffix)
            size = file_path.stat().st_size

            if category not in statistics:
                statistics[category] = {"count": 0, "size": 0}

            statistics[category]["count"] += 1
            statistics[category]["size"] += size
            total_files += 1
            total_size += size

        except OSError as error:
            logging.error("Statistics error for %s: %s", file_path, error)

    print("\n" + "=" * 45)
    print("             FILE STATISTICS")
    print("=" * 45)

    for category, data in sorted(statistics.items()):
        size_mb = data["size"] / (1024 * 1024)
        print(
            f"{category:<15} Files: {data['count']:<5} "
            f"Size: {size_mb:.2f} MB"
        )

    print("-" * 45)
    print(f"Total files: {total_files}")
    print(f"Total size : {total_size / (1024 * 1024):.2f} MB")
    print("=" * 45)


def main():
    print("\n" + "=" * 45)
    print("          ADVANCED FILE ORGANIZER")
    print("=" * 45)

    folder_path = input(
        "\nEnter the directory path to organize: "
    ).strip().strip('"').strip("'")

    if not folder_path:
        print("A directory path is required.")
        return

    while True:
        print("\n--------------- MAIN MENU ---------------")
        print("1. Organize files")
        print("2. Preview organization (Dry Run)")
        print("3. Undo last organization")
        print("4. View file statistics")
        print("5. Exit")
        print("-----------------------------------------")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            confirmation = input(
                "Are you sure you want to move files? (yes/no): "
            ).strip().lower()

            if confirmation == "yes":
                organize_files(folder_path)
            else:
                print("Organization cancelled.")

        elif choice == "2":
            organize_files(folder_path, dry_run=True)

        elif choice == "3":
            confirmation = input(
                "Undo the latest organization? (yes/no): "
            ).strip().lower()

            if confirmation == "yes":
                undo_last_organization()
            else:
                print("Undo cancelled.")

        elif choice == "4":
            show_statistics(folder_path)

        elif choice == "5":
            print("\nThank you for using Advanced File Organizer!")
            break

        else:
            print("Invalid option. Please choose between 1 and 5.")


if __name__ == "__main__":
    main()
