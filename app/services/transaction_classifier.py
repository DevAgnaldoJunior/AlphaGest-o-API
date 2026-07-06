import unicodedata


CATEGORY_RULES = {
    "Transporte": [
        "99 ride",
        "99app",
        "uber",
        "uber rides",
        "uber trip",
    ],
    "Alimentação": [
        "ifood",
        "restaurante",
        "food",
        "maisdelicia",
        "balas e doces",
        "bebidas",
        "mercadinho",
        "assai",
    ],
    "Compras": [
        "shopee",
        "aliexpress",
        "cea",
    ],
    "Combustível": [
        "posto",
        "gas",
        "gasolina",
        "combustivel",
    ],
    "Lazer": [
        "zigpay",
        "espaco cultural",
    ],
    "Serviços": [
        "telefonica",
        "papelaria",
    ],
}


def normalizar_texto(text: str) -> str:
    normalized = unicodedata.normalize(
        "NFKD",
        text,
    )

    text_without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return text_without_accents.lower().strip()


def categorizar_transacao(
    description: str,
    transaction_type: str,
) -> str:

    if transaction_type == "pagamento":
        return "Pagamento de fatura"

    if transaction_type == "financiamento":
        return "Financiamento"

    normalized_description = normalizar_texto(
        description
    )

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            normalized_keyword = normalizar_texto(
                keyword
            )

            if normalized_keyword in normalized_description:
                return category

    return "Outros"