from PySide6 import QtCore, QtGui, QtOpenGLWidgets, QtWidgets


class View(QtWidgets.QGraphicsView):
    _background_color = QtGui.QColor(38, 38, 38)

    _grid_pen_s = QtGui.QPen(QtGui.QColor(52, 52, 52, 255), 0.5)
    _grid_pen_l = QtGui.QPen(QtGui.QColor(22, 22, 22, 255), 1.0)

    _grid_size_fine = 15
    _grid_size_course = 150

    request_node = QtCore.Signal(object)

    def change_place(self, event, button):
        if event.button() in button:
            self._pan = True
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

    def __init__(self, parent):
        super().__init__(parent)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self._manipulationMode = 0

        gl_format = QtGui.QSurfaceFormat()
        gl_format.setSamples(10)
        QtGui.QSurfaceFormat.setDefaultFormat(gl_format)
        gl_widget = QtOpenGLWidgets.QOpenGLWidget()

        self.currentScale = 1
        self._pan = False
        self._pan_start_x = 0
        self._pan_start_y = 0
        self._numScheduledScaling = 0
        self.lastMousePos = QtCore.QPoint()

        self.setViewport(gl_widget)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

    def drawBackground(self, painter, rect):
        """
        Draws the background for the interface editor view.

        :param painter: The painter to draw with.
        :param rect: The rectangle to be drawn.
        """

        def fill_grid(grid_size, grid_pen):
            left = int(rect.left()) - (int(rect.left()) % grid_size)
            top = int(rect.top()) - (int(rect.top()) % grid_size)

            # Draw horizontal lines
            grid_lines = []
            painter.setPen(grid_pen)
            y = float(top)
            while y < float(rect.bottom()):
                grid_lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
                y += grid_size
            painter.drawLines(grid_lines)

            # Draw vertical lines
            grid_lines = []
            painter.setPen(grid_pen)
            x = float(left)
            while x < float(rect.right()):
                grid_lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
                x += grid_size
            painter.drawLines(grid_lines)

        painter.fillRect(rect, self._background_color)
        fill_grid(self._grid_size_fine, self._grid_pen_s)  # fine squares
        fill_grid(self._grid_size_course, self._grid_pen_l)  # course squares

        return super().drawBackground(painter, rect)

    # ---------------------------------------- Events for Mouse -------------------------------------------------------#
    def wheelEvent(self, event):
        """
        Handles the wheel events, e.g. zoom in/out.
        :param event: Wheel event.
        """
        # Sometimes you can trigger the wheel when panning, so we disable when panning
        if self._pan:
            return

        delta = event.angleDelta().y()
        factor = 1.2 if delta > 0 else 1 / 1.2
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        """
        This method is called when a mouse press event occurs in the view.
        It sets the cursor to a closed hand cursor and enables panning if the middle mouse button is pressed.
        """
        self.change_place(event, button=QtCore.Qt.MouseButton.MiddleButton)
        return super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        This method is called when a double mouse press event occurs in the view.
        It sets the cursor to a closed hand cursor and enables panning if the left mouse button is pressed.
        """
        self.change_place(event, button=QtCore.Qt.MouseButton.LeftButton)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        This method is called when a mouse release event occurs in the view.
        It sets the cursor back to the arrow cursor and disables panning if the middle mouse button is released.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton or event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """
        This method is called when a mouse move event occurs in the view.
        It pans the view if the middle mouse button is pressed and moves the mouse.
        """
        if self._pan:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self._pan_start_x))

            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self._pan_start_y))

            self._pan_start_x = event.x()
            self._pan_start_y = event.y()

        return super().mouseMoveEvent(event)

    # ---------------------------------------- Events for Nodes -------------------------------------------------------#
    def dragEnterEvent(self, event):
        """
        This method is called when a drag and drop event enters the view. It checks if the mime data format is
        "text/plain" and accepts or ignores the event accordingly.
        """
        if event.mimeData().hasFormat("text/plain"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        This method is called when a drag and drop event is dropped onto the view.
        It retrieves the name of the dropped node from the mime data and emits a signal to request the creation of the
        corresponding node.
        """
        node = event.mimeData().item.class_name
        if node:
            self.request_node.emit(node())