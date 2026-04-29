#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Three‑panel precipitation map (file‑1, file‑2, file‑2‑file‑1).

Uses:
  • xarray for I/O and arithmetic
  • cartopy + matplotlib for the geographic plots
"""

import pathlib
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point   # ← new import

# ----------------------------------------------------------------------
# 👉 USER SETTINGS – edit these ------------------------------------------------
# ----------------------------------------------------------------------
FILE_1 = pathlib.Path(
    "/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/sample_1.nc"
)
FILE_2 = pathlib.Path(
    "/pscratch/sd/m/mahf708/ACE2-EAMv3/picontrol_run/seg_0016/atmosphere/6h_surface_surface_precipitation_rate_predictions.nc"
)

# Name of the precipitation variable inside the NetCDF files
PRECIP_VAR = "surface_precipitation_rate"

# ----------------------------------------------------------------------
# Helper functions ----------------------------------------------------
# ----------------------------------------------------------------------
def format_lon(x, _=None):
    """0‑360° → E/W labels."""
    if x < 0:
        return f"{-x:.0f}°W"
    elif x > 180:
        return f"{360 - x:.0f}°W"
    else:
        return f"{x:.0f}°E"


def format_lat(y, _=None):
    """N / S label."""
    return f"{abs(y):.0f}°{'N' if y >= 0 else 'S'}"


def open_precip(path: pathlib.Path) -> xr.DataArray:
    """Open a NetCDF file and return a DataArray with standard lon/lat.

    The function:
      • extracts ``PRECIP_VAR``
      • renames coordinates to ``lon`` and ``lat``
      • wraps longitudes to the 0‑360° range expected by Cartopy.
    """
    ds = xr.open_dataset(path)
    if PRECIP_VAR not in ds:
        raise KeyError(f"Variable '{PRECIP_VAR}' not found in {path}")
    da = ds[PRECIP_VAR]

    # standardise coordinate names
    lon_coord = next(c for c in da.coords if "lon" in c.lower())
    lat_coord = next(c for c in da.coords if "lat" in c.lower())
    da = da.rename({lon_coord: "lon", lat_coord: "lat"})

    # wrap longitudes to 0‑360°
    if da.lon.max() > 180:
        da = da.assign_coords(lon=((da.lon + 360) % 360)).sortby("lon")
    else:
        da = da.sortby("lon")
    return da


# ----------------------------------------------------------------------
# Load both datasets and compute the mean over time
# ----------------------------------------------------------------------
precip1 = open_precip(FILE_1).mean(dim="time")
precip2 = open_precip(FILE_2).mean(dim="time")

# Convert from m s⁻¹ → mm day⁻¹ (1 m s⁻¹ = 86 400 mm day⁻¹)
precip1 = precip1 * 86_400.0
precip2 = precip2 * 86_400.0

diff = precip1 - precip2

# ----------------------------------------------------------------------
# Plot the three panels
# ----------------------------------------------------------------------
def plot_three_panel(
    da1: xr.DataArray,
    da2: xr.DataArray,
    da_diff: xr.DataArray,
    units: str = "mm day⁻¹",
    cmap: str = "viridis",
    diff_cmap: str = "RdBu_r",
):
    """
    Create a 1 × 3 Cartopy figure.

    * ``imshow`` is used (instead of ``pcolormesh``) because it works with
      plain 2‑D NumPy arrays.
    * A cyclic point is added to each field so the map wraps cleanly at the
      0°/360° seam.
    """
    proj = ccrs.PlateCarree()
    fig, axs = plt.subplots(
        1,
        3,
        figsize=(20, 6),
        subplot_kw=dict(projection=proj),
        constrained_layout=True,
    )

    # --------------------------------------------------------------
    # 1.  Remove any singleton dimensions
    # --------------------------------------------------------------
    da1 = da1.squeeze()
    da2 = da2.squeeze()
    da_diff = da_diff.squeeze()

    # --------------------------------------------------------------
    # 2.  Add cyclic points (required for a seamless global plot)
    # --------------------------------------------------------------
    # ``add_cyclic_point`` returns the data array with an extra column and
    # the corresponding longitude array.
    data1_cyc, lon1_cyc = add_cyclic_point(da1.values, coord=da1.lon.values)
    data2_cyc, lon2_cyc = add_cyclic_point(da2.values, coord=da2.lon.values)
    diff_cyc,  lond_cyc = add_cyclic_point(da_diff.values, coord=da_diff.lon.values)

    # --------------------------------------------------------------
    # 3.  Define a common colour scale for the two precipitation fields
    # --------------------------------------------------------------
    vmax = np.nanmax([data1_cyc.max(), data2_cyc.max()])
    vmin = 0.0

    # ---------- Panel 1 – first file ----------
    im0 = axs[0].imshow(
        data1_cyc,
        extent=[lon1_cyc.min(), lon1_cyc.max(),
                float(da1.lat.min()), float(da1.lat.max())],
        origin="lower",
        transform=proj,
        cmap=cmap,
        interpolation="nearest",
        vmin=vmin,
        vmax=vmax,
    )
    axs[0].set_title("ACE2-EAMv3-AMIP")
    axs[0].coastlines(resolution="110m")
    axs[0].add_feature(cfeature.BORDERS, linewidth=0.5)
    axs[0].set_global()

    # ---------- Panel 2 – second file ----------
    im1 = axs[1].imshow(
        data2_cyc,
        extent=[lon2_cyc.min(), lon2_cyc.max(),
                float(da2.lat.min()), float(da2.lat.max())],
        origin="lower",
        transform=proj,
        cmap=cmap,
        interpolation="nearest",
        vmin=vmin,
        vmax=vmax,
    )
    axs[1].set_title("ACE2-EAMv3-PI")
    axs[1].coastlines(resolution="110m")
    axs[1].add_feature(cfeature.BORDERS, linewidth=0.5)
    axs[1].set_global()

    # ---------- Panel 3 – difference ----------
    diff_abs_max = np.nanmax(np.abs(diff_cyc))
    im2 = axs[2].imshow(
        diff_cyc,
        extent=[lond_cyc.min(), lond_cyc.max(),
                float(da_diff.lat.min()), float(da_diff.lat.max())],
        origin="lower",
        transform=proj,
        cmap=diff_cmap,
        interpolation="nearest",
        vmin=-diff_abs_max,
        vmax=diff_abs_max,
    )
    axs[2].set_title("Difference ACE2(AMIP – PI")
    axs[2].coastlines(resolution="110m")
    axs[2].add_feature(cfeature.BORDERS, linewidth=0.5)
    axs[2].set_global()

    # ----- Colourbars -----
    fig.colorbar(
        im0,
        ax=[axs[0], axs[1]],
        orientation="vertical",
        pad=0.02,
        label=f"Precipitation ({units})",
    )
    fig.colorbar(
        im2,
        ax=axs[2],
        orientation="vertical",
        pad=0.02,
        label=f"Difference ({units})",
    )

    # ----- Nice lon/lat tick labels (optional) -----
    for ax in axs:
        ax.set_xticks(np.arange(-180, 181, 60), crs=proj)
        ax.set_yticks(np.arange(-90, 91, 30), crs=proj)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_lon))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_lat))

    fig.suptitle(
        "Total Precipitation Rate",
        fontsize=16,
    )

    # Save before showing so the PNG matches the displayed figure
    plt.savefig("mean_precip_map.png", dpi=150)
    plt.show()


# ----------------------------------------------------------------------
# Run the plot
# ----------------------------------------------------------------------
plot_three_panel(precip1, precip2, diff)

# Close the datasets (good practice)
precip1.close()
precip2.close()