import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pdb

def plot_rainrate_pdfs(
    file1,
    file2,
    file3,
    label1,
    label2,
    label3,
                    tropics_only=False,
                    land_only=False,
    ocean_only=False,
    specific_lat_lon=False,
    landmask=None,
    locate_anomaly=False,
):
    ds1 = xr.open_dataset(file1)
    ds2 = xr.open_dataset(file2)
    ds3 = xr.open_dataset(file3)

    hist1 = ds1["amount"]
    hist2 = ds2["amount"]
    hist3 = ds3["amount"]

    bin_edges1, bin_centers1 = ds1["edges"], ds1["centers"]
    bin_edges2, bin_centers2 = ds2["edges"], ds2["centers"]
    bin_edges3, bin_centers3 = ds3["edges"], ds3["centers"]

    suffix = ""

    if tropics_only:
        max_lat = 25.0
        hist1 = hist1.where(np.abs(hist1.lat) <= max_lat, drop=True)
        hist2 = hist2.where(np.abs(hist2.lat) <= max_lat, drop=True)
        hist3 = hist3.where(np.abs(hist3.lat) <= max_lat, drop=True)
        suffix += "_tropics"

    land_mask_3d = None
    if land_only or ocean_only:
        if landmask is None:
            raise ValueError("landmask path must be provided when using land_only or ocean_only.")
        landfrac = xr.open_dataset(landmask)["LANDFRAC"]
        if land_only:
            land_mask = landfrac > 0.5
            suffix += "_land"
        else:
            land_mask = landfrac < 0.5
            suffix += "_ocean"
        land_mask_3d = land_mask.broadcast_like(hist1)
        hist1 = hist1.where(land_mask_3d)
        hist2 = hist2.where(land_mask_3d)
        hist3 = hist3.where(land_mask_3d)

    if specific_lat_lon:
        lat_spec=specific_lat_lon[0]
        lon_spec=specific_lat_lon[1]
        hist1 = hist1.sel(lat = lat_spec, lon = lon_spec, method='nearest',drop=False)
        hist2 = hist2.sel(lat = lat_spec, lon = lon_spec, method='nearest',drop=False)
        hist3 = hist3.sel(lat = lat_spec, lon = lon_spec, method='nearest',drop=False)
        suffix+=f'_lat{lat_spec}_lon{lon_spec}'

    if locate_anomaly:
        # Identify centers within 0.8‑1.2 mm day⁻¹
        centers_in_range = (bin_centers1 >= 0.8) & (bin_centers1 <= 1.2)
        selected_centers = bin_centers1.where(centers_in_range, drop=True)

        # Subset histogram to those centers
        sub_hist1 = hist1.sel(centers=selected_centers)

        # Build spatial mask: True where any selected bin > 0.5
        mask = (sub_hist1 > 0.5).any("centers")
        mask = mask.squeeze(drop=True)          # <<< **Important fix**

        proj = ccrs.PlateCarree()
        fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=dict(projection=proj))

        extent = [
            float(mask.lon.min()), float(mask.lon.max()),   # left, right
            float(mask.lat.min()), float(mask.lat.max())    # bottom, top
        ]

        mask_img = ax.imshow(
            mask,
            origin='lower',           # aligns the first row with the southernmost latitude
            extent=extent,
            transform=proj,
            cmap="gray_r",
            interpolation='nearest',
            rasterized=True,
        )

        ax.coastlines(resolution="110m")
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)
        ax.set_global()
        ax.set_title("Spatial mask (0.8‑1.2 mm day⁻¹, value > 0.5)")

        cbar = plt.colorbar(mask_img, ax=ax,
                            orientation="vertical", pad=0.02,
                            label="Mask (1=keep, 0=mask out)")
        plt.tight_layout()
        plt.savefig("mask1.png", dpi=250)
        plt.close(fig)

    # Area weighting by cosine of latitude
    weights1 = np.cos(np.deg2rad(hist1.lat))
    weights2 = np.cos(np.deg2rad(hist2.lat))
    weights3 = np.cos(np.deg2rad(hist3.lat))

    if not specific_lat_lon:
        hist1_mean = hist1.weighted(weights1).mean(("lon", "lat"))
        hist2_mean = hist2.weighted(weights2).mean(("lon", "lat"))
        hist3_mean = hist3.weighted(weights3).mean(("lon", "lat"))
    else:
        hist1_mean, hist2_mean, hist3_mean = hist1, hist2, hist3

    plt.figure()
    plt.plot(bin_centers1, hist1_mean, label=label1)
    plt.plot(bin_centers2, hist2_mean, label=label2)
    plt.plot(bin_centers3, hist3_mean, label=label3)
    plt.xscale("log")
    plt.title("PDFs for rain rate")
    plt.xlabel("Rain rate mm/day")
    plt.ylabel("Amount mm/day")
    plt.xlim(1e-2, 1e3)
    plt.legend()
    plt.savefig(f"rain_rate{suffix}_pdf.png")
    plt.close()

    ds1.close()
    ds2.close()
    ds3.close()


plot_rainrate_pdfs(
    "/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_197101_200012.nc",
    "/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_naser_picontrol.nc",
    "/pscratch/sd/w/wagmanbe/rainrate_compare/v3.LR.amip_0101/post/atm/180x360_aave/ts/6-hourly/5yr/pdf_6hrly_197601_198012.nc",
    "ACE2-EAMv3-AMIP",
    "ACE2-pi-Naser",
    "E3SMv3-AMIP",
    tropics_only=False,
    land_only=False,
    ocean_only=False,
    specific_lat_lon=False, #[-110,30],
    landmask="/global/cfs/cdirs/e3sm/emulate/ace/e3smv3-amip/e3sm-v3-amip-180x360-gaussian/landmask_e3sm_180x360_aave/landfrac_180x360_aave.nc",
    locate_anomaly=True,
)


