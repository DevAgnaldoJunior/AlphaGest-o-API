from dataclasses import dataclass

import pymupdf


@dataclass
class ResultadoExtracaoPdf:
    text: str
    pages: int


@dataclass
class PalavraPdf:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str


@dataclass
class LinhaPdf:
    y: float
    words: list[PalavraPdf]

    @property
    def text(self) -> str:
        ordered_words = sorted(
            self.words,
            key=lambda word: word.x0,
        )

        return " ".join(
            word.text
            for word in ordered_words
        )


@dataclass
class LinhaDocumento:
    page: int
    y: float
    text: str


def extrair_palavras_da_pagina(
    page: pymupdf.Page,
) -> list[PalavraPdf]:

    raw_words = page.get_text(
        "words",
        sort=True,
    )

    words: list[PalavraPdf] = []

    for raw_word in raw_words:
        word = PalavraPdf(
            x0=raw_word[0],
            y0=raw_word[1],
            x1=raw_word[2],
            y1=raw_word[3],
            text=raw_word[4],
        )

        words.append(word)

    return words


def agrupar_palavras_em_linhas(
    words: list[PalavraPdf],
    tolerance: float = 3.0,
) -> list[LinhaPdf]:

    lines: list[LinhaPdf] = []

    ordered_words = sorted(
        words,
        key=lambda word: (
            word.y0,
            word.x0,
        ),
    )

    for word in ordered_words:
        word_y = (
            word.y0 + word.y1
        ) / 2

        matching_line: LinhaPdf | None = None

        for line in reversed(lines[-3:]):
            if abs(line.y - word_y) <= tolerance:
                matching_line = line
                break

        if matching_line:
            matching_line.words.append(word)

            matching_line.y = sum(
                (
                    item.y0 + item.y1
                ) / 2
                for item in matching_line.words
            ) / len(matching_line.words)

        else:
            lines.append(
                LinhaPdf(
                    y=word_y,
                    words=[word],
                )
            )

    return lines


def extrair_texto_do_pdf(
    content: bytes,
) -> ResultadoExtracaoPdf:

    document = pymupdf.open(
        stream=content,
        filetype="pdf",
    )

    pages_text: list[str] = []

    try:
        number_of_pages = len(document)

        for page in document:
            text = page.get_text(
                "text",
                sort=True,
            )

            pages_text.append(text)

    finally:
        document.close()

    return ResultadoExtracaoPdf(
        text="\n".join(pages_text),
        pages=number_of_pages,
    )


def extrair_linhas_do_pdf(
    content: bytes,
) -> list[LinhaDocumento]:

    document = pymupdf.open(
        stream=content,
        filetype="pdf",
    )

    document_lines: list[LinhaDocumento] = []

    try:
        for page_index, page in enumerate(
            document,
            start=1,
        ):
            words = extrair_palavras_da_pagina(
                page
            )

            lines = agrupar_palavras_em_linhas(
                words
            )

            for line in lines:
                document_lines.append(
                    LinhaDocumento(
                        page=page_index,
                        y=line.y,
                        text=line.text,
                    )
                )

    finally:
        document.close()

    return document_lines