# Bambu Lab Boosts Tool (BLBT)

A fast and friendly command-line tool to calculate the **gift card value of your Makerworld boosts**,  
using **live exchange rates** pulled automatically from public APIs.  

## ✨ Features

✅ Uses live EUR-based exchange rates (no hardcoded FX)  
✅ Supports EU, USD, GBP, AUD, JPY, KRW, CNY, and more  
✅ Converts between currencies like PLN, CZK, SEK, etc.  
✅ Colorized CLI output for clarity  
✅ Fully open-source and MIT-licensed  


## 🚀 Installation

```bash
pip install blbt
```

## 💻 Usage

```bash
blbt 12000 -r EU -c PLN
```

### Examples

| Command | Description |
|----------|--------------|
| `blbt 5.5k -r AUD` | Calculates for 5.5 k boosts using Australian rate |
| `blbt 12000 -r EU -c PLN --verbose` | Converts EU base rate to PLN with detailed breakdown |
| `blbt 490 -us` | Uses the US store rate and shows results in USD |

## 🧩 Supported Regions

| Region | Base Currency | Example |
|---------|----------------|----------|
| EU | EUR | `blbt 1k -r EU -c PLN` |
| US | USD | `blbt 1.k -us` |
| GBP | GBP | `blbt 1.k -r GBP` |
| JPY | JPY | `blbt 1k -r JPY` |
| KRW | KRW | `blbt 1k -r KRW` |
| AUD | AUD | `blbt 1k -r AUD` |
| CNY | CNY | `blbt 1k -r CNY` |

## ⚙️ Developer Notes

To run from source:

```bash
python -m blbt 12000 -r EU -c PLN
```

The program automatically retrieves live rates from:
- [api.exchangerate.host](https://api.exchangerate.host)
- [open.er-api.com](https://open.er-api.com)

and caches nothing (always fresh data).

## 🧠 License

[MIT License](MIT) © 2025 thefilipcom4607

