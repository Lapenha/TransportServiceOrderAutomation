from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    document: Mapped[str] = mapped_column(String(32), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    email: Mapped[str] = mapped_column(String(160), default="")
    address: Mapped[str] = mapped_column(String(240), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["ServiceOrder"]] = relationship(back_populates="client")


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(80), default="")
    document: Mapped[str] = mapped_column(String(32), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["ServiceOrder"]] = relationship(back_populates="driver")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    plate: Mapped[str] = mapped_column(String(16), default="")
    prefix: Mapped[str] = mapped_column(String(40), default="")
    capacity: Mapped[str] = mapped_column(String(40), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["ServiceOrder"]] = relationship(back_populates="vehicle_ref")


class Motorist(Base):
    __tablename__ = "motorists"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    cpf: Mapped[str] = mapped_column(String(20), default="")
    cnh: Mapped[str] = mapped_column(String(32), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["ServiceOrder"]] = relationship(back_populates="motorist")


class ServiceOrder(Base):
    __tablename__ = "service_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    os_number: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    issue_date: Mapped[date] = mapped_column(Date, default=date.today)
    service_date: Mapped[date] = mapped_column(Date, default=date.today)
    status: Mapped[str] = mapped_column(String(32), default="Aberta")
    order_type: Mapped[str] = mapped_column(String(32), default="Servico completo")
    created_by: Mapped[str] = mapped_column(String(120), default="")
    requester: Mapped[str] = mapped_column(String(120), default="")
    prefix: Mapped[str] = mapped_column(String(40), default="")
    service_time: Mapped[str] = mapped_column(String(16), default="")
    km_initial: Mapped[str] = mapped_column(String(24), default="")
    km_final: Mapped[str] = mapped_column(String(24), default="")
    origin: Mapped[str] = mapped_column(Text, default="")
    destination: Mapped[str] = mapped_column(Text, default="")
    passengers: Mapped[str] = mapped_column(Text, default="")
    vehicle: Mapped[str] = mapped_column(String(100), default="")
    payment_status: Mapped[str] = mapped_column(String(32), default="Pendente")
    sale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"), nullable=True)
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("vehicles.id"), nullable=True)
    motorist_id: Mapped[int | None] = mapped_column(ForeignKey("motorists.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    client: Mapped[Client] = relationship(back_populates="orders")
    driver: Mapped[Driver | None] = relationship(back_populates="orders")
    vehicle_ref: Mapped[Vehicle | None] = relationship(back_populates="orders")
    motorist: Mapped[Motorist | None] = relationship(back_populates="orders")

    @property
    def profit(self) -> Decimal:
        return Decimal(self.sale_price or 0) - Decimal(self.cost or 0)
