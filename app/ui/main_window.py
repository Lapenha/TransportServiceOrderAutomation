import os
from datetime import date
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from app.core.config import settings
from app.services.pdf_service import generate_order_pdf
from app.services.repositories import Repository
from app.ui.theme import COLORS, apply_theme
from app.utils.formatting import format_date, parse_date


ORDER_TYPES = ["So ida", "So retorno", "Servico completo"]


class OSManagerApp(ctk.CTk):
    def __init__(self, app_name: str) -> None:
        super().__init__()
        apply_theme()
        self.repo = Repository()
        self.selected_order_id: int | None = None
        self.selected_client_id: int | None = None
        self.selected_driver_id: int | None = None
        self.selected_vehicle_id: int | None = None
        self.selected_motorist_id: int | None = None
        self.logo_image = self._load_logo()

        self.title(app_name)
        self.geometry("1240x740")
        self.minsize(1060, 660)
        self.configure(fg_color=COLORS["bg"])

        self._build_header()
        self.tabs = ctk.CTkTabview(self, corner_radius=8)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        for name in ("Ordens de Serviço", "Clientes", "Prestadores", "Motoristas", "Veículos"):
            self.tabs.add(name)

        self._build_orders_tab()
        self._build_clients_tab()
        self._build_drivers_tab()
        self._build_motorists_tab()
        self._build_vehicles_tab()
        self.refresh_all()

    def _load_logo(self):
        if settings.logo_path.exists():
            return ctk.CTkImage(Image.open(settings.logo_path), size=(230, 90))
        return None

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=14)
        if self.logo_image:
            ctk.CTkLabel(header, text="", image=self.logo_image).pack(side="left")
        else:
            ctk.CTkLabel(
                header,
                text="Loop Adventure",
                font=ctk.CTkFont(size=30, weight="bold", slant="italic"),
                text_color=COLORS["primary"],
            ).pack(side="left")
        ctk.CTkButton(
            header,
            text="Atualizar",
            width=120,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.refresh_all,
        ).pack(side="right")

    def _build_orders_tab(self) -> None:
        tab = self.tabs.tab("Ordens de Serviço")
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=12)
        self.order_search = ctk.CTkEntry(toolbar, placeholder_text="Buscar por OS, cliente, roteiro, tipo ou status")
        self.order_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.order_search.bind("<Return>", lambda _event: self.refresh_orders())
        ctk.CTkButton(toolbar, text="Buscar", width=95, command=self.refresh_orders).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Nova OS", width=105, fg_color=COLORS["primary"], command=self.open_order_dialog).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Editar", width=90, command=self.edit_selected_order).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="PDF", width=80, command=self.print_selected_order).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Excluir", width=90, fg_color=COLORS["danger"], command=self.delete_selected_order).pack(side="left", padx=4)

        self.orders_list = ctk.CTkScrollableFrame(tab, fg_color=COLORS["panel"], corner_radius=8)
        self.orders_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_clients_tab(self) -> None:
        tab = self.tabs.tab("Clientes")
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(toolbar, text="Novo cliente", fg_color=COLORS["primary"], command=self.open_client_dialog).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Editar", command=self.edit_selected_client).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Excluir", fg_color=COLORS["danger"], command=self.delete_selected_client).pack(side="left", padx=4)
        self.clients_list = ctk.CTkScrollableFrame(tab, fg_color=COLORS["panel"], corner_radius=8)
        self.clients_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_drivers_tab(self) -> None:
        tab = self.tabs.tab("Prestadores")
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(toolbar, text="Novo prestador", fg_color=COLORS["primary"], command=self.open_driver_dialog).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Editar", command=self.edit_selected_driver).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Excluir", fg_color=COLORS["danger"], command=self.delete_selected_driver).pack(side="left", padx=4)
        self.drivers_list = ctk.CTkScrollableFrame(tab, fg_color=COLORS["panel"], corner_radius=8)
        self.drivers_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_vehicles_tab(self) -> None:
        tab = self.tabs.tab("Veículos")
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(toolbar, text="Novo veículo", fg_color=COLORS["primary"], command=self.open_vehicle_dialog).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Editar", command=self.edit_selected_vehicle).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Excluir", fg_color=COLORS["danger"], command=self.delete_selected_vehicle).pack(side="left", padx=4)
        self.vehicles_list = ctk.CTkScrollableFrame(tab, fg_color=COLORS["panel"], corner_radius=8)
        self.vehicles_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_motorists_tab(self) -> None:
        tab = self.tabs.tab("Motoristas")
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(toolbar, text="Novo motorista", fg_color=COLORS["primary"], command=self.open_motorist_dialog).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Editar", command=self.edit_selected_motorist).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Excluir", fg_color=COLORS["danger"], command=self.delete_selected_motorist).pack(side="left", padx=4)
        self.motorists_list = ctk.CTkScrollableFrame(tab, fg_color=COLORS["panel"], corner_radius=8)
        self.motorists_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def refresh_all(self) -> None:
        self.refresh_orders()
        self.refresh_clients()
        self.refresh_drivers()
        self.refresh_motorists()
        self.refresh_vehicles()

    def refresh_orders(self) -> None:
        self._clear(self.orders_list)
        self._row(self.orders_list, ["OS", "Data", "Tipo", "Cliente", "Prestador", "Veículo", "Roteiro"], header=True)
        for order in self.repo.list_orders(self.order_search.get()):
            route = self._route_preview(order.origin, order.destination)
            vehicle = order.vehicle_ref.name if order.vehicle_ref else order.vehicle
            provider = (order.driver.nickname or order.driver.name) if order.driver else ""
            self._row(
                self.orders_list,
                [order.os_number, format_date(order.service_date), order.order_type, order.client.name, provider, vehicle, route],
                item_id=order.id,
                on_select=self._select_order,
            )

    def _route_preview(self, origins: str, destinations: str) -> str:
        origin_lines = [line.strip() for line in str(origins or "").splitlines() if line.strip()]
        destination_lines = [line.strip() for line in str(destinations or "").splitlines() if line.strip()]
        if origin_lines and destination_lines:
            total = max(len(origin_lines), len(destination_lines))
            routes = [
                f"{origin_lines[index] if index < len(origin_lines) else ''} -> {destination_lines[index] if index < len(destination_lines) else ''}".strip(" ->")
                for index in range(total)
            ]
            return " / ".join(routes)
        return " / ".join(origin_lines or destination_lines)

    def refresh_clients(self) -> None:
        self._clear(self.clients_list)
        self._row(self.clients_list, ["Nome", "Documento", "Telefone", "Email", "Endereço"], header=True)
        for client in self.repo.list_clients():
            self._row(self.clients_list, [client.name, client.document, client.phone, client.email, client.address], item_id=client.id, on_select=self._select_client)

    def refresh_drivers(self) -> None:
        self._clear(self.drivers_list)
        self._row(self.drivers_list, ["Prestador", "Apelido", "Documento", "Telefone"], header=True)
        for driver in self.repo.list_drivers():
            self._row(self.drivers_list, [driver.name, driver.nickname, driver.document, driver.phone], item_id=driver.id, on_select=self._select_driver)

    def refresh_vehicles(self) -> None:
        self._clear(self.vehicles_list)
        self._row(self.vehicles_list, ["Veículo", "Placa", "Prefixo", "Capacidade"], header=True)
        for vehicle in self.repo.list_vehicles():
            self._row(self.vehicles_list, [vehicle.name, vehicle.plate, vehicle.prefix, vehicle.capacity], item_id=vehicle.id, on_select=self._select_vehicle)

    def refresh_motorists(self) -> None:
        self._clear(self.motorists_list)
        self._row(self.motorists_list, ["Nome completo", "CPF", "CNH", "Telefone"], header=True)
        for motorist in self.repo.list_motorists():
            self._row(self.motorists_list, [motorist.full_name, motorist.cpf, motorist.cnh, motorist.phone], item_id=motorist.id, on_select=self._select_motorist)

    def _clear(self, frame) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _row(self, parent, values: list[str], header: bool = False, item_id=None, on_select=None) -> None:
        row = ctk.CTkFrame(parent, fg_color="#EEF2F7" if header else "#FFFFFF", corner_radius=6)
        row.pack(fill="x", padx=8, pady=(8 if header else 3, 3))
        weight = "bold" if header else "normal"
        for value in values:
            label = ctk.CTkLabel(row, text=str(value or ""), anchor="w", font=ctk.CTkFont(size=12, weight=weight), wraplength=260)
            label.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        if item_id is not None and on_select is not None:
            row.bind("<Button-1>", lambda _e: on_select(item_id, row))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda _e: on_select(item_id, row))

    def _mark_selected(self, parent, selected) -> None:
        for child in parent.winfo_children():
            try:
                child.configure(fg_color="#FFFFFF")
            except Exception:
                pass
        selected.configure(fg_color="#DDEBFF")

    def _select_order(self, order_id: int, row) -> None:
        self.selected_order_id = order_id
        self._mark_selected(self.orders_list, row)

    def _select_client(self, client_id: int, row) -> None:
        self.selected_client_id = client_id
        self._mark_selected(self.clients_list, row)

    def _select_driver(self, driver_id: int, row) -> None:
        self.selected_driver_id = driver_id
        self._mark_selected(self.drivers_list, row)

    def _select_vehicle(self, vehicle_id: int, row) -> None:
        self.selected_vehicle_id = vehicle_id
        self._mark_selected(self.vehicles_list, row)

    def _select_motorist(self, motorist_id: int, row) -> None:
        self.selected_motorist_id = motorist_id
        self._mark_selected(self.motorists_list, row)

    def open_order_dialog(self, order_id: int | None = None) -> None:
        OrderDialog(self, self.repo, order_id, on_saved=self.refresh_all)

    def edit_selected_order(self) -> None:
        if not self.selected_order_id:
            messagebox.showinfo("Selecione", "Selecione uma O.S. para editar.")
            return
        self.open_order_dialog(self.selected_order_id)

    def print_selected_order(self) -> None:
        if not self.selected_order_id:
            messagebox.showinfo("Selecione", "Selecione uma O.S. para gerar PDF.")
            return
        order = self.repo.get_order(self.selected_order_id)
        if order:
            path = generate_order_pdf(order)
            messagebox.showinfo("PDF gerado", f"Arquivo criado:\n{path}")
            os.startfile(path)

    def delete_selected_order(self) -> None:
        if self.selected_order_id and messagebox.askyesno("Excluir", "Excluir a O.S. selecionada?"):
            self.repo.delete_order(self.selected_order_id)
            self.selected_order_id = None
            self.refresh_all()

    def open_client_dialog(self, client_id: int | None = None) -> None:
        ClientDialog(self, self.repo, client_id, on_saved=self.refresh_all)

    def edit_selected_client(self) -> None:
        if not self.selected_client_id:
            messagebox.showinfo("Selecione", "Selecione um cliente.")
            return
        self.open_client_dialog(self.selected_client_id)

    def delete_selected_client(self) -> None:
        if self.selected_client_id and messagebox.askyesno("Excluir", "Excluir o cliente selecionado?"):
            self.repo.delete_client(self.selected_client_id)
            self.selected_client_id = None
            self.refresh_all()

    def open_driver_dialog(self, driver_id: int | None = None) -> None:
        DriverDialog(self, self.repo, driver_id, on_saved=self.refresh_all)

    def edit_selected_driver(self) -> None:
        if not self.selected_driver_id:
            messagebox.showinfo("Selecione", "Selecione um prestador.")
            return
        self.open_driver_dialog(self.selected_driver_id)

    def delete_selected_driver(self) -> None:
        if self.selected_driver_id and messagebox.askyesno("Excluir", "Excluir o prestador selecionado?"):
            self.repo.delete_driver(self.selected_driver_id)
            self.selected_driver_id = None
            self.refresh_all()

    def open_vehicle_dialog(self, vehicle_id: int | None = None) -> None:
        VehicleDialog(self, self.repo, vehicle_id, on_saved=self.refresh_all)

    def edit_selected_vehicle(self) -> None:
        if not self.selected_vehicle_id:
            messagebox.showinfo("Selecione", "Selecione um veículo.")
            return
        self.open_vehicle_dialog(self.selected_vehicle_id)

    def delete_selected_vehicle(self) -> None:
        if self.selected_vehicle_id and messagebox.askyesno("Excluir", "Excluir o veículo selecionado?"):
            self.repo.delete_vehicle(self.selected_vehicle_id)
            self.selected_vehicle_id = None
            self.refresh_all()

    def open_motorist_dialog(self, motorist_id: int | None = None) -> None:
        MotoristDialog(self, self.repo, motorist_id, on_saved=self.refresh_all)

    def edit_selected_motorist(self) -> None:
        if not self.selected_motorist_id:
            messagebox.showinfo("Selecione", "Selecione um motorista.")
            return
        self.open_motorist_dialog(self.selected_motorist_id)

    def delete_selected_motorist(self) -> None:
        if self.selected_motorist_id and messagebox.askyesno("Excluir", "Excluir o motorista selecionado?"):
            self.repo.delete_motorist(self.selected_motorist_id)
            self.selected_motorist_id = None
            self.refresh_all()


class BaseDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, width: int = 560, height: int = 560) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.transient(parent)
        self.grab_set()
        self.entries: dict[str, ctk.CTkEntry | ctk.CTkTextbox | ctk.CTkOptionMenu] = {}
        self.text_placeholders: dict[str, str] = {}
        self.body = ctk.CTkScrollableFrame(self, fg_color=COLORS["panel"], corner_radius=8)
        self.body.pack(fill="both", expand=True, padx=14, pady=14)

    def field(self, key: str, label: str, value: str = "", placeholder: str = "") -> None:
        ctk.CTkLabel(self.body, text=label, anchor="w").pack(fill="x", padx=8, pady=(8, 2))
        entry = ctk.CTkEntry(self.body, placeholder_text=placeholder)
        entry.insert(0, value or "")
        entry.pack(fill="x", padx=8, pady=(0, 4))
        self.entries[key] = entry

    def masked_field(self, key: str, label: str, value: str = "", mask: str = "date", placeholder: str = "") -> None:
        self.field(key, label, value, placeholder)
        entry = self.entries[key]
        if not isinstance(entry, ctk.CTkEntry):
            return

        def apply_mask(_event=None) -> None:
            current = entry.get()
            raw = "".join(ch for ch in current if ch.isdigit())
            if mask == "date":
                raw = raw[:8]
                parts = [raw[:2], raw[2:4], raw[4:8]]
                formatted = "/".join(part for part in parts if part)
            elif mask == "time":
                raw = raw[:4]
                formatted = raw[:2] + (":" + raw[2:] if len(raw) > 2 else "")
            elif mask == "phone":
                raw = raw[:11]
                if len(raw) <= 2:
                    formatted = f"({raw}" if raw else ""
                elif len(raw) <= 6:
                    formatted = f"({raw[:2]}) {raw[2:]}"
                elif len(raw) <= 10:
                    formatted = f"({raw[:2]}) {raw[2:6]}-{raw[6:]}"
                else:
                    formatted = f"({raw[:2]}) {raw[2:7]}-{raw[7:]}"
            elif mask == "cpf":
                raw = raw[:11]
                if len(raw) <= 3:
                    formatted = raw
                elif len(raw) <= 6:
                    formatted = f"{raw[:3]}.{raw[3:]}"
                elif len(raw) <= 9:
                    formatted = f"{raw[:3]}.{raw[3:6]}.{raw[6:]}"
                else:
                    formatted = f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"
            elif mask == "cpf_cnpj":
                raw = raw[:14]
                if len(raw) <= 11:
                    if len(raw) <= 3:
                        formatted = raw
                    elif len(raw) <= 6:
                        formatted = f"{raw[:3]}.{raw[3:]}"
                    elif len(raw) <= 9:
                        formatted = f"{raw[:3]}.{raw[3:6]}.{raw[6:]}"
                    else:
                        formatted = f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"
                else:
                    formatted = f"{raw[:2]}.{raw[2:5]}.{raw[5:8]}/{raw[8:12]}-{raw[12:]}"
            elif mask == "cnh":
                formatted = raw[:11]
            elif mask == "plate":
                raw_text = "".join(ch for ch in current.upper() if ch.isalnum())[:7]
                formatted = raw_text
            elif mask == "prefix":
                formatted = raw[:6]
            elif mask == "km":
                formatted = raw[:7]
            else:
                return
            entry.delete(0, "end")
            entry.insert(0, formatted)

        entry.bind("<KeyRelease>", apply_mask)

    def text_field(self, key: str, label: str, value: str = "", height: int = 80, placeholder: str = "") -> None:
        ctk.CTkLabel(self.body, text=label, anchor="w").pack(fill="x", padx=8, pady=(8, 2))
        entry = ctk.CTkTextbox(self.body, height=height)
        if value:
            entry.insert("1.0", value)
        elif placeholder:
            entry.insert("1.0", placeholder)
            entry.configure(text_color="#94A3B8")
            self.text_placeholders[key] = placeholder
        entry.pack(fill="x", padx=8, pady=(0, 4))
        self.entries[key] = entry

        if placeholder:
            def on_focus_in(_event=None) -> None:
                if key in self.text_placeholders and entry.get("1.0", "end").strip() == placeholder:
                    entry.delete("1.0", "end")
                    entry.configure(text_color=COLORS["text"])

            def on_focus_out(_event=None) -> None:
                if not entry.get("1.0", "end").strip():
                    entry.insert("1.0", placeholder)
                    entry.configure(text_color="#94A3B8")
                    self.text_placeholders[key] = placeholder

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

    def option(self, key: str, label: str, values: list[str], value: str = "") -> None:
        ctk.CTkLabel(self.body, text=label, anchor="w").pack(fill="x", padx=8, pady=(8, 2))
        option = ctk.CTkOptionMenu(self.body, values=values or [""])
        option.set(value or (values[0] if values else ""))
        option.pack(fill="x", padx=8, pady=(0, 4))
        self.entries[key] = option

    def get(self, key: str) -> str:
        widget = self.entries[key]
        if isinstance(widget, ctk.CTkTextbox):
            value = widget.get("1.0", "end").strip()
            return "" if self.text_placeholders.get(key) == value else value
        return widget.get().strip()

    def actions(self, save_command) -> None:
        bar = ctk.CTkFrame(self.body, fg_color="transparent")
        bar.pack(fill="x", padx=8, pady=14)
        ctk.CTkButton(bar, text="Cancelar", fg_color="#64748B", command=self.destroy).pack(side="right", padx=4)
        ctk.CTkButton(bar, text="Salvar", fg_color=COLORS["primary"], command=save_command).pack(side="right", padx=4)


