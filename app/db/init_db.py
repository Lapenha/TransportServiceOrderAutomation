from sqlalchemy import inspect, select, text

from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.entities import Client, Driver, Motorist, ServiceOrder, Vehicle


DEFAULT_COMPANY_NAME = "W.L TRANSPORTES E LOCADORA DE VEÍCULOS LTDA."
DEFAULT_COMPANY_DOCUMENT = "04.401.860/0001-98"
DEFAULT_COMPANY_PHONE = "(11) 2952-2129"
DEFAULT_COMPANY_EMAIL = "loopadventure@hotmail.com"
DEFAULT_COMPANY_ADDRESS = "Av. Jose da Rocha Viana, 257 - Vila Pedra Branca, Sao Paulo - SP"


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_order_columns()
    with SessionLocal() as session:
        _normalize_company(session)
        if not session.scalar(select(Client.id).limit(1)):
            session.add(
                Client(
                    name=DEFAULT_COMPANY_NAME,
                    document=DEFAULT_COMPANY_DOCUMENT,
                    phone=DEFAULT_COMPANY_PHONE,
                    email=DEFAULT_COMPANY_EMAIL,
                    address=DEFAULT_COMPANY_ADDRESS,
                )
            )

        if not session.scalar(select(Driver.id).where(Driver.name == DEFAULT_COMPANY_NAME)):
            session.add(
                Driver(
                    name=DEFAULT_COMPANY_NAME,
                    nickname="LOOP",
                    document=DEFAULT_COMPANY_DOCUMENT,
                    phone=DEFAULT_COMPANY_PHONE,
                )
            )

        if not session.scalar(select(Vehicle.id).limit(1)):
            session.add_all(
                [
                        Vehicle(name="MICRO", plate="", prefix="1001", capacity=""),
                        Vehicle(name="VAN", plate="", prefix="1002", capacity=""),
                        Vehicle(name="EXECUTIVO", plate="", prefix="1003", capacity=""),
                ]
            )
        if not session.scalar(select(Motorist.id).limit(1)):
            session.add(Motorist(full_name="Motorista Padrao", cpf="", cnh="", phone=""))
        session.commit()


def _normalize_company(session) -> None:
    old_names = ["Loop Adventure", "M " + "Rio " + "Negro"]
    target_client = session.scalar(select(Client).where(Client.name == DEFAULT_COMPANY_NAME))
    for name in old_names:
        old_client = session.scalar(select(Client).where(Client.name == name))
        if not old_client:
            continue
        if target_client and target_client.id != old_client.id:
            session.query(ServiceOrder).filter(ServiceOrder.client_id == old_client.id).update(
                {ServiceOrder.client_id: target_client.id}
            )
            session.delete(old_client)
        else:
            old_client.name = DEFAULT_COMPANY_NAME
            old_client.document = DEFAULT_COMPANY_DOCUMENT
            old_client.phone = DEFAULT_COMPANY_PHONE
            old_client.email = DEFAULT_COMPANY_EMAIL
            old_client.address = DEFAULT_COMPANY_ADDRESS
            target_client = old_client

    target_driver = session.scalar(select(Driver).where(Driver.name == DEFAULT_COMPANY_NAME))
    for name in ["Prestador Padrao", "Loop", "Loop Adventure"]:
        old_driver = session.scalar(select(Driver).where(Driver.name == name))
        if not old_driver:
            continue
        if target_driver and target_driver.id != old_driver.id:
            session.query(ServiceOrder).filter(ServiceOrder.driver_id == old_driver.id).update(
                {ServiceOrder.driver_id: target_driver.id}
            )
            session.delete(old_driver)
        else:
            old_driver.name = DEFAULT_COMPANY_NAME
            old_driver.nickname = "LOOP"
            old_driver.document = DEFAULT_COMPANY_DOCUMENT
            old_driver.phone = DEFAULT_COMPANY_PHONE
            target_driver = old_driver
    session.commit()


def _ensure_order_columns() -> None:
    inspector = inspect(engine)
    if "service_orders" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("service_orders")}
        statements = []
        if "prefix" not in columns:
            statements.append("ALTER TABLE service_orders ADD COLUMN prefix VARCHAR(40) DEFAULT ''")
        if "service_time" not in columns:
            statements.append("ALTER TABLE service_orders ADD COLUMN service_time VARCHAR(16) DEFAULT ''")
        if "order_type" not in columns:
            statements.append("ALTER TABLE service_orders ADD COLUMN order_type VARCHAR(32) DEFAULT 'Servico completo'")
        if "created_by" not in columns:
            statements.append("ALTER TABLE service_orders ADD COLUMN created_by VARCHAR(120) DEFAULT ''")
        if "vehicle_id" not in columns:
            statements.append("ALTER TABLE service_orders ADD COLUMN vehicle_id INTEGER")
        if "motorist_id" not in columns:
            statements.append("ALTER TABLE service_orders ADD COLUMN motorist_id INTEGER")
        if "km_initial" not in columns:
            statements.append("ALTER TABLE service_orders ADD COLUMN km_initial VARCHAR(24) DEFAULT ''")
        if "km_final" not in columns:
            statements.append("ALTER TABLE service_orders ADD COLUMN km_final VARCHAR(24) DEFAULT ''")
        if statements:
            with engine.begin() as connection:
                for statement in statements:
                    connection.execute(text(statement))
    _ensure_motorist_columns(inspector)
    _ensure_driver_columns(inspector)


def _ensure_motorist_columns(inspector) -> None:
    if "motorists" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("motorists")}
    statements = []
    if "phone" not in columns:
        statements.append("ALTER TABLE motorists ADD COLUMN phone VARCHAR(32) DEFAULT ''")
    if not statements:
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _ensure_driver_columns(inspector) -> None:
    if "drivers" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("drivers")}
    statements = []
    if "nickname" not in columns:
        statements.append("ALTER TABLE drivers ADD COLUMN nickname VARCHAR(80) DEFAULT ''")
    if not statements:
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
