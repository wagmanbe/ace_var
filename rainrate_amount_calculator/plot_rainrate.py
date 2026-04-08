# plot_rainrate.py

import xarray as xr
import matplotlib.pyplot as plt
import pdb
import numpy as np

def plot_rainrate_pdfs(file1, file2, file3, label1, label2, label3, tropics_only=False):
    # Open the first netcdf file
    ds1 = xr.open_dataset(file1)
    # Open the second netcdf file
    ds2 = xr.open_dataset(file2)
    ds3 = xr.open_dataset(file3)


    # Extract the histogram data from the first file
    hist1 = ds1['amount']
    # Extract the histogram data from the second file
    hist2 = ds2['amount']
    hist3 = ds3['amount']
   


    bin_edges1, bin_centers1 = ds1['edges'], ds1['centers']
    bin_edges2, bin_centers2 = ds2['edges'], ds2['centers']
    bin_edges3, bin_centers3 = ds3['edges'], ds3['centers']



    if tropics_only:
        max_lat = 25.0
        hist1 = hist1.where(np.abs(hist1.lat) <= max_lat, drop=True)
        hist2 = hist2.where(np.abs(hist2.lat) <= max_lat, drop=True)
        hist3 = hist3.where(np.abs(hist3.lat) <= max_lat, drop=True)


    # Average the histograms over all grid points. 
    weights1 = np.cos(np.deg2rad(hist1.lat))
    weights2 = np.cos(np.deg2rad(hist2.lat))
    weights3 = np.cos(np.deg2rad(hist3.lat))


    hist1_weighted = hist1.weighted(weights1)
    hist1_mean = hist1_weighted.mean(('lon','lat'))

    hist2_weighted = hist2.weighted(weights2)
    hist2_mean = hist2_weighted.mean(('lon','lat'))

    hist3_weighted = hist3.weighted(weights3)
    hist3_mean = hist3_weighted.mean(('lon','lat'))

    # Create the plot
    plt.plot(bin_centers1, hist1_mean, label=label1)
    plt.plot(bin_centers2, hist2_mean, label=label2)
    plt.plot(bin_centers3, hist3_mean, label=label3)

    # Set the x-axis to logarithmic scale
    plt.xscale('log')

    # Add title and labels
    plt.title('PDFs for rain rate')
    plt.xlabel('Rain rate mm/day')
    plt.ylabel('Amount mm/day')
    plt.xlim(10**-2, 10**3) 

    # Add legend
    plt.legend()

    # Show the plot
    if tropics_only:
        plt.savefig('rain_rate_tropics_pdf.png')
    else:
        plt.savefig('rain_rate_pdf.png')

    # Close the netcdf files
    ds1.close()
    ds2.close()
    ds3.close()

# Example usage
plot_rainrate_pdfs('/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_197601_198012.nc',
                 '/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_naser_picontrol.nc',
                 '/pscratch/sd/w/wagmanbe/rainrate_compare/v3.LR.amip_0101/post/atm/180x360_aave/ts/6-hourly/5yr/pdf_6hrly_197601_198012.nc',
                    'ACE2-EAMv3-AMIP',
                    'ACE2-pi-Naser',
                    'E3SMv3-AMIP',
                    tropics_only=True)