from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.database.database import obter_sessao

from app.services.user_login.auth_service import (
    obter_usuario_autenticado,
)

from app.schemas.invoice import (
    RespostaDetalheFatura,
    RespostaExtracaoFatura,
    RespostaFaturaLista,
    RespostaFaturaSalva,
    RespostaLinhaPdf,
    RespostaLinhasFatura,
    RespostaMetadadosFatura,
    RespostaResumoCategoria,
    RespostaResumoTransacoes,
    RespostaTransacoesFatura,
    RespostaExclusaoFatura,
)

from app.schemas.transaction import (
    AtualizacaoTransacao,
    RespostaExclusaoTransacao,
    RespostaTransacao,
)

from app.services.invoice_parser import (
    TransacaoAnalisada,
    analisar_transacoes,
    extrair_metadados_da_fatura,
    gerar_resumo_das_transacoes,
    gerar_resumo_por_categoria,
)

from app.services.invoice_repository import (
    buscar_fatura_por_id,
    listar_faturas,
    salvar_fatura,
)

from app.services.pdf_extractor import (
    extrair_linhas_do_pdf,
    extrair_texto_do_pdf,
)

from app.services.transaction_repository import (
    atualizar_transacao,
    buscar_transacao_por_id,
    excluir_transacao,
    identificar_origem_da_transacao,
)


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    dependencies=[
        Depends(
            obter_usuario_autenticado
        )
    ],
)


@router.post(
    "/extract",
    response_model=RespostaExtracaoFatura,
)
async def extrair_fatura(
    file: UploadFile = File(...),
) -> RespostaExtracaoFatura:

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado deve ser um PDF.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio.",
        )

    try:
        extraction = extrair_texto_do_pdf(
            content
        )

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Não foi possível processar o PDF.",
        )

    return RespostaExtracaoFatura(
        filename=file.filename or "arquivo.pdf",
        content_type=file.content_type,
        size=len(content),
        pages=extraction.pages,
        text=extraction.text,
    )


@router.post(
    "/inspect-lines",
    response_model=RespostaLinhasFatura,
)
async def inspecionar_linhas_da_fatura(
    file: UploadFile = File(...),
) -> RespostaLinhasFatura:

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado deve ser um PDF.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio.",
        )

    try:
        document_lines = extrair_linhas_do_pdf(
            content
        )

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Não foi possível processar o PDF.",
        )

    response_lines = [
        RespostaLinhaPdf(
            page=line.page,
            y=round(line.y, 2),
            text=line.text,
        )
        for line in document_lines
    ]

    return RespostaLinhasFatura(
        filename=file.filename or "arquivo.pdf",
        lines=response_lines,
    )


@router.post(
    "/parse",
    response_model=RespostaTransacoesFatura,
)
async def analisar_fatura(
    file: UploadFile = File(...),
) -> RespostaTransacoesFatura:

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado deve ser um PDF.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio.",
        )

    try:
        document_lines = extrair_linhas_do_pdf(
            content
        )

        parsed_transactions = analisar_transacoes(
            document_lines
        )

        invoice_metadata = extrair_metadados_da_fatura(
            document_lines
        )

        transaction_summary = gerar_resumo_das_transacoes(
            parsed_transactions
        )

        category_summary = gerar_resumo_por_categoria(
            parsed_transactions
        )

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Não foi possível analisar a fatura.",
        )

    transactions = [
        RespostaTransacao(
            id=None,
            invoice_id=None,
            date=transaction.date,
            transaction_date=None,
            card=transaction.card,
            description=transaction.description,
            amount=transaction.amount,
            type=transaction.type,
            category=transaction.category,
            origin="fatura",
            page=transaction.page,
        )
        for transaction in parsed_transactions
    ]

    categories = [
        RespostaResumoCategoria(
            category=item["category"],
            total_transactions=item["total_transactions"],
            total_amount=item["total_amount"],
        )
        for item in category_summary
    ]

    return RespostaTransacoesFatura(
        filename=file.filename or "arquivo.pdf",

        invoice=RespostaMetadadosFatura(
            total_amount=invoice_metadata.total_amount,
            due_date=invoice_metadata.due_date,
            period_start=invoice_metadata.period_start,
            period_end=invoice_metadata.period_end,
        ),

        summary=RespostaResumoTransacoes(
            compra=transaction_summary["compra"],
            estorno=transaction_summary["estorno"],
            pagamento=transaction_summary["pagamento"],
            financiamento=transaction_summary["financiamento"],
        ),

        category_summary=categories,

        total_transactions=len(
            transactions
        ),

        transactions=transactions,
    )


