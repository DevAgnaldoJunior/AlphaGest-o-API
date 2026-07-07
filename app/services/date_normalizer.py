import re
from datetime import date


MONTHS = {
    "JAN": 1,

    "FEV": 2,
    "FEB": 2,

    "MAR": 3,

    "ABR": 4,
    "APR": 4,

    "MAI": 5,
    "MAY": 5,

    "JUN": 6,

    "JUL": 7,

    "AGO": 8,
    "AUG": 8,

    "SET": 9,
    "SEP": 9,

    "OUT": 10,
    "OCT": 10,

    "NOV": 11,

    "DEZ": 12,
    "DEC": 12,
}


MONTH_NAMES = {
    1: "JAN",
    2: "FEV",
    3: "MAR",
    4: "ABR",
    5: "MAI",
    6: "JUN",
    7: "JUL",
    8: "AGO",
    9: "SET",
    10: "OUT",
    11: "NOV",
    12: "DEZ",
}


def converter_mes_para_numero(
    month: str,
) -> int | None:

    normalized_month = (
        month
        .strip()
        .upper()
    )

    return MONTHS.get(
        normalized_month
    )


def normalizar_data_da_transacao(
    date_text: str,
    due_date: str | None,
    period_start: str | None,
    period_end: str | None,
) -> date | None:

    if due_date is None:
        return None

    transaction_match = re.fullmatch(
        r"(\d{2})\s+([A-ZÀ-Ú]{3})",
        date_text.strip().upper(),
    )

    due_date_match = re.fullmatch(
        r"(\d{2})\s+([A-ZÀ-Ú]{3})\s+(\d{4})",
        due_date.strip().upper(),
    )

    if not transaction_match:
        return None

    if not due_date_match:
        return None

    transaction_day = int(
        transaction_match.group(1)
    )

    transaction_month = converter_mes_para_numero(
        transaction_match.group(2)
    )

    due_year = int(
        due_date_match.group(3)
    )

    if transaction_month is None:
        return None

    transaction_year = due_year

    if period_start and period_end:

        start_match = re.fullmatch(
            r"\d{2}\s+([A-ZÀ-Ú]{3})",
            period_start.strip().upper(),
        )

        end_match = re.fullmatch(
            r"\d{2}\s+([A-ZÀ-Ú]{3})",
            period_end.strip().upper(),
        )

        if start_match and end_match:

            start_month = converter_mes_para_numero(
                start_match.group(1)
            )

            end_month = converter_mes_para_numero(
                end_match.group(1)
            )

            if (
                start_month is not None
                and end_month is not None
                and start_month > end_month
                and transaction_month >= start_month
            ):
                transaction_year -= 1

    try:
        return date(
            year=transaction_year,
            month=transaction_month,
            day=transaction_day,
        )

    except ValueError:
        return None


def formatar_data_para_texto(
    transaction_date: date,
) -> str:

    month = MONTH_NAMES[
        transaction_date.month
    ]

    return (
        f"{transaction_date.day:02d} "
        f"{month}"
    )