from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def parse_date(value: str) -> date:
    value = value.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("Use data no formato DD/MM/AAAA.")


def format_date(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def parse_money(value: str) -> Decimal:
    cleaned = value.strip().replace("R$", "").replace(".", "").replace(",", ".")
    if not cleaned:
        return Decimal("0.00")
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("Use valor monetario valido.") from exc


def format_money(value) -> str:
    amount = Decimal(value or 0).quantize(Decimal("0.01"))
    return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
