from log import log
from time import monotonic
log("Loading program...")
start = monotonic()
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
    app.setStartDragDistance(30) # Sensibility of statring dragging
    window = FileExplorerApp()
    #apply_stylesheet(window)
    log(f"Loading finisehd in {round(monotonic()- start, 2)}s")
    log("Starting window...")
    window.show()
    sys.exit(app.exec())
