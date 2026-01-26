import os
#import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from momp.lib.loader import get_cfg, get_setting
from itertools import product
from dataclasses import asdict
from momp.lib.control import iter_list, make_case
from momp.lib.control import ref_cfg_layout, ref_model_case
from momp.lib.convention import Case
from momp.graphics.func_map import spatial_metrics_map
from momp.utils.printing import tuple_to_str
import cartopy.crs as ccrs
from matplotlib.ticker import MaxNLocator, FixedLocator
from matplotlib.gridspec import GridSpec
from matplotlib import colors as mcolors


def panel_map_mae_far_mr(model_list, verification_window, var_name, cfg, setting, **kwargs):

    day_bin = tuple_to_str(verification_window)
    
    n = len(model_list)
    fig = plt.figure(figsize=(8, 5/4*n))
    axes = []
    ims = []
    fig_width, fig_height = fig.get_size_inches()
    text_scale =  min(fig_width/n, fig_height/1) / 5 * 1.2

    gs = GridSpec(2, n, height_ratios=[1, 0.043], hspace=0.02, wspace=0.07)

    for i, model in enumerate(model_list):
        fi = os.path.join(cfg.dir_out,"spatial_metrics_{}_{}.nc")
        fi = fi.format(model, day_bin)
        ds = xr.open_dataset(fi)
        da = ds[var_name]
        ds.close()

        combi = (model, verification_window)
        if model == cfg.ref_model:
            cfg_ref, _ = ref_cfg_layout(cfg, ref_model=model, verification_window=verification_window)
            case = make_case(Case, combi, vars(cfg_ref))
        else:
            case = make_case(Case, combi, vars(cfg))

        case_cfg = {**asdict(case), **asdict(setting)}

        if i > 0:
            show_ylabel, title, cmap = False, None, 'RdBu_r'
        else:
            show_ylabel, title, cmap = True, f"{var_name} {day_bin} day", 'YlOrRd'

        print(i, show_ylabel, title, cmap)

        ax = fig.add_subplot(gs[0, i], projection=ccrs.PlateCarree())

        fig, ax, im, _ = spatial_metrics_map(da, model, fig=fig, ax=ax, domain_mask=True, 
                                         show_ylabel=show_ylabel, cmap=cmap, title=title, panel=True, 
                                         text_scale=text_scale, **case_cfg)

        axes.append(ax)
        ims.append(im)
        i += 1

    cax_ref = fig.add_subplot(gs[1, 0])
    cbar_ref = fig.colorbar(ims[0], cax=cax_ref, orientation='horizontal')

    gs_cell = gs[1, 1:]  # full width across remaining panels
    pos = gs_cell.get_position(fig)  # bounding box of this cell
    cax_mod = fig.add_axes([pos.x0 + 0.1, pos.y0, pos.width * 0.6, pos.height]) # shrink width by 20% on each side

    cbar_mod = fig.colorbar(ims[1], cax=cax_mod, orientation='horizontal')

    for cb in (cbar_ref, cbar_mod):
        cb.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        for i, label in enumerate(cb.ax.get_xticklabels()):
            if i % 2 == 1:
                label.set_visible(False)

    for cb in (cbar_ref, cbar_mod):
        if isinstance(cb.norm, mcolors.BoundaryNorm):
            boundaries = cb.norm.boundaries  # the levels
            tick_locs = 0.5 * (boundaries[:-1] + boundaries[1:]) # bin centers
            tick_locs_to_show = tick_locs[::2]
            cb.set_ticks(tick_locs_to_show)

            cb.ax.xaxis.set_minor_locator(plt.NullLocator())

            tick_labels = [str(int(i)) for i in np.arange(len(tick_locs_to_show))]

            cb.set_ticklabels(tick_labels)
            cb.ax.tick_params(labelsize=7, direction='in', length=1.5)


    fig.suptitle(f"{var_name} (in days) {day_bin} day forecast", fontsize=15)
    plt.tight_layout(rect=[0, 0, 0.99, 1]) # doesn't work for Cartopy axes
    plt.show()

    return fig, axes, ims
    

