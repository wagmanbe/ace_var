#!/bin/bash
python rainrate_amount_calculator_ace_or_e3sm.py \
        --in_file /pscratch/sd/m/mahf708/ACE2-EAMv3/picontrol_run/seg_0016/atmosphere/6h_surface_surface_precipitation_rate_predictions.nc \
        --out_file /pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_naser_picontrol.nc \
        --precip_name surface_precipitation_rate

      #--start_time 1001-01-01 \
      #--end_time 1005-12-01 \



python rainrate_amount_calculator_ace_or_e3sm.py \
        --in_file /pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/sample_0.nc \
        --out_file /pscratch/sd/w/wagmanbe/rainrate_compare/inf_test4/surface_precipitation_rate/pdf_6hrly_197601_198012.nc \
      --start_time 1976-02-01 \
      --end_time 1980-12-01 \
      --precip_name surface_precipitation_rate



python rainrate_amount_calculator_ace_or_e3sm.py \
        --in_file /pscratch/sd/w/wagmanbe/rainrate_compare/v3.LR.amip_0101/post/atm/180x360_aave/ts/6-hourly/5yr/PRECT_197601_198012.nc \
        --out_file /pscratch/sd/w/wagmanbe/rainrate_compare/v3.LR.amip_0101/post/atm/180x360_aave/ts/6-hourly/5yr/pdf_6hrly_197601_198012.nc \
      --start_time 1976-02-01 \
      --end_time 1980-12-01 \
      --precip_name PRECT