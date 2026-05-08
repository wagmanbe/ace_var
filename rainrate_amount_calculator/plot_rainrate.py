import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pdb

def plot_rainrate_pdfs(
    files,          # list of file paths (e.g. [file1, file2, ..., file5])
    labels,         # list of corresponding labels
    tropics_only=False,
    land_only=False,
    ocean_only=False,
    specific_lat_lon=False,
    landmask=None,
    locate_anomaly=False,
):
    """
    Plot PDFs of rain‑rate amount from one or more NetCDF files.

    Parameters
    ----------
    files : list[str]
        Paths to the NetCDF files (must be the same length as ``labels``).
    labels : list[str]
        Human‑readable legend entries for each file.
    tropics_only, land_only, ocean_only, specific_lat_lon, landmask, locate_anomaly
        Optional sub‑setting flags – behaviour unchanged from the original script.
    """
    if len(files) != len(labels):
        raise ValueError("``files`` and ``labels`` must have the same length.")

    # ------------------------------------------------------------------
    # 1️⃣ Open all datasets and collect the needed variables
    # ------------------------------------------------------------------
    datasets   = [xr.open_dataset(f) for f in files]
    histograms = [ds["amount"] for ds in datasets]

    # Assume bin edges/centers are identical across files; grab from the first.
    bin_edges, bin_centers = datasets[0]["edges"], datasets[0]["centers"]

    suffix = ""

    # ------------------------------------------------------------------
    # 2️⃣ Optional sub‑setting (tropics, land/ocean, specific point)
    # ------------------------------------------------------------------
    if tropics_only:
        max_lat = 25.0
        histograms = [
            h.where(np.abs(h.lat) <= max_lat, drop=True) for h in histograms
        ]
        suffix += "_tropics"

    if land_only or ocean_only:
        if landmask is None:
            raise ValueError(
                "landmask path must be provided when using land_only or ocean_only."
            )
        landfrac = xr.open_dataset(landmask)["LANDFRAC"]
        land_mask = landfrac > 0.5 if land_only else landfrac < 0.5
        suffix += "_land" if land_only else "_ocean"
        # Broadcast mask to histogram shape and mask each histogram
        mask_3d = land_mask.broadcast_like(histograms[0])
        histograms = [h.where(mask_3d) for h in histograms]

    if specific_lat_lon:
        lat_spec, lon_spec = specific_lat_lon
        histograms = [
            h.sel(lat=lat_spec, lon=lon_spec, method="nearest", drop=False)
            for h in histograms
        ]
        suffix += f"_lat{lat_spec}_lon{lon_spec}"

    # ------------------------------------------------------------------
    # 3️⃣ (Optional) Locate anomaly – unchanged, uses only the first dataset
    # ------------------------------------------------------------------
    if locate_anomaly:
        centers_in_range = (bin_centers >= 0.8) & (bin_centers <= 1.2)
        selected_centers = bin_centers.where(centers_in_range, drop=True)

        sub_hist = histograms[0].sel(centers=selected_centers)
        mask = (sub_hist > 0.5).any("centers").squeeze(drop=True)

        proj = ccrs.PlateCarree()
        fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=dict(projection=proj))

        extent = [
            float(mask.lon.min()), float(mask.lon.max()),
            float(mask.lat.min()), float(mask.lat.max()),
        ]

        mask_img = ax.imshow(
            mask,
            origin="lower",
            extent=extent,
            transform=proj,
            cmap="gray_r",
            interpolation="nearest",
            rasterized=True,
        )

        ax.coastlines(resolution="110m")
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)
        ax.set_global()
        ax.set_title("Spatial mask (0.8‑1.2 mm day⁻¹, value > 0.5)")

        plt.colorbar(mask_img, ax=ax, orientation="vertical", pad=0.02,
                     label="Mask (1=keep, 0=mask out)")
        plt.tight_layout()
        plt.savefig("mask1.png", dpi=250)
        plt.close(fig)

    # ------------------------------------------------------------------
    # 4️⃣ Area‑weighting (cosine of latitude) and mean calculation
    # ------------------------------------------------------------------
    # Compute a weight array for each histogram (same shape, only latitude matters)
    weights = [
        np.cos(np.deg2rad(h.lat)) for h in histograms
    ]

    if not specific_lat_lon:
        means = [
            h.weighted(w).mean(("lon", "lat"))
            for h, w in zip(histograms, weights)
        ]
    else:
        # When a single point is selected we just keep the raw values
        means = histograms

    # ------------------------------------------------------------------
    # 5️⃣ Plot all PDFs
    # ------------------------------------------------------------------
    plt.figure()
    for mean, lbl in zip(means, labels):
       # Convert to plain NumPy arrays to avoid x‑y dimension mismatches.
       lw,ls=2.0,'-'
       if 'Wag' in lbl:
           lw,ls = 4.0,'--'
       plt.plot(bin_centers.values, mean.values, label=lbl, linewidth=lw, linestyle=ls, alpha=0.8 )

    plt.xscale("log")
    plt.title("PDFs for rain rate")
    plt.xlabel("Rain rate mm/day")
    plt.ylabel("Amount mm/day")
    plt.xlim(1e-2, 1e3)
    plt.legend()
    plt.savefig(f"rain_rate{suffix}_pdf.png")
    plt.close()

    # ------------------------------------------------------------------
    # 6️⃣ Clean up
    # ------------------------------------------------------------------
    for ds in datasets:
        ds.close()


# ----------------------------------------------------------------------
# Example usage – now simply pass a list of five files / labels
# ----------------------------------------------------------------------
plot_rainrate_pdfs(
    files=[
        "/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_197101_200012.nc",
        "/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_198501_training.nc",
        "/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_naser_picontrol.nc",
        "/pscratch/sd/w/wagmanbe/rainrate_compare/v3.LR.amip_0101/post/atm/180x360_aave/ts/6-hourly/5yr/pdf_6hrly_197601_198012.nc",
        #"/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test1/surface_precipitation_rate/pdf_6hrly_sample0.nc",          
        "/pscratch/sd/w/wagmanbe/rainrate_compare/amip.train_data.ace.19800101/surface_precipitation_rate/pdf_6hrly_sample0.nc"
    ],
    labels=[
        "ACE2-EAMv3-AMIP-Wag",
        "Training Data 1985-01",
        "ACE2-pi-Naser",
        "E3SMv3-AMIP",
        #"ACE2-EAMv3-AMIP-Wag-1971_frc_only",                  
        "ACE2-EAMv3-AMIP-Ola"
    ],
    tropics_only=False,
    land_only=False,
    ocean_only=False,
    specific_lat_lon=False,
    landmask="/global/cfs/cdirs/e3sm/emulate/ace/e3smv3-amip/e3sm-v3-amip-180x360-gaussian/landmask_e3sm_180x360_aave/landfrac_180x360_aave.nc",
    locate_anomaly=True,
)