class ClientDialog(BaseDialog):
    def __init__(self, parent, repo: Repository, client_id: int | None, on_saved) -> None:
        super().__init__(parent, "Cliente", 560, 520)
        self.repo, self.client_id, self.on_saved = repo, client_id, on_saved
        client = next((c for c in repo.list_clients() if c.id == client_id), None)
        self.field("name", "Nome", client.name if client else "", "Ex: Escola Estadual...")
        self.masked_field("document", "CNPJ/CPF", client.document if client else "", "cpf_cnpj", "Ex: 12.345.678/0001-90")
        self.masked_field("phone", "Telefone", client.phone if client else "", "phone", "Ex: (11) 99999-9999")
        self.field("email", "Email", client.email if client else "", "Ex: contato@email.com")
        self.field("address", "Endereço", client.address if client else "", "Ex: Rua, número - bairro")
        self.actions(self.save)

    def save(self) -> None:
        try:
            self.repo.save_client({key: self.get(key) for key in self.entries}, self.client_id)
            self.on_saved()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))


class DriverDialog(BaseDialog):
    def __init__(self, parent, repo: Repository, driver_id: int | None, on_saved) -> None:
        super().__init__(parent, "Prestador", 560, 440)
        self.repo, self.driver_id, self.on_saved = repo, driver_id, on_saved
        driver = next((d for d in repo.list_drivers() if d.id == driver_id), None)
        self.field("name", "Prestador", driver.name if driver else "", "Ex: W.L Transportes")
        self.field("nickname", "Apelido", driver.nickname if driver else "", "Ex: LOOP")
        self.masked_field("document", "CPF/CNPJ", driver.document if driver else "", "cpf_cnpj", "Ex: 04.401.860/0001-98")
        self.masked_field("phone", "Telefone", driver.phone if driver else "", "phone", "Ex: (11) 2952-2129")
        self.actions(self.save)

    def save(self) -> None:
        try:
            self.repo.save_driver({key: self.get(key) for key in self.entries}, self.driver_id)
            self.on_saved()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))


