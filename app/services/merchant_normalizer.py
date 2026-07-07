import unicodedata


MERCHANT_RULES = {
    "99": [
        "99 ride",
        "99app",
        "dl*99",
        "dl *99",
    ],

    "Uber": [
        "uber",
        "uberrides",
        "uber trip",
    ],

    "iFood": [
        "ifood",
        "ifood.com",
        "ifood com",
    ],

    "Shopee": [
        "shopee",
    ],

    "AliExpress": [
        "aliexpress",
    ],

    "Assaí": [
        "assai",
    ],

    "C&A": [
        "cea",
    ],
}


def normalizar_texto(
    text: str,
) -> str:

    normalized = unicodedata.normalize(
        "NFKD",
        text,
    )

    text_without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return (
        text_without_accents
        .lower()
        .strip()
    )


def normalizar_estabelecimento(
    description: str,
) -> str:

    normalized_description = normalizar_texto(
        description
    )

    for merchant, patterns in MERCHANT_RULES.items():

        for pattern in patterns:

            normalized_pattern = normalizar_texto(
                pattern
            )

            if normalized_pattern in normalized_description:
                return merchant

    clean_description = (
        description
        .split(" - Parcela")[0]
        .strip()
    )

    return clean_description