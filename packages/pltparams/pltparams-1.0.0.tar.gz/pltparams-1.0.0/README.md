# Scientific style for matplotlib on import

The default font, font size, figure size, color shceme, linewidth, marker size etc. are not suited for scientific publications. This package sets the defaults to suitable parameters on import, and offers some handy functions for setting new defaults or cycling props.

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

The defualt colorscheme has some hard to see colors for white backgrounds, especially if it defaults to the darkmode theme. The `'tab10'`colorshcme is good for white background, and is defualt here. Call `use_tab10_color` to revert back to it. 

For black and white, we call `use_classic_bw_style()` for different linestyles and markers instead of color. This is probably the most useful command.

There's also an alternate `use_okabe_ito_color()` if you prefer the okabe ito color scheme.

Cycle through the markers by simply calling `next(pltparams.marker_cycle)`. This is the easiest way, as setting default markers will also impose them on `plot()`in addition to `scatter()`. 

```python
# Plot single column (Default style )
fig, ax = plt.subplots(1,1,figsize = pltparams.figsize_single)
plot_example(ax)

```
![Example single column plot](figures/example_single_default.png)

For the "classic" black and white style
```python
pltparams.use_classic_bw_lines()
fig, ax = plt.subplots(1,1,figsize = pltparams.figsize_single)
plot_example(ax)
```

![Classic BW](figures/example_single_bw.png)

Alternate okabe ito color scheme
```python
pltparams.use_okabe_ito_color()
fig, ax = plt.subplots(1,1,figsize = pltparams.figsize_single)
plot_example(ax)
```
![Okabe Ito](figures/example_single_okabe_it.png)

## Cycle props
We can fetch the next marker using `next(marker_cycle)`, to easily grab the next markers. This is the easiest way to do this, as marker prop cycles can not be set in the defualt RCParams.
```python
ax.scatter(x_scatter, y_scatter, marker = next(pltparams.marker_cycle), label="data 1 scatter")
```

There's also a `letter_labels_lc` and `letter_labels_uc` for lower case, and upper case, letters. This is handy for subplots.
```python
ax.set_title(pltparams.letter_labels_lc[j]+") : "+subplot_labels[j], loc='left')
```
![Subplots](figures/example_single_subplots.png)


# Alternatively copy paste this

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