class VehicleDialog(BaseDialog):
    def __init__(self, parent, repo: Repository, vehicle_id: int | None, on_saved) -> None:
        super().__init__(parent, "Veículo", 560, 460)
        self.repo, self.vehicle_id, self.on_saved = repo, vehicle_id, on_saved
        vehicle = next((v for v in repo.list_vehicles() if v.id == vehicle_id), None)
        self.field("name", "Tipo", vehicle.name if vehicle else "", "Ex: MICRO, VAN, ONIBUS")
        self.masked_field("plate", "Placa", vehicle.plate if vehicle else "", "plate", "Ex: ABC1D23")
        self.masked_field("prefix", "Prefixo", vehicle.prefix if vehicle else "", "prefix", "Ex: 1001")
        self.actions(self.save)

    def save(self) -> None:
        try:
            self.repo.save_vehicle({key: self.get(key) for key in self.entries}, self.vehicle_id)
            self.on_saved()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))


class MotoristDialog(BaseDialog):
    def __init__(self, parent, repo: Repository, motorist_id: int | None, on_saved) -> None:
        super().__init__(parent, "Motorista", 560, 460)
        self.repo, self.motorist_id, self.on_saved = repo, motorist_id, on_saved
        motorist = next((m for m in repo.list_motorists() if m.id == motorist_id), None)
        self.field("full_name", "Nome completo", motorist.full_name if motorist else "", "Ex: Pedro Henrique Silva")
        self.masked_field("cpf", "CPF", motorist.cpf if motorist else "", "cpf", "Ex: 123.456.789-00")
        self.masked_field("cnh", "CNH", motorist.cnh if motorist else "", "cnh", "Ex: 12345678901")
        self.masked_field("phone", "Telefone", motorist.phone if motorist else "", "phone", "Ex: (11) 99999-9999")
        self.actions(self.save)

    def save(self) -> None:
        try:
            self.repo.save_motorist({key: self.get(key) for key in self.entries}, self.motorist_id)
            self.on_saved()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))


