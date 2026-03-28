import sys
import numpy as np
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg

class VectorVisualizer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matrix / Basis Mesh Visualizer (Fixed Grid)")

        # Original basis
        self.v0_1 = np.array([1.0, 0.0])
        self.v0_2 = np.array([0.0, 1.0])
        # Target basis
        self.v1_target = np.array([1.0, 0.0])
        self.v2_target = np.array([0.0, 1.0])

        # Central widget + layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True)
        layout.addWidget(self.plot_widget)

        # Controls layout
        form_layout = QtWidgets.QFormLayout()
        layout.addLayout(form_layout)

        # Text boxes for vectors
        self.v1x_text = QtWidgets.QLineEdit(str(self.v1_target[0]))
        self.v1y_text = QtWidgets.QLineEdit(str(self.v1_target[1]))
        self.v2x_text = QtWidgets.QLineEdit(str(self.v2_target[0]))
        self.v2y_text = QtWidgets.QLineEdit(str(self.v2_target[1]))

        form_layout.addRow("v1 x", self.v1x_text)
        form_layout.addRow("v1 y", self.v1y_text)
        form_layout.addRow("v2 x", self.v2x_text)
        form_layout.addRow("v2 y", self.v2y_text)

        # Animation slider
        self.anim_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.anim_slider.setRange(0, 100)
        self.anim_slider.setValue(0)
        form_layout.addRow("Animation t", self.anim_slider)

        # Connect signals
        self.v1x_text.textChanged.connect(self.update_target_basis)
        self.v1y_text.textChanged.connect(self.update_target_basis)
        self.v2x_text.textChanged.connect(self.update_target_basis)
        self.v2y_text.textChanged.connect(self.update_target_basis)
        self.anim_slider.valueChanged.connect(self.draw)

        # Initial draw
        self.draw()
        self.auto_zoom()  # Only called once at startup

    def transform(self, points, v1, v2):
        M = np.column_stack((v1, v2))
        return points @ M.T

    def draw(self):
        self.plot_widget.clear()
        t = self.anim_slider.value() / 100.0

        # Interpolated basis
        v1 = (1 - t) * self.v0_1 + t * self.v1_target
        v2 = (1 - t) * self.v0_2 + t * self.v2_target

        # Mesh grid
        x_vals = np.arange(-10, 11)
        y_vals = np.arange(-10, 11)

        for y in y_vals:
            line = np.array([[x, y] for x in x_vals])
            trans_line = self.transform(line, v1, v2)
            self.plot_widget.plot(trans_line[:, 0], trans_line[:, 1],
                                  pen=pg.mkPen('b', width=1))
        for x in x_vals:
            line = np.array([[x, y] for y in y_vals])
            trans_line = self.transform(line, v1, v2)
            self.plot_widget.plot(trans_line[:, 0], trans_line[:, 1],
                                  pen=pg.mkPen('b', width=1))

        # Draw basis vectors
        self.plot_widget.plot([0, v1[0]], [0, v1[1]], pen=pg.mkPen('r', width=2))
        self.plot_widget.plot([0, v2[0]], [0, v2[1]], pen=pg.mkPen('g', width=2))

        self.plot_widget.setAspectLocked(True)

    def update_target_basis(self):
        try:
            self.v1_target = np.array([float(self.v1x_text.text()),
                                       float(self.v1y_text.text())])
            self.v2_target = np.array([float(self.v2x_text.text()),
                                       float(self.v2y_text.text())])
        except ValueError:
            return
        self.draw()  # Only redraw mesh, do NOT adjust zoom

    def auto_zoom(self):
        """Zoom to initial view including basis vectors, called only once."""
        all_vectors = np.array([self.v0_1, self.v0_2, self.v1_target, self.v2_target])
        max_val = np.max(np.abs(all_vectors)) * 1.5  # Add some padding
        self.plot_widget.setXRange(-max_val, max_val)
        self.plot_widget.setYRange(-max_val, max_val)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = VectorVisualizer()
    w.resize(900, 700)
    w.show()
    sys.exit(app.exec())