import math

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import matplotlib.ticker as mtick
from matplotlib.axes import Axes
from matplotlib.ticker import AutoMinorLocator



plt.rcParams['font.sans-serif'] = 'Liberation Sans' 
plt.rcParams['font.family'] = 'serif'  
plt.rcParams['errorbar.capsize'] = 3.0  


golden = (1 + 5**0.5) / 2



# Figure creation
def golden_fig(nrows=1, ncols=1, scale=1, orient='h'):
    assert orient in ['h', 'v']
    height = 3.5
    width = ncols * height 
    height = nrows * height 
    if orient == 'h':
        width *= golden
    elif orient == 'v':
        height *= golden
    fig, axes = plt.subplots(nrows, ncols, figsize=tuple(scale * np.array([width, height])))
    if type(axes) == np.ndarray:
        axes = axes.flatten()
        axes = [Gax(ax) for ax in axes]
        for ax in axes:
            ax.make_golden()
    else:
        axes = Gax(axes)
        axes.make_golden()
    return fig, axes



def square_fig(nrows=1, ncols=1, scale=1):
    height = 4.45  
    width = ncols *  height 
    height = nrows * height 
    fig, axes = plt.subplots(nrows, ncols, figsize=tuple(scale * np.array([width, height])))
    if type(axes) == np.ndarray:
        axes = axes.flatten()
        axes = [Gax(ax) for ax in axes]
        for ax in axes:
            ax.make_square()
    else:
        axes = Gax(axes)
        axes.make_square()
        axes.set_nticks()
    return fig, axes




# Charts


