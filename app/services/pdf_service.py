from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from app.core.config import settings
from app.models.entities import ServiceOrder
from app.utils.formatting import format_date


BLUE = colors.HexColor("#0500FF")
RED = colors.HexColor("#FF0000")
BLACK = colors.HexColor("#111111")
LIGHT_GRAY = colors.HexColor("#E7E7EE")


def generate_order_pdf(order: ServiceOrder) -> str:
    settings.output_pdf_dir.mkdir(parents=True, exist_ok=True)
    path = settings.output_pdf_dir / f"OS_{order.os_number}_{datetime.now():%Y%m%d_%H%M%S}.pdf"

    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    _header(c, width, height, order)
    _main_fields(c, width, height, order)
    _section(c, 15.0 * cm, "ITINERÁRIO", width)
    _itinerary(c, width, order)
    _section(c, 8.6 * cm, "OBSERVAÇÕES", width)
    _observations(c, width, order)
    _signatures(c, width)
    _footer(c, width)

    c.showPage()
    c.save()
    return str(path)


def _header(c: canvas.Canvas, width: float, height: float, order: ServiceOrder) -> None:
    if settings.logo_path.exists():
        c.drawImage(str(settings.logo_path), 2.2 * cm, height - 2.45 * cm, width=8.0 * cm, height=1.75 * cm, preserveAspectRatio=True, mask="auto")
    else:
        c.setFillColor(BLUE)
        c.setFont("Helvetica-BoldOblique", 50)
        c.drawString(2.35 * cm, height - 2.08 * cm, "Loop")
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(9.75 * cm, height - 1.8 * cm, "ADVENTURE")

    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 0.45 * cm, height - 2.55 * cm, "W.L TRANSPORTES E LOCADORA DE VEÍCULOS LTDA. CNPJ : 04.401.860/0001-98")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.5 * cm, height - 2.95 * cm, order.prefix or "LESTE 3")

    c.setFillColor(BLUE)
    c.rect(0, height - 3.55 * cm, width, 0.38 * cm, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(0, height - 3.72 * cm, width, 0.18 * cm, fill=1, stroke=0)


def _main_fields(c: canvas.Canvas, width: float, height: float, order: ServiceOrder) -> None:
    top = height - 5.0 * cm
    left_label = 3.1 * cm
    left_value = 5.65 * cm
    right_label = 11.65 * cm
    right_value = 14.9 * cm
    line_w = 4.7 * cm

    _label(c, left_label, top, "DATA:")
    _value_line(c, left_value, top, format_date(order.service_date), 4.5 * cm)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(11.25 * cm, top, "Ordem de Serviço no.")
    c.setFillColor(LIGHT_GRAY)
    c.rect(16.0 * cm, top - 0.42 * cm, 2.15 * cm, 1.0 * cm, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(17.08 * cm, top - 0.12 * cm, order.os_number)

    provider = order.driver.name if order.driver else ""
    _label(c, left_label, top - 1.65 * cm, "PRESTADOR:")
    _wrapped_value_line(c, left_value + 0.45 * cm, top - 1.55 * cm, provider.upper(), 4.2 * cm, font_size=6.2)
    _label(c, right_label, top - 1.65 * cm, "MOTORISTA:")
    motorist_name = order.motorist.full_name if order.motorist else order.requester
    _value_line(c, right_value, top - 1.65 * cm, motorist_name.upper(), 4.0 * cm)

    _label(c, left_label, top - 3.25 * cm, "PREFIXO:")
    _value_line(c, left_value, top - 3.25 * cm, order.prefix.upper(), 4.5 * cm)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(right_label, top - 3.1 * cm, "KM")
    c.drawString(right_label, top - 3.6 * cm, "INICIAL:")
    _value_line(c, right_value, top - 3.25 * cm, "", 1.8 * cm)
    c.drawString(right_value + 2.25 * cm, top - 3.1 * cm, "KM")
    c.drawString(right_value + 2.25 * cm, top - 3.6 * cm, "FINAL:")
    _value_line(c, right_value + 3.8 * cm, top - 3.25 * cm, "", 1.6 * cm)

    _label(c, left_label, top - 4.85 * cm, "HORÁRIO:")
    _value_line(c, left_value, top - 4.85 * cm, order.service_time, 4.5 * cm)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(right_label, top - 4.7 * cm, "TIPO DE")
    c.drawString(right_label, top - 5.2 * cm, "VEICULO:")
    vehicle_name = order.vehicle_ref.name if order.vehicle_ref else order.vehicle
    _value_line(c, right_value, top - 4.95 * cm, vehicle_name.upper(), 4.0 * cm)

    _label(c, left_label, top - 6.25 * cm, "TIPO DE O.S.:")
    _value_line(c, left_value + 0.7 * cm, top - 6.25 * cm, order.order_type.upper(), 6.0 * cm)


def _itinerary(c: canvas.Canvas, width: float, order: ServiceOrder) -> None:
    routes = _route_lines(order)
    y = 14.25 * cm
    row_gap = 1.08 * cm
    label_x = 1.75 * cm
    value_x = 4.85 * cm
    line_width = width - value_x - 2.0 * cm
    for index, route in enumerate(routes[:5], start=1):
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(label_x, y, f"EMBARQUE {index}:")
        _fit_text(c, value_x, y, route, line_width, 11)
        _line(c, value_x, y - 0.08 * cm, line_width)
        y -= row_gap


def _observations(c: canvas.Canvas, width: float, order: ServiceOrder) -> None:
    _centered_wrapped(c, order.notes, 2.2 * cm, 7.35 * cm, width - 4.4 * cm, 11)
    for y in (7.35 * cm, 6.35 * cm):
        _line(c, 2.0 * cm, y, width - 4.0 * cm)


def _signatures(c: canvas.Canvas, width: float) -> None:
    _line(c, 2.1 * cm, 5.25 * cm, 7.5 * cm)
    _line(c, 10.7 * cm, 5.25 * cm, 7.5 * cm)
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(5.85 * cm, 4.72 * cm, "RESPONSÁVEL")
    c.drawCentredString(14.45 * cm, 4.72 * cm, "MOTORISTA")


def _footer(c: canvas.Canvas, width: float) -> None:
    c.setFillColor(BLUE)
    c.rect(0, 0.55 * cm, width, 0.95 * cm, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(0, 0, width, 0.55 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, 1.05 * cm, "(11) 2952-2129 - loopadventure@hotmail.com - Av. José da Rocha Viana, 257 - Vila Pedra Branca")
    c.drawCentredString(width / 2, 0.63 * cm, "São Paulo - SP")


def _section(c: canvas.Canvas, y: float, title: str, width: float) -> None:
    c.setFillColor(BLUE)
    c.rect(2.05 * cm, y, width - 4.1 * cm, 0.7 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y + 0.2 * cm, title)


def _label(c: canvas.Canvas, x: float, y: float, text: str) -> None:
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, text)


def _value_line(c: canvas.Canvas, x: float, y: float, text: str, width: float, font_size: int = 13) -> None:
    c.setFillColor(BLACK)
    c.setFont("Helvetica", font_size)
    c.drawString(x, y + 0.02 * cm, str(text or ""))
    _line(c, x, y - 0.08 * cm, width)


def _fit_value_line(c: canvas.Canvas, x: float, y: float, text: str, width: float, max_size: int = 13, min_size: int = 7) -> None:
    value = str(text or "")
    size = max_size
    while size > min_size and c.stringWidth(value, "Helvetica", size) > width:
        size -= 1
    if c.stringWidth(value, "Helvetica", size) > width:
        while value and c.stringWidth(value + "...", "Helvetica", size) > width:
            value = value[:-1]
        value = value + "..."
    _value_line(c, x, y, value, width, font_size=size)


def _fit_text(c: canvas.Canvas, x: float, y: float, text: str, width: float, max_size: int = 11, min_size: int = 7) -> None:
    value = str(text or "")
    size = max_size
    while size > min_size and c.stringWidth(value, "Helvetica", size) > width:
        size -= 1
    if c.stringWidth(value, "Helvetica", size) > width:
        while value and c.stringWidth(value + "...", "Helvetica", size) > width:
            value = value[:-1]
        value = value + "..."
    c.setFillColor(BLACK)
    c.setFont("Helvetica", size)
    c.drawString(x, y + 0.02 * cm, value)


def _route_lines(order: ServiceOrder) -> list[str]:
    origins = [line.strip() for line in str(order.origin or "").splitlines() if line.strip()]
    destinations = [line.strip() for line in str(order.destination or "").splitlines() if line.strip()]
    if origins and destinations:
        total = max(len(origins), len(destinations))
        return [
            f"{origins[index] if index < len(origins) else ''} - {destinations[index] if index < len(destinations) else ''}".strip(" -")
            for index in range(total)
        ]
    if origins:
        return origins
    if destinations:
        return destinations
    return [""]


def _wrapped_value_line(c: canvas.Canvas, x: float, y: float, text: str, width: float, font_size: float = 7) -> None:
    words = str(text or "").split()
    lines = ["", ""]
    current = 0
    for word in words:
        candidate = f"{lines[current]} {word}".strip()
        if c.stringWidth(candidate, "Helvetica", font_size) <= width or current == 1:
            lines[current] = candidate
        else:
            current = 1
            lines[current] = word
    c.setFillColor(BLACK)
    c.setFont("Helvetica", font_size)
    c.drawString(x, y + 0.11 * cm, lines[0])
    if lines[1]:
        c.drawString(x, y - 0.14 * cm, lines[1])
    _line(c, x, y - 0.22 * cm, width)


def _line(c: canvas.Canvas, x: float, y: float, width: float) -> None:
    c.setStrokeColor(BLACK)
    c.setLineWidth(0.8)
    c.line(x, y, x + width, y)


def _centered_wrapped(c: canvas.Canvas, text: str, x: float, y: float, width: float, size: int) -> None:
    style = ParagraphStyle(
        "centered",
        fontName="Helvetica",
        fontSize=size,
        leading=size + 5,
        alignment=TA_CENTER,
    )
    paragraph = Paragraph(str(text or "").replace("\n", "<br/>"), style)
    _, height = paragraph.wrap(width, 3.0 * cm)
    paragraph.drawOn(c, x, y - height)
