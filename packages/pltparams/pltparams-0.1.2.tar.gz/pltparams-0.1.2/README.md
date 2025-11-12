# Scientific style for matplotlib on import

## Install

Use pip package
```bash
pip install pltparams
```

Or download the repo to your computer

```bash
cd path/to/pltparams
pip install .
```


## Usage
```python
import pltparams
```

sets the appropriate rc params for scientific style.


Alternatively:
```python
import pltparams
pltparams.set_params()
```


These are the params the package will change, feel free to copy/paste if you prefer that
```python
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
          "figure.figsize": figsize/ 25.4,
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
```