@router.post(
    "/import",
    response_model=RespostaFaturaSalva,
)
async def importar_fatura(
    file: UploadFile = File(...),
    session: Session = Depends(obter_sessao),
) -> RespostaFaturaSalva:

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado deve ser um PDF.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio.",
        )

    try:
        document_lines = extrair_linhas_do_pdf(
            content
        )

        parsed_transactions = analisar_transacoes(
            document_lines
        )

        invoice_metadata = extrair_metadados_da_fatura(
            document_lines
        )

        saved_invoice = salvar_fatura(
            session=session,
            filename=file.filename or "arquivo.pdf",
            metadata=invoice_metadata,
            transactions=parsed_transactions,
        )

    except Exception:
        session.rollback()

        raise HTTPException(
            status_code=422,
            detail="Não foi possível importar a fatura.",
        )

    return RespostaFaturaSalva(
        id=saved_invoice.id,
        filename=saved_invoice.filename,
        total_amount=saved_invoice.total_amount,
        due_date=saved_invoice.due_date,
        total_transactions=len(
            saved_invoice.transactions
        ),
    )


@router.get(
    "",
    response_model=list[RespostaFaturaLista],
)
def consultar_faturas(
    session: Session = Depends(obter_sessao),
) -> list[RespostaFaturaLista]:

    invoices = listar_faturas(
        session=session
    )

    return [
        RespostaFaturaLista(
            id=invoice.id,
            filename=invoice.filename,
            total_amount=invoice.total_amount,
            due_date=invoice.due_date,
            period_start=invoice.period_start,
            period_end=invoice.period_end,
            total_transactions=len(
                invoice.transactions
            ),
        )
        for invoice in invoices
    ]


@router.get("/{invoice_id}",response_model=RespostaDetalheFatura,)
def consultar_detalhes_da_fatura(
    invoice_id: int,
    session: Session = Depends(obter_sessao),
) -> RespostaDetalheFatura:

    invoice = buscar_fatura_por_id(
        session=session,
        invoice_id=invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Fatura não encontrada.",
        )

    parsed_transactions = [
        TransacaoAnalisada(
            date=transaction.date,
            card=transaction.card,
            description=transaction.description,
            amount=transaction.amount,
            type=transaction.type,
            category=transaction.category,
            page=transaction.page,
        )
        for transaction in invoice.transactions
    ]

    transaction_summary = gerar_resumo_das_transacoes(
        parsed_transactions
    )

    category_summary = gerar_resumo_por_categoria(
        parsed_transactions
    )

    transactions = [
        RespostaTransacao(
            id=transaction.id,
            invoice_id=transaction.invoice_id,
            date=transaction.date,
            transaction_date=transaction.transaction_date,
            card=transaction.card,
            description=transaction.description,
            amount=transaction.amount,
            type=transaction.type,
            category=transaction.category,
            origin=identificar_origem_da_transacao(
                transaction
            ),
            page=transaction.page,
        )
        for transaction in invoice.transactions
    ]

    categories = [
        RespostaResumoCategoria(
            category=item["category"],
            total_transactions=item["total_transactions"],
            total_amount=item["total_amount"],
        )
        for item in category_summary
    ]

    return RespostaDetalheFatura(
        id=invoice.id,

        filename=invoice.filename,

        invoice=RespostaMetadadosFatura(
            total_amount=invoice.total_amount,
            due_date=invoice.due_date,
            period_start=invoice.period_start,
            period_end=invoice.period_end,
        ),

        summary=RespostaResumoTransacoes(
            compra=transaction_summary["compra"],
            estorno=transaction_summary["estorno"],
            pagamento=transaction_summary["pagamento"],
            financiamento=transaction_summary["financiamento"],
        ),

        category_summary=categories,

        total_transactions=len(
            transactions
        ),

        transactions=transactions,
    )




