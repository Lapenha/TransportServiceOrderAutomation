from app.core.config import settings
from app.db.init_db import init_database
from app.ui.main_window import OSManagerApp


def main() -> None:
    init_database()
    app = OSManagerApp(app_name=settings.app_name)
    app.mainloop()


if __name__ == "__main__":
    main()
