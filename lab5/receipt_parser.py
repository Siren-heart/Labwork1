# Practice 5: Python RegEx receipt parser

import json
import re
from pathlib import Path


base_path = Path(__file__).resolve().parent
raw_file = base_path / "raw.txt"


def parse_money(value):
    normalized = value.replace(" ", "").replace(",", ".")
    return float(normalized)


def extract_prices(text):
    # Find values like 154,00 or 7 330,00.
    return [parse_money(price) for price in re.findall(r"\b\d[\d ]*,\d{2}\b", text)]


def extract_products(text):
    # Each item starts with "1." on its own line, followed by a name and price lines.
    pattern = (
        r"(?m)^(\d+)\.\s*\n"
        r"(.+)\n"
        r"([\d,]+)\s*x\s*([\d ]+,\d{2})\n"
        r"([\d ]+,\d{2})"
    )
    matches = re.findall(pattern, text)

    products = []
    for item_number, name, quantity, unit_price, line_total in matches:
        products.append(
            {
                "item_number": int(item_number),
                "name": name.strip(),
                "quantity": float(quantity.replace(",", ".")),
                "unit_price": parse_money(unit_price),
                "line_total": parse_money(line_total),
            }
        )
    return products


def extract_date_time(text):
    match = re.search(r"^Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})$", text, flags=re.MULTILINE)
    return {
        "date": match.group(1) if match else None,
        "time": match.group(2) if match else None,
    }


def extract_payment_method(text):
    payment_match = re.search(r"^(Банковская карта|Наличные):$", text, flags=re.MULTILINE)
    return payment_match.group(1) if payment_match else None


def extract_totals(text):
    card_match = re.search(r"^Банковская карта:\n([\d ]+,\d{2})$", text, flags=re.MULTILINE)
    total_match = re.search(r"^ИТОГО:\n([\d ]+,\d{2})$", text, flags=re.MULTILINE)
    vat_match = re.search(r"^в т\.ч\. НДС 12%:\n([\d ]+,\d{2})$", text, flags=re.MULTILINE)

    return {
        "paid_by_card": parse_money(card_match.group(1)) if card_match else None,
        "total": parse_money(total_match.group(1)) if total_match else None,
        "vat": parse_money(vat_match.group(1)) if vat_match else None,
    }


def extract_receipt_info(text):
    branch_match = re.search(r"^Филиал\s+(.+)$", text, flags=re.MULTILINE)
    bin_match = re.search(r"^БИН\s+(\d+)$", text, flags=re.MULTILINE)
    receipt_match = re.search(r"^Чек №(\d+)$", text, flags=re.MULTILINE)
    fiscal_match = re.search(r"^Фискальный признак:\n(\d+)$", text, flags=re.MULTILINE)

    return {
        "branch": branch_match.group(1) if branch_match else None,
        "bin": bin_match.group(1) if bin_match else None,
        "receipt_number": receipt_match.group(1) if receipt_match else None,
        "fiscal_sign": fiscal_match.group(1) if fiscal_match else None,
    }


def regex_examples(text):
    # re.split example: split into non-empty lines.
    lines = [line for line in re.split(r"\r?\n", text) if line.strip()]

    # re.sub example: normalize runs of spaces.
    cleaned_text = re.sub(r"[ ]{2,}", " ", text)

    # Special sequence examples.
    words = re.findall(r"\b\w+\b", text)
    product_codes = re.findall(r"\[RX\]", text)

    return {
        "line_count": len(lines),
        "word_sample": words[:12],
        "rx_mark_count": len(product_codes),
        "cleaned_preview": cleaned_text.splitlines()[:10],
    }


def build_summary(text):
    products = extract_products(text)
    totals = extract_totals(text)
    date_time = extract_date_time(text)
    payment_method = extract_payment_method(text)
    receipt_info = extract_receipt_info(text)
    all_prices = extract_prices(text)

    return {
        "receipt_info": {
            **receipt_info,
            "date": date_time["date"],
            "time": date_time["time"],
            "payment_method": payment_method,
        },
        "products": products,
        "product_names": [item["name"] for item in products],
        "all_prices_found": all_prices,
        "calculated_total_from_products": round(sum(item["line_total"] for item in products), 2),
        "totals": totals,
        "regex_examples": regex_examples(text),
    }


def main():
    text = raw_file.read_text(encoding="utf-8")
    summary = build_summary(text)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