class Gax(Axes):

    nticks = 5
    labelpad = 7

    def __init__(self, ax):
        # Adopt the existing ax's attributes
        self.__dict__ = ax.__dict__

    def remove(self):
        self.set_visible(False)

    def legend_side(self, title=None, bbox_to_anchor=(1.05, 1), fontsize=8, loc='upper left', **kwargs):
        self.legend(bbox_to_anchor=bbox_to_anchor, loc=loc, title=title, fontsize=fontsize, **kwargs)

    def remove_legend(self):
        self.legend_.remove()

    def reverse_ylim(self):
        ymin, ymax = self.get_ylim()
        self.set_ylim(ymax, ymin)

    def reverse_xlim(self):
        xmin, xmax = self.get_xlim()
        self.set_xlim(xmax, xmin)

    def remove_xtick_marks(self, **kwargs):
        self.tick_params(axis='x', length=0, **kwargs)  
   
    def remove_ytick_marks(self, **kwargs):
        self.tick_params(axis='y', length=0, **kwargs)  

    # Remove ticks
    def remove_xticks(self):
        self.set_xticks([])
        
    def remove_yticks(self):
        self.set_yticks([])    

    # Number of ticks
    def set_nxticks(self, n=None):
        if n is None:
            n = self.nticks
        self.xaxis.set_major_locator(plt.MaxNLocator(n))

    def set_nyticks(self, n=None):
        if n is None:
            n = self.nticks
        self.yaxis.set_major_locator(plt.MaxNLocator(n))

    def set_nticks(self, n=None):
        self.set_nxticks(n)
        self.set_nyticks(n)

    # Tick fontsize
    def set_xtick_fontsize(self, fontsize=None):
        self.tick_params(axis='x', labelsize=fontsize)

    def set_ytick_fontsize(self, fontsize=None):
        self.tick_params(axis='y', labelsize=fontsize)

    # Legend linewidth
    def set_legend_linewidth(self, width=0.7):
        self.get_legend().get_frame().set_linewidth(width)

    # Minor ticks
    def set_minor_nxticks(self, n):
        self.xaxis.set_minor_locator(plt.MaxNLocator(n))

    def set_minor_nyticks(self, n):
        self.yaxis.set_minor_locator(AutoMinorLocator(n))

    # Labels
    def set_xlabel(self, xlabel, labelpad=None, **kwargs):
        if labelpad is None:
            labelpad = self.labelpad
        Axes.set_xlabel(self, xlabel, labelpad=labelpad, **kwargs)

    def set_ylabel(self, ylabel, labelpad=None, **kwargs):
        if labelpad is None:
            labelpad = self.labelpad
        Axes.set_ylabel(self, ylabel, labelpad=labelpad, **kwargs)

    # Remove labels
    def remove_xlabel(self):
        self.set_xlabel(None)

    def remove_ylabel(self):
        self.set_ylabel(None)

    # Floating spines
    def float_x(self, x):
        self.spines.bottom.set_bounds(min(x), max(x))

    def float_y(self, y):
        self.spines.left.set_bounds(min(y), max(y))
    
    # Naked 
    def naked(self):
        self.naked_top()
        self.naked_bottom()

    def naked_bottom(self):
        self.remove_bottom_spine()
        self.remove_xlabel()
        self.remove_xticks()

    def naked_top(self):
        self.remove_top_right_spines()
        self.remove_left_spine()
        self.remove_yticks()
        self.remove_ylabel()
    
    # Remove spines
    def remove_top_right_spines(self):
        self.remove_top_spine()
        self.remove_right_spine()

    def remove_top_spine(self):
        self.spines['top'].set_visible(False)

    def remove_right_spine(self):
        self.spines['right'].set_visible(False)

    def remove_left_spine(self):
        self.spines['left'].set_visible(False)

    def remove_bottom_spine(self):
        self.spines['bottom'].set_visible(False)

    def modify_spinewidth(self, width=0.5):
        self.spines['top'].set_linewidth(width)
        self.spines['right'].set_linewidth(width)
        self.spines['bottom'].set_linewidth(width)
        self.spines['left'].set_linewidth(width)
    
    def modify_tickwidth(self, width=0.5):
        self.tick_params(axis='both', width=width)

    def remove_spine(self, spine):
        self.spines[spine].set_visible(False)

    # Grid
    def grid(self, linestyle='-', alpha=0.4, which='major', **kwargs):
        Axes.grid(self, linestyle=linestyle, alpha=alpha, which=which, **kwargs)

    def xgrid(self, linestyle='--', alpha=0.4, which='major', **kwargs):
        self.grid(axis='x', linestyle=linestyle, alpha=alpha, which=which, **kwargs)    

    def ygrid(self, linestyle='-', alpha=0.15, which='major', **kwargs):
        self.grid(axis='y', linestyle=linestyle, alpha=alpha, which=which, **kwargs)    

    # Scales
    def log_xscale(self):
        self.set_xscale('log')

    def log_yscale(self):
        self.set_yscale('log')

    def hline(self, y, **kwargs):
        self.axhline(y, **kwargs)

    def vline(self, x, **kwargs):
        self.axvline(x, **kwargs)

    def create_sign_formatter(self, decimals=1):
        def formatter(x, pos):
            if x == 0:
                return '0'
            elif x > 0:
                return f'$+${x:.{decimals}f}'
            else:
                return f'$-${-x:.{decimals}f}'
        return formatter

    # Plus and minus signs
    def sign_xscale(self, decimals=0):
        self.xaxis.set_major_formatter(mtick.FuncFormatter(self.create_sign_formatter(decimals)))

    def sign_yscale(self, decimals=0):
        self.yaxis.set_major_formatter(mtick.FuncFormatter(self.create_sign_formatter(decimals)))

    # Commas
    def comma_xscale(self, decimals=0):
        self.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: format(int(x), ',')))

    def comma_yscale(self, decimals=0):
        self.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Percent 
    def percent_xscale(self, decimals=0, change_lim=True):
        if change_lim:
            self.set_xlim(0, 1)
            self.set_xticks([0, 0.25, 0.5, 0.75, 1])
        self.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=decimals))

    def percent_yscale(self, decimals=0, change_lim=True):
        if change_lim:
            self.set_ylim(0, 1)
            self.set_nyticks(11)
            self.set_ytick_fontsize(8)
        self.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=decimals))

    def twinx(self, **kwargs):
        return Gax(Axes.twinx(self, **kwargs))

    # Mirror
    def mirror_y(self, fontsize=None):
        ax_right = self.twinx()
        ax_right.set_yticks(self.get_yticks())
        ax_right.set_yticklabels(self.get_yticklabels(), fontsize=fontsize)
        ax_right.set_ylim(self.get_ylim())

    def mirror_x(self, fontsize=None):
        ax_top = self.twiny()
        ax_top.set_xticks(self.get_xticks())
        ax_top.set_xticklabels(self.get_xticklabels(), fontsize=fontsize)
        ax_top.set_xlim(self.get_xlim())

    def make_golden(self, orient='h'):
        assert orient in ['h', 'v']
        if orient == 'h':
            self.set_box_aspect(1 / golden)
        elif orient == 'v':
            self.set_box_aspect(golden)

    def make_square(self):
        self.set_box_aspect(1)








