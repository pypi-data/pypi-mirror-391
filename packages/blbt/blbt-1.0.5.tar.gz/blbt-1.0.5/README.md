# BLBT - Bambu Lab Boosts Tool

A command-line utility to calculate the real-world gift card value of your Makerworld boosts across different regional stores.

![alt text](https://assets.thefilip.com/blbt.jpg)

## Installation

```bash
pip install blbt
```

## Quick Start

```bash
# Calculate value for 5,500 boosts using Australian store rates
blbt 5.5k -r AUD

# Calculate value for EU store, converted to Polish Zloty
blbt 12000 -r EU -c PLN

# Calculate value using US store rates
blbt 490 -us
```

## Features

- 💰 **Multi-Region Support**: Calculate values for 13+ different regional stores
- 🌍 **Live Exchange Rates**: Automatically fetches current exchange rates for accurate conversions
- 🎨 **Colored Output**: Clear, easy-to-read terminal output with color coding
- 📊 **Verbose Mode**: Detailed calculation breakdowns when you need them
- ⚡ **Flexible Input**: Accept boost counts as regular numbers (2300) or with k suffix (2.3k)

## Usage

### Basic Syntax

```bash
blbt <boosts> [options]
```

### Arguments

- `boosts` (required): Number of boosts received
  - Regular numbers: `2300`, `15000`
  - K notation: `2.3k`, `15k`

### Options

**Output Mode:**
- `-v`, `--verbose`: Display full calculation breakdown
- `-us`, `--us-store`: Use US store rate and output in USD

**Region & Currency:**
- `-r`, `--region <CODE>`: Set store pricing region (default: EU)
- `-c`, `--currency <CODE>`: Convert EU rate to specified EU currency

## Supported Regions

### Local Currency Gift Cards
| Region Code | Store | Currency | Points per Card | Card Value |
|-------------|-------|----------|-----------------|------------|
| `EU` | EU | EUR | 524 | €40.00 |
| `GBP` | UK | GBP | 535 | £35.00 |
| `CAD` | Canada | CAD | 504 | C$55.00 |
| `AUD` | Australia | AUD | 511 | A$65.00 |
| `JPY` | Japan | JPY | 502 | ¥5,300 |
| `KRW` | South Korea | KRW | 490 | ₩58,000 |
| `CNY` | China | CNY | 490 | ¥284.00 |

### USD-Pegged Gift Cards
These regions use $40 USD equivalent gift cards:

| Region Code | Store |
|-------------|-------|
| `SGD` | Singapore |
| `THB` | Thailand |
| `MYR` | Malaysia |
| `HKD` | Hong Kong |
| `MOP` | Macao |
| `TWD` | Taiwan |
| `US` | United States |

All USD-pegged regions use **490 points per card**.

## EU Currency Conversions

When using the EU region (`-r EU`), you can convert the output to these currencies:

- `PLN` - Polish Zloty
- `CZK` - Czech Koruna
- `HUF` - Hungarian Forint
- `DKK` - Danish Krone
- `SEK` - Swedish Krona
- `EUR` - Euro (default)

**Note:** The `-c` flag only works with the EU region.

## Examples

### Example 1: Quick Check
```bash
blbt 5500 -r AUD
```
Output: Final gift card value using Australian store rates

### Example 2: Detailed EU Calculation
```bash
blbt 12000 -r EU -c PLN --verbose
```
Output: Full breakdown with conversion to Polish Zloty

### Example 3: US Store
```bash
blbt 3.5k -us
```
Output: Value in USD using US store rates

### Example 4: UK Store
```bash
blbt 2140 -r GBP -v
```
Output: Detailed calculation using UK (GBP) rates

### Example 5: Japanese Store
```bash
blbt 10k -r JPY
```
Output: Value in Japanese Yen

## Understanding the Output

### Standard Output
```
==================================================
💰 Makerworld Reward Calculation
Store Region: EU | Output Currency: EUR
==================================================
--- Configuration ---
Points per Card: 524
Card Value: 40.00 EUR
---------------------

🎉 Final Value: 160.00 € from 2,300 boosts (4 gift cards).
```

### Verbose Output
Includes:
- Total points/boosts count
- Number of whole gift cards you can purchase
- Remaining points toward next card (if any)
- Step-by-step calculation breakdown
- Exchange rate information (when applicable)

## Exchange Rates

BLBT automatically fetches live exchange rates from:
1. Primary: exchangerate.host
2. Fallback: open.er-api.com

Exchange rates are relative to EUR as the base currency. If both APIs are unavailable, the tool will display an error message.

## How It Works

1. **Points System**: Makerworld uses a points system where boosts equal points (1 boost = 1 point)
2. **Regional Rates**: Different stores have different point requirements and gift card values
3. **Whole Gift Cards Only**: BLBT uses integer division to calculate only the number of complete gift cards you can purchase (e.g., 2,300 points ÷ 524 = 4 gift cards, not 4.39)
4. **Total Value Calculation**: Total value = number of whole gift cards × card value
5. **Currency Conversion**: When needed, live exchange rates convert the final value between currencies

## Error Handling

The tool provides clear error messages for:
- Invalid boost numbers
- Unknown region codes
- Missing exchange rates
- Invalid currency conversions
- Network issues when fetching exchange rates

## Requirements

- Python 3.6+
- Internet connection (for live exchange rates)

## Dependencies

- `requests` - HTTP library for fetching exchange rates
- `colorama` - Cross-platform colored terminal output

## Contributing

Found a bug or have a feature request? Please open an issue on the GitHub repository.

## License

MIT

## Support

For questions or issues:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Note**: Store rates and point requirements are subject to change by Bambu Lab. This tool uses the rates as of the latest update.