@router.delete(
    "/{invoice_id}",
    response_model=RespostaExclusaoFatura,
)
def excluir_fatura(
    invoice_id: int,
    session: Session = Depends(obter_sessao),
) -> RespostaExclusaoFatura:

    invoice = buscar_fatura_por_id(
        session=session,
        invoice_id=invoice_id,
    )

    if invoice is None:

        raise HTTPException(
            status_code=404,
            detail="Fatura não encontrada.",
        )


    total_transactions = len(
        invoice.transactions
    )


    try:

        for transaction in list(
            invoice.transactions
        ):

            session.delete(
                transaction
            )


        session.delete(
            invoice
        )


        session.commit()


    except Exception as error:

        session.rollback()


        print(
            f"Erro ao excluir fatura: {error}"
        )


        raise HTTPException(
            status_code=422,
            detail=(
                "Não foi possível excluir "
                "a fatura."
            ),
        )


    return RespostaExclusaoFatura(
        message=(
            "Fatura e transações vinculadas "
            "excluídas com sucesso."
        ),
        invoice_id=invoice_id,
        deleted_transactions=total_transactions,
    )




@router.patch(
    "/{invoice_id}/transactions/{transaction_id}",
    response_model=RespostaTransacao,
)
def editar_transacao(
    invoice_id: int,
    transaction_id: int,
    update_data: AtualizacaoTransacao,
    session: Session = Depends(obter_sessao),
) -> RespostaTransacao:

    transaction = buscar_transacao_por_id(
        session=session,
        invoice_id=invoice_id,
        transaction_id=transaction_id,
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transação não encontrada nesta fatura.",
        )

    try:
        updated_transaction = atualizar_transacao(
            session=session,
            transaction=transaction,
            update_data=update_data,
        )

    except Exception:
        session.rollback()

        raise HTTPException(
            status_code=422,
            detail="Não foi possível atualizar a transação.",
        )

    return RespostaTransacao(
        id=updated_transaction.id,
        invoice_id=updated_transaction.invoice_id,
        date=updated_transaction.date,
        transaction_date=updated_transaction.transaction_date,
        card=updated_transaction.card,
        description=updated_transaction.description,
        amount=updated_transaction.amount,
        type=updated_transaction.type,
        category=updated_transaction.category,
        origin=identificar_origem_da_transacao(
            updated_transaction
        ),
        page=updated_transaction.page,
    )


@router.delete(
    "/{invoice_id}/transactions/{transaction_id}",
    response_model=RespostaExclusaoTransacao,
)
def remover_transacao(
    invoice_id: int,
    transaction_id: int,
    session: Session = Depends(obter_sessao),
) -> RespostaExclusaoTransacao:

    transaction = buscar_transacao_por_id(
        session=session,
        invoice_id=invoice_id,
        transaction_id=transaction_id,
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transação não encontrada nesta fatura.",
        )

    try:
        excluir_transacao(
            session=session,
            transaction=transaction,
        )

    except Exception:
        session.rollback()

        raise HTTPException(
            status_code=422,
            detail="Não foi possível excluir a transação.",
        )

    return RespostaExclusaoTransacao(
        message="Transação excluída com sucesso.",
        transaction_id=transaction_id,
    )