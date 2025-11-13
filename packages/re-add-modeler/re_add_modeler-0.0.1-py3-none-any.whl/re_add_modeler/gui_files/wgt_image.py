from okin.base.chem_logger import chem_logger
from re_add_modeler.utils.storage_paths import readdm_path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QPaintEvent

class ImageWidget(QWidget):
    resized = Signal()
    DEFAULT_IMG_FILE = f"{readdm_path}\\media\\xkcd_python.png"
    # ASPECT_RATIO = 16 / 9
    ASPECT_RATIO = 15 / 6.5 # empirical value

    def __init__(self, initial_width=800, parent=None):
        super().__init__()
        self.logger = chem_logger.getChild(self.__class__.__name__)
        self.initial_width = initial_width
        self.parent = parent
        self.image_label = QLabel()
        self.setup_ui()
        self.set_image_path(self.DEFAULT_IMG_FILE)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        self.setMouseTracking(True)

    def set_image_path(self, image_path):
        self.image_path = image_path
        self.update()

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        if self.image_path:
            painter = QPainter(self)
            pixmap = QPixmap(self.image_path)

            # Calculate the scaled pixmap dimensions to fit within the widget
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Calculate the position to center the image
            x = (self.width() - scaled_pixmap.width()) / 2
            y = (self.height() - scaled_pixmap.height()) / 2
            painter.drawPixmap(x, y, scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()

    def sizeHint(self):
        return QSize(self.initial_width, self.initial_width/self.ASPECT_RATIO)

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    image_widget = ImageWidget(initial_width=400)
    image_widget.show()
    sys.exit(app.exec())