if __name__ == "__main__":

    from itertools import product
    from dataclasses import asdict
    import xarray as xr
    #from momp.stats.benchmark import compute_metrics_multiple_years
    from momp.lib.control import iter_list, make_case
    from momp.lib.control import ref_cfg_layout, ref_model_case
    from momp.lib.convention import Case
    from momp.lib.loader import get_cfg, get_setting
    #from momp.metrics.error import create_spatial_far_mr_mae
    from momp.graphics.func_map import spatial_metrics_map
    from momp.utils.printing import tuple_to_str
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    from matplotlib.ticker import MaxNLocator, FixedLocator
    from matplotlib.gridspec import GridSpec
    from matplotlib import colors as mcolors


    cfg, setting = get_cfg(), get_setting()

    model_list = cfg.model_list
    model_list = (cfg.ref_model,) + model_list
    verification_window = cfg.verification_window_list[0]
    print(verification_window)
    day_bin = tuple_to_str(verification_window)
    
    var_name = "mean_mae"

    n = len(model_list)
    #fig = plt.figure(figsize=(8, 5/4*n), constrained_layout=True)
    fig = plt.figure(figsize=(8, 5/4*n))
    axes = []
    ims = []
    fig_width, fig_height = fig.get_size_inches()
    text_scale =  min(fig_width/n, fig_height/1) / 5 * 1.2
    #print(txt_scale)
    #import sys
    #sys.exit()

    gs = GridSpec(
        2, n,
        height_ratios=[1, 0.043],   # plots, then colorbars
        hspace=0.02,
        wspace=0.07
    )

    for i, model in enumerate(model_list):
        fi = os.path.join(cfg.dir_out,"spatial_metrics_{}_{}.nc")
        fi = fi.format(model, day_bin)
        ds = xr.open_dataset(fi)
        da = ds[var_name]
        ds.close()

        combi = (model, verification_window)
        if model == cfg.ref_model:
            cfg_ref, _ = ref_cfg_layout(cfg, ref_model=model, verification_window=verification_window)
            case = make_case(Case, combi, vars(cfg_ref))
        else:
            case = make_case(Case, combi, vars(cfg))

        case_cfg = {**asdict(case), **asdict(setting)}

        if i > 0:
            show_ylabel, title, cmap = False, None, 'RdBu_r'
        else:
            show_ylabel, title, cmap = True, f"{var_name} {day_bin} day", 'YlOrRd'

        print(i, show_ylabel, title, cmap)

        #ax = fig.add_subplot(1, n, i+1, projection=ccrs.PlateCarree())
        ax = fig.add_subplot(gs[0, i], projection=ccrs.PlateCarree())
        #ax = fig.add_subplot(gs[0, i])

        fig, ax, im, _ = spatial_metrics_map(da, model, fig=fig, ax=ax, domain_mask=True, 
                                         show_ylabel=show_ylabel, cmap=cmap, title=title, panel=True, 
                                         text_scale=text_scale, **case_cfg)

        axes.append(ax)
        ims.append(im)
        i += 1


    #cbar_ax_ref = fig.add_axes([0.10, 0.05, 0.30, 0.02])
    #cbar_ax_mod = fig.add_axes([0.40, 0.05, 0.30, 0.02])
    #cb_ref = fig.colorbar(ims[0], cax=cbar_ax_ref, orientation='horizontal')
    #cb_mod = fig.colorbar(ims[1], cax=cbar_ax_mod, orientation='horizontal')

    #cbar_ref = fig.colorbar(ims[0], ax=axes[0], orientation='horizontal', fraction=0.046, pad=0.02)
    #cbar_ref.set_label("Reference units")
    #
    #cbar_mod = fig.colorbar(ims[1], ax=axes[1:], orientation='horizontal', fraction=0.046, pad=0.02)
    #cbar_mod.set_label("Model units")

#    cbar_ref.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
#    cbar_mod.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
#
#    ticks = cb_ref.get_ticks()
#    cb_ref.set_ticks(ticks[::2])

    cax_ref = fig.add_subplot(gs[1, 0])
    cbar_ref = fig.colorbar(
        ims[0],
        cax=cax_ref,
        orientation='horizontal'
    )
    
    #cax_mod = fig.add_subplot(gs[1, 1:])

    gs_cell = gs[1, 1:]  # full width across remaining panels
    pos = gs_cell.get_position(fig)  # bounding box of this cell
    # shrink width by 10% on each side
    cax_mod = fig.add_axes([pos.x0 + 0.1, pos.y0, pos.width * 0.6, pos.height])

    cbar_mod = fig.colorbar(
        ims[1],
        cax=cax_mod,
        orientation='horizontal'
    )


    for cb in (cbar_ref, cbar_mod):
        cb.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        for i, label in enumerate(cb.ax.get_xticklabels()):
            if i % 2 == 1:
                label.set_visible(False)


    for cb in (cbar_ref, cbar_mod):
        # Access the bins from BoundaryNorm
        if isinstance(cb.norm, mcolors.BoundaryNorm):
            boundaries = cb.norm.boundaries  # the levels
            # Compute centers of each bin
            tick_locs = 0.5 * (boundaries[:-1] + boundaries[1:])
            #cb.set_ticks(tick_locs_to_show)
            tick_locs_to_show = tick_locs[::2]
            cb.set_ticks(tick_locs_to_show)

            # Set tick labels as integers
            #cb.set_ticklabels(np.arange(len(tick_locs)))

            cb.ax.xaxis.set_minor_locator(plt.NullLocator())
            # Label every 4th tick
            #tick_labels = [str(i) if (idx % 4 == 0) else ''
            #               for idx, i in enumerate(np.arange(len(tick_locs)))]

            tick_labels = [str(int(i)) for i in np.arange(len(tick_locs_to_show))]

            cb.set_ticklabels(tick_labels)
            cb.ax.tick_params(labelsize=7, direction='in', length=1.5)



    fig.suptitle(f"{var_name} (in days) {day_bin} day forecast", fontsize=15)
    plt.tight_layout(rect=[0, 0, 0.99, 1])
    plt.show()