class OrderDialog(BaseDialog):
    def __init__(self, parent, repo: Repository, order_id: int | None, on_saved) -> None:
        super().__init__(parent, "Ordem de Serviço", 720, 800)
        self.repo, self.order_id, self.on_saved = repo, order_id, on_saved
        self.route_entries: list[tuple[ctk.CTkEntry, ctk.CTkEntry]] = []
        order = repo.get_order(order_id) if order_id else None
        clients = repo.list_clients()
        drivers = repo.list_drivers()
        vehicles = repo.list_vehicles()
        motorists = repo.list_motorists()
        self.client_map = {self._client_label(c): c.id for c in clients}
        self.driver_map = {self._driver_label(d): d.id for d in drivers}
        self.motorist_map = {m.full_name: m.id for m in motorists}
        self.vehicle_labels = {v.name: v.id for v in vehicles}

        client_value = self._client_label(order.client) if order and order.client else (self._client_label(clients[0]) if clients else "")
        driver_value = self._driver_label(order.driver) if order and order.driver else (self._driver_label(drivers[0]) if drivers else "")
        motorist_value = order.motorist.full_name if order and order.motorist else (order.requester if order and order.requester else (motorists[0].full_name if motorists else ""))
        selected_vehicle_id = order.vehicle_ref.id if order and order.vehicle_ref else None
        vehicle_value = next(
            (label for label, vehicle_id in self.vehicle_labels.items() if vehicle_id == selected_vehicle_id),
            next(iter(self.vehicle_labels), ""),
        )

        self.field("os_number", "Número da O.S.", order.os_number if order else repo.next_os_number(), "Ex: 0001")
        self.masked_field("issue_date", "Data de emissão", format_date(order.issue_date) if order else format_date(date.today()), "date", "Ex: 27/04/2026")
        self.masked_field("service_date", "Data do serviço", format_date(order.service_date) if order else format_date(date.today()), "date", "Ex: 27/04/2026")
        self.field("created_by", "Criado por", order.created_by if order else "", "Ex: Ana")
        self.option("order_type", "Tipo de O.S.", ORDER_TYPES, order.order_type if order else "Servico completo")
        order_type_widget = self.entries["order_type"]
        if isinstance(order_type_widget, ctk.CTkOptionMenu):
            order_type_widget.configure(command=self._on_order_type_changed)
        self.option("client", "Cliente", list(self.client_map.keys()), client_value)
        self.option("driver", "Prestador", list(self.driver_map.keys()), driver_value)
        self.option("motorist", "Motorista", list(self.motorist_map.keys()), motorist_value)
        self.option("vehicle", "Tipo do veículo", list(self.vehicle_labels.keys()), vehicle_value)
        self.masked_field("service_time", "Horário", order.service_time if order else "", "time", "Ex: 08:30")
        self._build_routes(order.origin if order else "", order.destination if order else "")
        self._on_order_type_changed(self.get("order_type"))
        self.text_field("notes", "Observações", order.notes if order else "", 90)
        self.actions(self.save)

    def _driver_label(self, driver) -> str:
        if not driver:
            return ""
        name = f"{driver.nickname} - {driver.name}" if driver.nickname else driver.name
        return f"{name} - {driver.document}" if driver.document else name

    def _client_label(self, client) -> str:
        if not client:
            return ""
        return f"{client.name} - {client.document}" if client.document else client.name

    def _build_routes(self, origins_value: str, destinations_value: str = "") -> None:
        self.routes_title = ctk.CTkLabel(self.body, text="Embarque / trecho", anchor="w")
        self.routes_title.pack(fill="x", padx=8, pady=(8, 2))
        self.routes_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.routes_frame.pack(fill="x", padx=8, pady=(0, 4))
        routes = self._split_saved_routes(origins_value, destinations_value)
        for origin, destination in routes:
            self._add_route_field(origin, destination)
        self.route_button_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.route_button_frame.pack(fill="x", padx=8, pady=(2, 8))
        self.add_route_button = ctk.CTkButton(
            self.route_button_frame,
            text="Adicionar trecho",
            width=150,
            fg_color=COLORS["primary"],
            command=lambda: self._add_route_field("", ""),
        )
        self.add_route_button.pack(anchor="w")

    def _split_saved_routes(self, origins_value: str, destinations_value: str = "") -> list[tuple[str, str]]:
        origins = [line.strip() for line in str(origins_value or "").splitlines() if line.strip()]
        destinations = [line.strip() for line in str(destinations_value or "").splitlines() if line.strip()]
        if origins and not destinations:
            split_routes = []
            for route in origins:
                separator = "->" if "->" in route else "-"
                if separator in route:
                    origin, destination = route.split(separator, 1)
                    split_routes.append((origin.strip(), destination.strip()))
                else:
                    split_routes.append((route, ""))
            return split_routes or [("", "")]
        total = max(len(origins), len(destinations), 1)
        return [
            (
                origins[index] if index < len(origins) else "",
                destinations[index] if index < len(destinations) else "",
            )
            for index in range(total)
        ]

    def _add_route_field(self, origin: str = "", destination: str = "") -> None:
        row = ctk.CTkFrame(self.routes_frame, fg_color="transparent")
        row.pack(fill="x", pady=(0, 6))
        number = len(self.route_entries) + 1
        ctk.CTkLabel(row, text=f"{number}.", width=28, anchor="w").pack(side="left")
        origin_entry = ctk.CTkEntry(row, placeholder_text="Origem")
        origin_entry.insert(0, origin or "")
        origin_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        destination_entry = ctk.CTkEntry(row, placeholder_text="Destino")
        destination_entry.insert(0, destination or "")
        destination_entry.pack(side="left", fill="x", expand=True)
        self.route_entries.append((origin_entry, destination_entry))
        self._renumber_routes()

    def _on_order_type_changed(self, value: str) -> None:
        allow_multiple = value == "Servico completo"
        if not hasattr(self, "add_route_button"):
            return
        self.routes_title.configure(text="Embarques / trechos" if allow_multiple else "Embarque / trecho")
        if allow_multiple:
            if not self.route_button_frame.winfo_ismapped():
                self.route_button_frame.pack(fill="x", padx=8, pady=(2, 8), after=self.routes_frame)
        else:
            self.route_button_frame.pack_forget()
            for origin_entry, _destination_entry in self.route_entries[1:]:
                origin_entry.master.destroy()
            self.route_entries = self.route_entries[:1]
            self._renumber_routes()

    def _renumber_routes(self) -> None:
        for index, (origin_entry, _destination_entry) in enumerate(self.route_entries, start=1):
            label = origin_entry.master.winfo_children()[0]
            label.configure(text=f"{index}.")

    def _selected_route_entries(self) -> list[tuple[ctk.CTkEntry, ctk.CTkEntry]]:
        entries = self.route_entries
        if self.get("order_type") != "Servico completo":
            entries = entries[:1]
        return entries

    def _get_origins(self) -> str:
        return "\n".join(
            origin_entry.get().strip()
            for origin_entry, destination_entry in self._selected_route_entries()
            if origin_entry.get().strip() or destination_entry.get().strip()
        )

    def _get_destinations(self) -> str:
        return "\n".join(
            destination_entry.get().strip()
            for origin_entry, destination_entry in self._selected_route_entries()
            if origin_entry.get().strip() or destination_entry.get().strip()
        )

    def save(self) -> None:
        try:
            client_name = self.get("client")
            driver_name = self.get("driver")
            motorist_name = self.get("motorist")
            vehicle_name = self.get("vehicle")
            if client_name not in self.client_map:
                raise ValueError("Cadastre e selecione um cliente.")
            if driver_name not in self.driver_map:
                raise ValueError("Cadastre e selecione um prestador.")
            if motorist_name not in self.motorist_map:
                raise ValueError("Cadastre e selecione um motorista.")
            if vehicle_name not in self.vehicle_labels:
                raise ValueError("Cadastre e selecione um veículo.")
            vehicle = next(v for v in self.repo.list_vehicles() if v.id == self.vehicle_labels[vehicle_name])
            prefix = vehicle.prefix
            data = {
                "os_number": self.get("os_number"),
                "issue_date": parse_date(self.get("issue_date")),
                "service_date": parse_date(self.get("service_date")),
                "order_type": self.get("order_type"),
                "created_by": self.get("created_by"),
                "status": "Aberta",
                "client_id": self.client_map[client_name],
                "driver_id": self.driver_map[driver_name],
                "motorist_id": self.motorist_map[motorist_name],
                "vehicle_id": vehicle.id,
                "requester": motorist_name,
                "prefix": prefix,
                "service_time": self.get("service_time"),
                "km_initial": "",
                "km_final": "",
                "origin": self._get_origins(),
                "destination": self._get_destinations(),
                "vehicle": vehicle.name,
                "passengers": "",
                "payment_status": "Pendente",
                "sale_price": 0,
                "cost": 0,
                "notes": self.get("notes"),
            }
            self.repo.save_order(data, self.order_id)
            self.on_saved()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro ao salvar", str(exc))