def prepare_golden_fig(ax=None, **kwargs):
    if ax is None:
        fig, ax = golden_fig(**kwargs)
        return_fig = True
    else:
        return_fig = False
        fig = None
    return fig, ax, return_fig


def prepare_square_fig(ax=None, **kwargs):
    if ax is None:
        fig, ax = square_fig(**kwargs)
        return_fig = True
    else:
        return_fig = False
        fig = None
    return fig, ax, return_fig




## Types of plots

def plot_scatter(x, y, xlabel=None, ylabel=None, grid=True, linewidth=0.7, color="black", alpha=0.8, 
                edgecolor="none", s=10, ax=None, **kwargs):
    
    if xlabel is None:
        if isinstance(x, pd.Series):
            xlabel = x.name
        else:
            xlabel = "x"
    
    if ylabel is None:
        if isinstance(y, pd.Series):
            ylabel = y.name
        else:
            ylabel = "y"
    
    # Prepare figure/axis
    fig, ax, return_fig = prepare_square_fig(ax)

    if s is None:
        s = 25

    if grid:
        ax.grid()
        
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.remove_top_right_spines()
    sns.scatterplot(
        x=x,
        y=y,
        s=s,
        color=color,
        alpha=alpha,
        edgecolor=edgecolor,
        linewidth=linewidth,
        zorder=3,
        **kwargs
    )
    ax.set_nyticks(5)
    ax.set_nxticks(5)
    return (fig, ax) if return_fig else ax




def plot_normality(x, xlabel=None, title=None, alpha_clip=0.001, plt_zlim=3, ax=None,
                   color="purple", linewidth_x=0.8, alpha=0.3, linewidth_normal=4):

    # Prepare figure/axis
    fig, ax, return_fig = prepare_golden_fig(ax)
    

    if alpha_clip is not None:
        lower = np.nanquantile(x, alpha_clip)
        upper = np.nanquantile(x, 1 - alpha_clip)
        x_clipped = np.clip(x, lower, upper)
        loc = np.nanmean(x_clipped)
        scale = np.nanstd(x_clipped)
    else:
        loc = np.nanmean(x)
        scale = np.nanstd(x)
    
    sns.ecdfplot(x, ax=ax, color=color, linewidth=linewidth_x, zorder=10)

    z = np.linspace(loc - scale * plt_zlim, loc + scale * plt_zlim, 1000)
    
    def norm_cdf(x, loc, scale):
        z = (x - loc) / (scale * math.sqrt(2))
        return 0.5 * (1 + np.vectorize(math.erf)(z))

    sns.lineplot(x=z, y=norm_cdf(z, loc, scale), ax=ax, 
                 color="grey", linewidth=linewidth_normal, alpha=alpha)

    ax.set_xlim(loc - scale * plt_zlim, loc + scale * plt_zlim)
            
    ax.percent_yscale()
    ax.set_ylabel("Percentile")
    
    if xlabel is None:
        if isinstance(x, pd.Series):
            xlabel = x.name.replace("_", " ").capitalize() if x.name is not None else "x"
        else:
            xlabel = "x"
            
    if title is None:
        if isinstance(x, pd.Series):
            title = x.name.replace("_", " ").capitalize() if x.name is not None else ""
        else:
            title = ""

    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_nxticks(5)
    ax.grid()

    return (fig, ax) if return_fig else ax




def plot_univariate_distribution(x, xlabel=None, alpha=0.005, 
                            linewidth=0.8, ax=None, color="black", **kwargs):
    """Set alpha to None to remove quantile edge"""
    # Prepare figure/axis
    fig, ax, return_fig = prepare_golden_fig(ax)
    
    if isinstance(x, pd.Series):
        x = x.dropna()
        
    sns.ecdfplot(x, ax=ax, color=color, linewidth=linewidth, zorder=10, **kwargs)
    
    if alpha is None:
        alpha = 0
    if min(x) == 0:
        ax.set_xlim(0, np.quantile(x, 1-alpha))
    else:
        ax.set_xlim(np.quantile(x, alpha), np.quantile(x, 1-alpha))
            
    ax.percent_yscale()
    ax.set_ylabel("Percentile")

    if xlabel is None:
        if isinstance(x, pd.Series):
            xlabel = x.name.replace("_", " ").capitalize() if x.name is not None else "x"
        else:
            xlabel = "x"

    ax.set_xlabel(xlabel)
    ax.grid()
    if (np.quantile(x, 1-alpha) - np.quantile(x, alpha) > 0.05) > 2_000:
        ax.comma_xscale()
    return (fig, ax) if return_fig else ax







