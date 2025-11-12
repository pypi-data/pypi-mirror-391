import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
import itertools

# Fricking freedom units smh
mm_to_inch = 1 / 25.4

double_column_width = 85 / 25.4  #inches
single_column_width = 160 / 25.4  #inches


figsize_double = np.array([double_column_width,85 * mm_to_inch]) #Figure size in inches for double column width in mm
figsize_single = np.array([single_column_width,85 * mm_to_inch]) #Figure size in inches for single column width in mm
golden_ratio = 0.618

figsize_double_golden = np.array([double_column_width, double_column_width / golden_ratio])#Figure size in inches for double column width in mm
figsize_single_golden = np.array([single_column_width, single_column_width * golden_ratio]) #Figure size in inches for single column width in mm

figsize_double_fullpage = np.array([double_column_width,200 * mm_to_inch]) #Figure size in inches for full page width in mm
figsize_single_fullpage = np.array([single_column_width,200 * mm_to_inch]) #Figure size in inches for full page width in mm
dpi = 300                         #Print resolution
ppi = np.sqrt(3456**2+2234**2)/24 #Screen resolution
#########################


markers = ['o', 'x', '+', '^', '*', 's', 'D', 'v', 'P', 'H']
marker_cycle = itertools.cycle(markers)

letter_labels_lc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']
letter_labels_uc = [letter.upper() for letter in letter_labels_lc]

def set_params():
    plt.rcParams.update(params)
    plt.rcParams['figure.constrained_layout.use'] = True

def use_classic_bw_lines():
    colors = ['black'] 
    linestyles = ['-', '--', '-.', ':']
    plt.rcParams['axes.prop_cycle'] = cycler(color=colors) * cycler(linestyle=linestyles)

def use_default_lines():
    plt.rcParams['axes.prop_cycle'] = plt.rcParamsDefault['axes.prop_cycle']

def use_okabe_ito_color():
    okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', 
             '#0072B2', '#D55E00', '#CC79A7', '#999999']
    plt.rcParams['axes.prop_cycle'] = cycler(color=okabe_ito)

def use_tab10_color():
    colors = plt.get_cmap('tab10').colors
    plt.rcParams['axes.prop_cycle'] = cycler(color=colors)


params = {
          "lines.color" :"black",
          "ytick.color" : "black",
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
          "figure.figsize": figsize_double, 
          'figure.constrained_layout.use': True,
          'figure.constrained_layout.hspace': 0.01,
          'figure.constrained_layout.wspace': 0.01,
          'figure.constrained_layout.h_pad':  0.02167,
          'figure.constrained_layout.w_pad':  0.02167,
          #'figure.autolayout': True,
          'lines.linewidth' : 0.8,
          'lines.markersize' : 4,
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
use_tab10_color()