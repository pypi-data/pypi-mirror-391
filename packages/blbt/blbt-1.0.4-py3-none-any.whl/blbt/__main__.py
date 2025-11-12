import argparse
import sys
import requests
from colorama import init, Fore, Style
from typing import Dict, Tuple

# Initialize colorama for colored output
init(autoreset=True)

# --- ANSI Codes for Help Text ---
BOLD = '\033[1m'
GREEN_BOLD = '\033[32m\033[1m'
CYAN_BOLD = '\033[36m\033[1m'
RED_BOLD = '\033[31m\033[1m'
RESET = '\033[0m'

# --- Global Constants for Store Rates and Currency ---

# Store Points per Gift Card Value in Local Currency
# Format: {Rate/Region Code: (Points, Local Value, Store Country/Region, Base Currency)}
STORE_RATES: Dict[str, Tuple[int, float, str, str]] = {
    # Base Currency is EUR
    "EU": (524, 40.00, "EU", "EUR"),

    # Global Markets with Local Currency Gift Cards
    "GBP": (535, 35.00, "UK", "GBP"),
    "CAD": (504, 55.00, "CANADA", "CAD"),
    "AUD": (511, 65.00, "AUSTRALIA", "AUD"),
    "JPY": (502, 5300.00, "JAPAN", "JPY"),
    "KRW": (490, 58000.00, "S. KOREA", "KRW"),
    "CNY": (490, 284.00, "CHINA", "CNY"),

    # Markets with USD-pegged gift cards (Base Value is $40 USD)
    # Base Currency is USD
    "SGD": (490, 40.00, "SINGAPORE", "USD"),
    "THB": (490, 40.00, "THAILAND", "USD"),
    "MYR": (490, 40.00, "MALAYSIA", "USD"),
    "HKD": (490, 40.00, "HONG KONG", "USD"),
    "MOP": (490, 40.00, "MACAO", "USD"),
    "TWD": (490, 40.00, "TAIWAN", "USD"),

    # US store
    "US": (490, 40.00, "US", "USD"),
}

# Currencies that can be used with the -c flag (for EUR-based EU rate)
EU_CURRENCIES = ["PLN", "CZK", "HUF", "DKK", "SEK", "EUR"]

# Currencies requiring dynamic conversion (base: EUR or USD)
REQUIRED_RATES = set(
    [rate[3] for rate in STORE_RATES.values()] +  # All base currencies
    EU_CURRENCIES +  # All EU output currencies
    ["USD"]  # Ensure USD is available for EUR-to-USD conversion
)

# Currency Symbols for display
CURRENCY_SYMBOLS = {
    "PLN": "zł", "SEK": "kr", "EUR": "€", "USD": "$", "GBP": "£", "AUD": "A$",
    "CAD": "C$", "JPY": "¥", "KRW": "₩", "CNY": "¥", "SGD": "S$", "THB": "฿",
    "MYR": "RM", "HKD": "HK$", "MOP": "P", "TWD": "NT$", "CZK": "Kč", "HUF": "Ft",
    "DKK": "kr."
}


# ----------------------------------------------------------------------
## Dynamic Exchange Rate Retrieval
# ----------------------------------------------------------------------

