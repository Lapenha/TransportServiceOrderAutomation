import customtkinter as ctk


def apply_theme() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")


COLORS = {
    "bg": "#F4F6FF",
    "panel": "#FFFFFF",
    "text": "#111111",
    "muted": "#5B6472",
    "primary": "#0700FF",
    "primary_hover": "#0200B8",
    "danger": "#E00000",
    "red": "#FF0000",
}
