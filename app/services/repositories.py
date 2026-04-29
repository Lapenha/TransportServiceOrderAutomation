from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from app.db.session import SessionLocal
from app.models.entities import Client, Driver, Motorist, ServiceOrder, Vehicle


class Repository:
    def list_clients(self) -> list[Client]:
        with SessionLocal() as session:
            return list(session.scalars(select(Client).order_by(Client.name)))

    def save_client(self, data: dict, client_id: int | None = None) -> Client:
        with SessionLocal() as session:
            client = session.get(Client, client_id) if client_id else Client()
            if client is None:
                raise ValueError("Cliente nao encontrado.")
            for key, value in data.items():
                setattr(client, key, value)
            session.add(client)
            session.commit()
            session.refresh(client)
            return client

    def delete_client(self, client_id: int) -> None:
        with SessionLocal() as session:
            client = session.get(Client, client_id)
            if client:
                session.delete(client)
                session.commit()

    def list_drivers(self) -> list[Driver]:
        with SessionLocal() as session:
            return list(session.scalars(select(Driver).order_by(Driver.name)))

    def save_driver(self, data: dict, driver_id: int | None = None) -> Driver:
        with SessionLocal() as session:
            driver = session.get(Driver, driver_id) if driver_id else Driver()
            if driver is None:
                raise ValueError("Motorista/prestador nao encontrado.")
            for key, value in data.items():
                setattr(driver, key, value)
            session.add(driver)
            session.commit()
            session.refresh(driver)
            return driver

    def delete_driver(self, driver_id: int) -> None:
        with SessionLocal() as session:
            driver = session.get(Driver, driver_id)
            if driver:
                session.delete(driver)
                session.commit()

    def list_vehicles(self) -> list[Vehicle]:
        with SessionLocal() as session:
            return list(session.scalars(select(Vehicle).order_by(Vehicle.name)))

    def save_vehicle(self, data: dict, vehicle_id: int | None = None) -> Vehicle:
        with SessionLocal() as session:
            vehicle = session.get(Vehicle, vehicle_id) if vehicle_id else Vehicle()
            if vehicle is None:
                raise ValueError("Veiculo nao encontrado.")
            for key, value in data.items():
                setattr(vehicle, key, value)
            session.add(vehicle)
            session.commit()
            session.refresh(vehicle)
            return vehicle

    def delete_vehicle(self, vehicle_id: int) -> None:
        with SessionLocal() as session:
            vehicle = session.get(Vehicle, vehicle_id)
            if vehicle:
                session.delete(vehicle)
                session.commit()

    def list_motorists(self) -> list[Motorist]:
        with SessionLocal() as session:
            return list(session.scalars(select(Motorist).order_by(Motorist.full_name)))

    def save_motorist(self, data: dict, motorist_id: int | None = None) -> Motorist:
        with SessionLocal() as session:
            motorist = session.get(Motorist, motorist_id) if motorist_id else Motorist()
            if motorist is None:
                raise ValueError("Motorista nao encontrado.")
            for key, value in data.items():
                setattr(motorist, key, value)
            session.add(motorist)
            session.commit()
            session.refresh(motorist)
            return motorist

    def delete_motorist(self, motorist_id: int) -> None:
        with SessionLocal() as session:
            motorist = session.get(Motorist, motorist_id)
            if motorist:
                session.delete(motorist)
                session.commit()

    def next_os_number(self) -> str:
        with SessionLocal() as session:
            max_id = session.scalar(select(func.max(ServiceOrder.id))) or 0
            return f"{max_id + 1:04d}"

    def list_orders(self, search: str = "") -> list[ServiceOrder]:
        with SessionLocal() as session:
            stmt = (
                select(ServiceOrder)
                .options(
                    joinedload(ServiceOrder.client),
                    joinedload(ServiceOrder.driver),
                    joinedload(ServiceOrder.vehicle_ref),
                    joinedload(ServiceOrder.motorist),
                )
                .order_by(ServiceOrder.service_date.desc(), ServiceOrder.id.desc())
            )
            if search.strip():
                term = f"%{search.strip()}%"
                stmt = stmt.join(ServiceOrder.client).where(
                    or_(
                        ServiceOrder.os_number.ilike(term),
                        ServiceOrder.origin.ilike(term),
                        ServiceOrder.destination.ilike(term),
                        ServiceOrder.order_type.ilike(term),
                        ServiceOrder.status.ilike(term),
                        Client.name.ilike(term),
                    )
                )
            return list(session.scalars(stmt))

    def get_order(self, order_id: int) -> ServiceOrder | None:
        with SessionLocal() as session:
            return session.scalar(
                select(ServiceOrder)
                .options(
                    joinedload(ServiceOrder.client),
                    joinedload(ServiceOrder.driver),
                    joinedload(ServiceOrder.vehicle_ref),
                    joinedload(ServiceOrder.motorist),
                )
                .where(ServiceOrder.id == order_id)
            )

    def save_order(self, data: dict, order_id: int | None = None) -> ServiceOrder:
        with SessionLocal() as session:
            order = session.get(ServiceOrder, order_id) if order_id else ServiceOrder()
            if order is None:
                raise ValueError("Ordem de Servico nao encontrada.")
            for key, value in data.items():
                setattr(order, key, value)
            session.add(order)
            session.commit()
            session.refresh(order)
            return self.get_order(order.id)

    def delete_order(self, order_id: int) -> None:
        with SessionLocal() as session:
            order = session.get(ServiceOrder, order_id)
            if order:
                session.delete(order)
                session.commit()

    def dashboard(self) -> dict:
        with SessionLocal() as session:
            orders = list(session.scalars(select(ServiceOrder)))
            total = sum(Decimal(o.sale_price or 0) for o in orders)
            costs = sum(Decimal(o.cost or 0) for o in orders)
            open_count = sum(1 for o in orders if o.status != "Concluida")
            paid = sum(Decimal(o.sale_price or 0) for o in orders if o.payment_status == "Pago")
            monthly = {}
            for order in orders:
                key = order.service_date.strftime("%Y-%m") if order.service_date else "Sem data"
                monthly[key] = monthly.get(key, Decimal("0")) + Decimal(order.sale_price or 0)
            return {
                "orders": len(orders),
                "open": open_count,
                "revenue": total,
                "costs": costs,
                "profit": total - costs,
                "paid": paid,
                "monthly": monthly,
            }
