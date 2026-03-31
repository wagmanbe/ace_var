# plot_rainrate.py

import xarray as xr
import matplotlib.pyplot as plt
import pdb
import numpy as np

def plot_rainrate_pdfs(file1, file2, label1, label2):
    # Open the first netcdf file
    ds1 = xr.open_dataset(file1)
    # Open the second netcdf file
    ds2 = xr.open_dataset(file2)

    # Extract the histogram data from the first file
    hist1 = ds1['amount']
    # Extract the histogram data from the second file
    hist2 = ds2['amount']

    bin_edges1, bin_centers1 = ds1['edges'], ds1['centers']
    bin_edges2, bin_centers2 = ds2['edges'], ds2['centers']

    # Average the histograms over all grid points. 
    weights1 = np.cos(np.deg2rad(hist1.lat))
    weights2 = np.cos(np.deg2rad(hist2.lat))


    hist1_weighted = hist1.weighted(weights1)
    hist1_mean = hist1_weighted.mean(('lon','lat'))

    hist2_weighted = hist2.weighted(weights2)
    hist2_mean = hist2_weighted.mean(('lon','lat'))

    # Create the plot
    plt.plot(bin_centers1, hist1_mean, label=label1)
    plt.plot(bin_centers2, hist2_mean, label=label2)

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
    plt.savefig('rain_rate_pdf.png')

    # Close the netcdf files
    ds1.close()
    ds2.close()

# Example usage
plot_rainrate_pdfs('/pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_197601_198012.nc',
                    '/pscratch/sd/w/wagmanbe/rainrate_compare/v3.LR.amip_0101/post/atm/180x360_aave/ts/6-hourly/5yr/pdf_6hrly_197601_198012.nc',
                    'ACE2-EAMv3-AMIP',
                    'E3SMv3-AMIP')