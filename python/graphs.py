import numpy as np
import re
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from io import BytesIO

def bar(data={},title="",size=(20,6)):
    """Produce a histogram of the given summary data"""
    fig = Figure(figsize=size)
    fig.patch.set_facecolor('white')
    axis = fig.add_subplot(1, 1, 1)
    axis.text(0.05, 0.9, title, fontsize=24,transform = axis.transAxes)

    axis.bar(range(len(data)), data.values(), width=0.9, align='center', color='#565656')
    
    axis.set_xticks(range(len(data)))
    axis.set_xticklabels(list(data.keys()), rotation=90)
    
    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)
    axis.yaxis.set_ticks_position('left')
    axis.xaxis.set_ticks_position('bottom')
    canvas = FigureCanvas(fig)
    output = BytesIO()
    canvas.print_png(output)
    return output