def get_exchange_rates_dynamic(target_currencies: set) -> Dict[str, float]:
    """
    Fetch live exchange rates relative to EUR (1 EUR = X local currency).
    Tries exchangerate.host first, then open.er-api.com as fallback.
    """

    urls = [
        "https://api.exchangerate.host/latest?base=EUR",
        "https://open.er-api.com/v6/latest/EUR",
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Try to find the rates key — API formats differ
            if "rates" in data:
                rates_data = data["rates"]
            elif "result" in data and "rates" in data["result"]:
                rates_data = data["result"]["rates"]
            else:
                continue

            # Filter only required currencies
            rates = {k: v for k, v in rates_data.items() if k in target_currencies}

            # Always include EUR as base = 1.0
            rates["EUR"] = 1.0

            missing = target_currencies - rates.keys()
            if missing:
                print(f"⚠️  Warning: Missing rates for: {', '.join(sorted(missing))}")

            return rates

        except Exception as e:
            print(f"⚠️  Failed to get rates from {url}: {e}")

    # If all APIs fail
    print(f"\n{Fore.RED}{Style.BRIGHT}FATAL ERROR:{Style.RESET_ALL} Could not retrieve live rates from any source.")
    sys.exit(1)


# ----------------------------------------------------------------------
## Argument Parsing
# ----------------------------------------------------------------------

HELP_EPILOG = f"""
{GREEN_BOLD}Available Regions/Rates (use with -r):{RESET}
- {BOLD}Local Rates:{RESET} GBP, CAD, AUD, JPY, KRW, CNY
- {BOLD}USD-Card Regions:{RESET} SGD, THB, MYR, HKD, MOP, TWD
- {BOLD}Default Rates:{RESET} EU (Base EUR rate), US (Base USD rate)

{CYAN_BOLD}Available EU Currencies (use with -c):{RESET}
- {BOLD}For EU Rate Only:{RESET} {' '.join(EU_CURRENCIES)}

Examples:
  # 1. Quick check for 5.5k boosts using the {BOLD}Australian (AUD){RESET} store rate
  blbt 5.5k -r AUD

  # 2. Detailed check for {BOLD}EU rate{RESET} but converted to {BOLD}Polish Zloty (PLN){RESET}
  blbt 12000 -r EU -c PLN --verbose

  # 3. Use the {BOLD}US rate{RESET} and output in USD ($)
  blbt 490 -us
"""


def parse_input() -> Tuple[float, bool, str, str, bool]:
    """Parse CLI arguments and return processed values."""
    parser = argparse.ArgumentParser(
        description="Calculate the total gift card value of Makerworld boosts.",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "boosts",
        type=str,
        help=f"{BOLD}REQUIRED:{RESET} Total number of boosts received (e.g., 2300 or 3.2k)."
    )
    mode_group = parser.add_argument_group('Output Mode & Store')
    mode_group.add_argument("-v", "--verbose", action="store_true", help="Display the full calculation breakdown.")
    mode_group.add_argument("-us", "--us-store", action="store_true",
                            help=f"Use {BOLD}US store rate{RESET} and output in {BOLD}USD ($){RESET}.")
    region_group = parser.add_argument_group('Region & Currency')
    region_group.add_argument("-r", "--region", default="EU",
                              help=f"Set the Store's Pricing Region (e.g., 'GBP', 'JPY'). Default: 'EU'")
    region_group.add_argument("-c", "--currency", default="",
                              help=f"OPTIONAL: Convert the final value to this EU currency when using the {BOLD}EU region rate{RESET}.")

    args = parser.parse_args()

    # Process the boost count
    raw = args.boosts.strip()
    try:
        if raw.lower().endswith("k"):
            value = float(raw[:-1]) * 1000
            if args.verbose:
                print(f"{Fore.YELLOW}Interpreting '{raw}' as {value:,.0f} boosts.")
        else:
            value = float(raw)

        if value < 0:
            raise ValueError("Boost count must be a non-negative number.")

        return value, args.us_store, args.region.upper(), args.currency.upper(), args.verbose

    except ValueError as e:
        print(f"{Fore.RED}Error: '{raw}' is not a valid number (e.g. 2300 or 3.2k). Details: {e}")
        sys.exit(1)


# ----------------------------------------------------------------------
## Core Logic
# ----------------------------------------------------------------------

def convert_currency(value: float, from_curr: str, to_curr: str, rates_eur: Dict[str, float]) -> Tuple[float, float]:
    """
    Converts a value from one currency to another using EUR as the base.

    :param value: The amount to convert.
    :param from_curr: The source currency code.
    :param to_curr: The target currency code.
    :param rates_eur: Dictionary of rates relative to EUR (1 EUR = X).
    :return: (converted_value, effective_exchange_rate)
    """
    if from_curr == to_curr:
        return value, 1.0

    if from_curr not in rates_eur or to_curr not in rates_eur:
        raise ValueError(f"Missing exchange rate for conversion: need rates for {from_curr} and {to_curr}.")

    # Convert to EUR, then to target currency
    value_in_eur = value / rates_eur[from_curr]
    converted_value = value_in_eur * rates_eur[to_curr]

    # Calculate the effective exchange rate
    effective_rate = rates_eur[to_curr] / rates_eur[from_curr]

    return converted_value, effective_rate


def calculate_value(boosts: float, us_store: bool, region_code: str, currency_code: str, verbose: bool):
    """Calculates the final gift card value based on selected region/currency."""

    # 0. Get Dynamic Rates
    try:
        EXCHANGE_RATES_EUR = get_exchange_rates_dynamic(REQUIRED_RATES)
        if not EXCHANGE_RATES_EUR:
            raise Exception("Rate dictionary is empty.")
    except Exception as e:
        print(f"\n{RED_BOLD}FATAL ERROR: Could not retrieve dynamic exchange rates!{RESET}")
        print(f"Please check your internet connection. Error: {e}")
        sys.exit(1)

    # 1. Determine the Rate and Currencies
    if us_store:
        rate_key = "US"
        output_currency = "USD"
    else:
        if region_code not in STORE_RATES:
            print(
                f"{Fore.RED}Error: Invalid region code '{region_code}'. Available regions: {', '.join(STORE_RATES.keys())}")
            sys.exit(1)

        rate_key = region_code

        # Determine final output currency
        if rate_key == "EU" and currency_code and currency_code in EU_CURRENCIES:
            output_currency = currency_code
        else:
            output_currency = STORE_RATES[rate_key][3]

    points_needed, card_value_local, store_name, base_currency = STORE_RATES[rate_key]

    # Final check for USD-pegged regions
    if base_currency == "USD" and output_currency in ["SGD", "THB", "MYR", "HKD", "MOP", "TWD"]:
        output_currency = "USD"

    # 2. Calculate using integer division for whole gift cards
    total_points = int(boosts)  # Boosts = Points
    num_gift_cards = total_points // points_needed  # Integer division
    remaining_points = total_points % points_needed

    # Total value in base currency (whole gift cards only)
    total_value_base = num_gift_cards * card_value_local

    if verbose:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}--- Calculation Details ---{Style.RESET_ALL}")
        print(
            f"{Fore.MAGENTA}Store Rate: {store_name} ({points_needed} points = {card_value_local:.2f} {base_currency}){Style.RESET_ALL}")
        print("-" * 50)
        print(f"1. Total Points: {total_points:,} boosts")
        print(f"2. Gift Cards: {total_points:,} points ÷ {points_needed} = {num_gift_cards} gift cards")
        if remaining_points > 0:
            print(f"   Remaining: {remaining_points} points ({remaining_points}/{points_needed} toward next card)")
        print(
            f"3. Total Value ({base_currency}): {num_gift_cards} cards × {card_value_local:.2f} = {total_value_base:,.2f} {base_currency}")

    # 3. Conversion to Final Output Currency
    try:
        final_value, effective_rate = convert_currency(
            total_value_base, base_currency, output_currency, EXCHANGE_RATES_EUR
        )
    except ValueError as e:
        print(f"\n{Fore.RED}Conversion Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # 4. Output Summary
    currency_symbol = CURRENCY_SYMBOLS.get(output_currency, output_currency)

    print("\n" + "=" * 50)
    print(f"{Style.BRIGHT}💰 Makerworld Reward Calculation")
    print(f"Store Region: {store_name} | Output Currency: {output_currency}")
    print("=" * 50)

    print(f"{Fore.YELLOW}--- Configuration ---")
    print(f"Points per Card: {points_needed}")
    print(f"Card Value: {card_value_local:.2f} {base_currency}")

    if base_currency != output_currency:
        print(f"Effective Exchange Rate: 1 {base_currency} = {effective_rate:.4f} {output_currency}")

    print("---------------------")

    final_value_str = f"{final_value:,.2f} {currency_symbol}"

    print(
        f"\n{Fore.GREEN}{Style.BRIGHT}🎉 Final Value: {final_value_str} from {boosts:,.0f} boosts ({num_gift_cards} gift cards).\n")

    if verbose and base_currency != output_currency:
        print(f"{Fore.YELLOW}NOTE:{Style.RESET_ALL} Conversion performed using dynamic rates relative to EUR.")


def main():
    """Main execution function."""
    try:
        boosts, us_store, region_code, currency_code, verbose = parse_input()

        # Enforce -c rule
        if currency_code and (region_code != "EU" or us_store):
            print(
                f"{Fore.RED}Error: The -c/--currency flag can only be used when the -r/--region is set to 'EU' and -us is not used.")
            sys.exit(1)

        calculate_value(boosts, us_store, region_code, currency_code, verbose)

    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()