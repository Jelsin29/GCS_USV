"""
IconUtils.py - Simple utility to convert SVG icons from black to white
"""

from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

def createWhiteIcon(svg_path, size=24):
    """Convert SVG icon to white color"""
    try:
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(255, 255, 255))  # White
        painter.end()
        
        return QIcon(pixmap)
    except:
        return QIcon(svg_path)  # Fallback to original