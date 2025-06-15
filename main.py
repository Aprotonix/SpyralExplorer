from PySide6.QtWidgets import QApplication

from app import FileExplorerApp
import sys



# def apply_stylesheet(widget, path="style.qss"):
#     try:
#         with open(path, "r") as f:
#             widget.setStyleSheet(f.read())
#     except Exception as e:
#         print(f"Erreur lors du chargement du style : {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorerApp()
    #apply_stylesheet(window)
    window.show()
    sys.exit(app.exec())
