from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import random
import matplotlib

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None):
        self.axs = []
        self.fig = Figure(dpi=100)
        self.fig.set_tight_layout(True) # to properly scale all elements on canvas
        self.axs.append(self.fig.add_subplot(3, 1, 1))
        self.axs[0].set_title("Cut")

        self.axs.append(self.fig.add_subplot(3, 1, (2, 3)))
        self.axs[1].set_title("Real time heatmap")
        super(MplCanvas, self).__init__(self.fig)