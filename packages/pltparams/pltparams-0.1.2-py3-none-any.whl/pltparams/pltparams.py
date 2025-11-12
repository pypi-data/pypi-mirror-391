import matplotlib.pyplot as plt
import numpy as np

# Fricking freedom units smh

figsize_single = np.array([85,85]) / 25.4 #Figure size in inches for double column width in mm
figsize_double = np.array([160,85]) / 25.4 #Figure size in inches for single column width in mm
single_column_width = 85 / 25.4  #inches
double_column_width = 160 / 25.4  #inches
dpi = 300                         #Print resolution
ppi = np.sqrt(3456**2+2234**2)/24 #Screen resolution
#########################



params = {"ytick.color" : "black",
          "xtick.color" : "black",
          "axes.labelcolor" : "black",
          "axes.edgecolor" : "black",
          "text.usetex" : True,
          "font.family" : "serif",
          "font.serif" : ["Computer Modern Serif"],
          "axes.labelsize": 10,
          "axes.titlesize": 10,
          "xtick.labelsize": 10,
          "ytick.labelsize": 10,
          "legend.fontsize": 7,
          "figure.figsize": figsize_single, 
          'figure.constrained_layout.use': True,
          'figure.constrained_layout.hspace': 0.01,
          'figure.constrained_layout.wspace': 0.01,
          'figure.constrained_layout.h_pad':  0.02167,
          'figure.constrained_layout.w_pad':  0.02167,
          #'figure.autolayout': True,
          'lines.linewidth' : 0.5,
          'figure.facecolor' : "white",
          'axes.facecolor' : "white",
          'text.color' : 'black',
          'axes.titlecolor' : 'black',
          'savefig.facecolor' : 'white',
          'savefig.dpi' : '300',
          'savefig.format' : 'pdf',

          }
plt.rcParams.update(params)
plt.rcParams['figure.constrained_layout.use'] = True

def set_params():
    plt.rcParams.update(params)
    plt.rcParams['figure.constrained_layout.use'] = True