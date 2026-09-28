import re
import json
from datetime import datetime


# ==================================================
# LOAD CATEGORY KEYWORDS
# ==================================================

with open(
    "config/category_keywords.json",
    "r",
    encoding="utf-8"
) as file:
    keywords = json.load(file)


# ==================================================
# EXTRACT MERCHANT
# ==================================================

def extract_merchant(text):

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    if not lines:
        return "Unknown"

    ignored_words = [
        "receipt",
        "invoice",
        "bill",
        "statement of account",
        "date",
        "dated",
        "total",
        "amount",
        "cash",
        "thank",
        "signature",
        "tin",
        "vat",
        "patient",
        "address",
        "telephone",
        "room no",
        "date admitted",
        "date discharge",
        "responsible party",
        "attending physician",
        "hospital bills",
        "charges",
        "healing with passion",
        "caring with compassion"
    ]

    candidates = []

    for line in lines:

        clean_line = line.strip()
        lower_line = clean_line.lower()

        # Ignore short OCR garbage
        if len(clean_line) < 8:
            continue

        # Ignore unwanted information
        if any(
            word in lower_line
            for word in ignored_words
        ):
            continue

        # Count letters and numbers
        letter_count = sum(
            char.isalpha()
            for char in clean_line
        )

        digit_count = sum(
            char.isdigit()
            for char in clean_line
        )

        if letter_count < 5:
            continue

        # Ignore lines containing too many numbers
        if digit_count > letter_count:
            continue

        word_count = len(clean_line.split())

        alpha_ratio = (
            letter_count / len(clean_line)
        )

        score = 0

        # Business names often have multiple words
        if word_count >= 4:
            score += 5
        elif word_count == 3:
            score += 4
        elif word_count == 2:
            score += 3

        # Longer names
        if letter_count >= 25:
            score += 5
        elif letter_count >= 15:
            score += 3
        elif letter_count >= 10:
            score += 1

        # Mostly alphabetic
        if alpha_ratio >= 0.80:
            score += 4

        candidates.append(
            (
                score,
                letter_count,
                clean_line
            )
        )

    if not candidates:
        return "Unknown"

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1]
        ),
        reverse=True
    )

    return candidates[0][2]


# ==================================================
# EXTRACT DATE
# ==================================================

def extract_date(text):

    patterns = [

        # 24/09/2026
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",

        # 24-09-2026
        r"\b\d{1,2}-\d{1,2}-\d{4}\b",

        # 2026-09-24
        r"\b\d{4}-\d{1,2}-\d{1,2}\b",

        # 24/09/26
        r"\b\d{1,2}/\d{1,2}/\d{2}\b",

        # 24-09-26
        r"\b\d{1,2}-\d{1,2}-\d{2}\b",

        # May 16, 2019
        r"\b[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}\b"
    ]

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%d-%m-%y",
        "%B %d, %Y",
        "%b %d, %Y"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        date_str = match.group()

        for fmt in formats:

            try:

                date = datetime.strptime(
                    date_str,
                    fmt
                )

                return date.strftime(
                    "%Y-%m-%d"
                )

            except ValueError:
                pass

    return None


# ==================================================
# EXTRACT AMOUNT
# ==================================================

def extract_amount(text):

    # --------------------------------------------------
    # 1. TOTAL / GRAND TOTAL / AMOUNT DUE
    # --------------------------------------------------

    total_patterns = [

        r"(?:TOTAL|GRAND\s+TOTAL|AMOUNT\s+DUE)"
        r"\s*[:\-]?\s*₹?\s*"
        r"(\d+(?:,\d{3})*(?:\.\d{1,2})?)",

        r"(?:TOTAL|GRAND\s+TOTAL|AMOUNT\s+DUE)"
        r"\s+"
        r"(\d+(?:,\d{3})*(?:\.\d{1,2})?)"
    ]

    for pattern in total_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            try:

                value = match.group(1)

                value = value.replace(
                    ",",
                    ""
                )

                return float(value)

            except ValueError:
                pass


    # --------------------------------------------------
    # 2. CURRENCY VALUES
    # --------------------------------------------------

    currency_pattern = (
        r"(?:₹|Rs\.?|INR)"
        r"\s*"
        r"(\d+(?:,\d{3})*(?:\.\d{1,2})?)"
    )

    matches = re.findall(
        currency_pattern,
        text,
        re.IGNORECASE
    )

    if matches:

        values = []

        for value in matches:

            try:

                values.append(
                    float(
                        value.replace(
                            ",",
                            ""
                        )
                    )
                )

            except ValueError:
                pass

        if values:
            return max(values)


    # --------------------------------------------------
    # 3. DECIMAL VALUES
    # --------------------------------------------------

    decimal_pattern = (
        r"\b"
        r"\d+(?:,\d{3})*"
        r"\.\d{1,2}"
        r"\b"
    )

    matches = re.findall(
        decimal_pattern,
        text
    )

    if matches:

        values = []

        for value in matches:

            try:

                values.append(
                    float(
                        value.replace(
                            ",",
                            ""
                        )
                    )
                )

            except ValueError:
                pass

        if values:
            return max(values)


    # --------------------------------------------------
    # 4. INTEGER AFTER TOTAL
    # --------------------------------------------------

    integer_total_pattern = (
        r"(?:TOTAL|GRAND\s+TOTAL|AMOUNT\s+DUE)"
        r"\s*[:\-]?\s*"
        r"(\d{1,6})"
    )

    match = re.search(
        integer_total_pattern,
        text,
        re.IGNORECASE
    )

    if match:

        try:
            return float(match.group(1))

        except ValueError:
            pass

    return None


# ==================================================
# EXTRACT CATEGORY
# ==================================================

def get_category(text):

    text_lower = text.lower()

    for category, words in keywords.items():

        for word in words:

            if word.lower() in text_lower:

                return category

    return "Other"