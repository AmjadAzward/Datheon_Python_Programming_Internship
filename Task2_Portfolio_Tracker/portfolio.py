import csv
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "portfolio_data.json"
SUMMARY_FILE = BASE_DIR / "portfolio_summary.csv"


def load_portfolio():
    if not DATA_FILE.exists():
        return {}

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError) as error:
        print(f"Could not load portfolio data: {error}")
        return {}


def save_portfolio(portfolio):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(portfolio, file, indent=4)
    except OSError as error:
        print(f"Could not save portfolio: {error}")


def read_positive_number(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def read_ticker():
    while True:
        ticker = input("Enter stock ticker symbol: ").strip().upper()
        if ticker and ticker.replace(".", "").replace("-", "").isalnum():
            return ticker
        print("Please enter a valid ticker symbol, such as AAPL or MSFT.")


def add_holding(portfolio):
    print("\nADD STOCK HOLDING")
    ticker = read_ticker()
    buy_price = read_positive_number("Enter average buy price per share: ")
    shares = read_positive_number("Enter number of shares: ")
    current_price = read_positive_number("Enter current price per share: ")

    portfolio[ticker] = {
        "buy_price": buy_price,
        "shares": shares,
        "current_price": current_price,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_portfolio(portfolio)
    print(f"{ticker} was added to your portfolio.")


def update_holding(portfolio):
    ticker = read_ticker()

    if ticker not in portfolio:
        print(f"{ticker} was not found in your portfolio.")
        return

    print("\n1. Update average buy price")
    print("2. Update share quantity")
    print("3. Update current market price")
    print("4. Update all values")

    choice = input("Choose an option: ").strip()
    holding = portfolio[ticker]

    if choice in ("1", "4"):
        holding["buy_price"] = read_positive_number("New average buy price: ")
    if choice in ("2", "4"):
        holding["shares"] = read_positive_number("New share quantity: ")
    if choice in ("3", "4"):
        holding["current_price"] = read_positive_number("New current price: ")

    if choice not in ("1", "2", "3", "4"):
        print("Invalid option.")
        return

    holding["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_portfolio(portfolio)
    print(f"{ticker} was updated successfully.")


def remove_holding(portfolio):
    ticker = read_ticker()

    if ticker not in portfolio:
        print(f"{ticker} was not found in your portfolio.")
        return

    confirmation = input(f"Remove {ticker} from your portfolio? (yes/no): ")
    if confirmation.strip().lower() == "yes":
        del portfolio[ticker]
        save_portfolio(portfolio)
        print(f"{ticker} was removed.")
    else:
        print("Removal cancelled.")


def calculate_holding(ticker, holding):
    buy_price = float(holding["buy_price"])
    shares = float(holding["shares"])
    current_price = float(holding["current_price"])

    invested = buy_price * shares
    market_value = current_price * shares
    gain_loss = market_value - invested
    percentage = (gain_loss / invested) * 100 if invested else 0

    return {
        "ticker": ticker,
        "buy_price": buy_price,
        "shares": shares,
        "current_price": current_price,
        "invested": invested,
        "market_value": market_value,
        "gain_loss": gain_loss,
        "percentage": percentage,
        "last_updated": holding.get("last_updated", "")
    }


def get_portfolio_report(portfolio):
    return [
        calculate_holding(ticker, holding)
        for ticker, holding in sorted(portfolio.items())
    ]


def display_portfolio(portfolio):
    if not portfolio:
        print("\nYour portfolio is currently empty.")
        return

    report = get_portfolio_report(portfolio)

    print("\n" + "=" * 105)
    print("INVESTMENT PORTFOLIO")
    print("=" * 105)
    print(
        f"{'TICKER':<10}{'SHARES':>10}{'BUY PRICE':>13}"
        f"{'CURRENT':>13}{'INVESTED':>15}{'MARKET VALUE':>16}"
        f"{'GAIN/LOSS':>15}{'RETURN %':>12}"
    )
    print("-" * 105)

    total_invested = 0
    total_market_value = 0

    for item in report:
        total_invested += item["invested"]
        total_market_value += item["market_value"]

        print(
            f"{item['ticker']:<10}"
            f"{item['shares']:>10.2f}"
            f"{item['buy_price']:>13.2f}"
            f"{item['current_price']:>13.2f}"
            f"{item['invested']:>15.2f}"
            f"{item['market_value']:>16.2f}"
            f"{item['gain_loss']:>15.2f}"
            f"{item['percentage']:>12.2f}"
        )

    total_gain_loss = total_market_value - total_invested
    total_percentage = (
        total_gain_loss / total_invested * 100 if total_invested else 0
    )

    print("-" * 105)
    print(f"Total invested capital : {total_invested:,.2f}")
    print(f"Current market value   : {total_market_value:,.2f}")
    print(f"Total gain / loss      : {total_gain_loss:,.2f}")
    print(f"Overall return         : {total_percentage:.2f}%")
    print("=" * 105)
    print("Note: Prices are the values entered by you, not live market quotes.")


def export_summary(portfolio):
    if not portfolio:
        print("\nThere are no holdings to export.")
        return

    report = get_portfolio_report(portfolio)
    total_invested = sum(item["invested"] for item in report)
    total_market_value = sum(item["market_value"] for item in report)
    total_gain_loss = total_market_value - total_invested
    total_percentage = (
        total_gain_loss / total_invested * 100 if total_invested else 0
    )

    fieldnames = [
        "ticker", "shares", "buy_price", "current_price",
        "invested", "market_value", "gain_loss", "percentage",
        "last_updated"
    ]

    try:
        with SUMMARY_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for item in report:
                writer.writerow(item)

            writer.writerow({})
            writer.writerow({
                "ticker": "PORTFOLIO TOTAL",
                "invested": round(total_invested, 2),
                "market_value": round(total_market_value, 2),
                "gain_loss": round(total_gain_loss, 2),
                "percentage": round(total_percentage, 2)
            })

        print(f"\nPortfolio summary exported to: {SUMMARY_FILE}")
    except OSError as error:
        print(f"Could not export CSV file: {error}")


def show_top_performers(portfolio):
    if not portfolio:
        print("\nYour portfolio is currently empty.")
        return

    report = get_portfolio_report(portfolio)
    report.sort(key=lambda item: item["percentage"], reverse=True)

    print("\nPORTFOLIO PERFORMANCE RANKING")
    print("-" * 45)
    for position, item in enumerate(report, start=1):
        print(
            f"{position}. {item['ticker']:<10} "
            f"{item['percentage']:>8.2f}% "
            f"({item['gain_loss']:+.2f})"
        )


def main():
    portfolio = load_portfolio()

    print("\n" + "=" * 48)
    print("          INVESTMENT PORTFOLIO TRACKER")
    print("=" * 48)

    while True:
        print("\nMAIN MENU")
        print("1. Add stock holding")
        print("2. Update stock holding")
        print("3. Remove stock holding")
        print("4. View portfolio and profit/loss")
        print("5. View performance ranking")
        print("6. Export portfolio summary to CSV")
        print("7. Exit")

        choice = input("\nChoose an option (1-7): ").strip()

        if choice == "1":
            add_holding(portfolio)
        elif choice == "2":
            update_holding(portfolio)
        elif choice == "3":
            remove_holding(portfolio)
        elif choice == "4":
            display_portfolio(portfolio)
        elif choice == "5":
            show_top_performers(portfolio)
        elif choice == "6":
            export_summary(portfolio)
        elif choice == "7":
            save_portfolio(portfolio)
            print("\nYour portfolio has been saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 7.")


if __name__ == "__main__":
    main()
