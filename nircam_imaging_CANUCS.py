# Import relevant libraries
from pandeia.engine.perform_calculation import perform_calculation
import json
import astropy.io.fits as pyfits
import numpy as np

# OBSERVATIONS: Filter
def get_channel(filt):
    lam = int(filt[1:4])  # f200w -> 200
    if lam < 240:
        ch = 'sw'  # Short Wavelength Channel (0.6 - 2.3 microns)
    else:
        ch = 'lw'  # Long  Wavelength Channel (2.4 - 5.0 microns)
    return ch

def assign_filter(imgr_data, filt):
    imgr_data['configuration']['instrument']['filter'] = filt
    ch = get_channel(filt)
    imgr_data['configuration']['instrument']['aperture'] = ch
    imgr_data['configuration']['instrument']['mode'] = ch+'_imaging'
    return imgr_data

# RESULTS: SUMMARY
def print_summary():
    exptime = results['scalar']['exposure_time']
    snr = results['scalar']['sn']
    readmode = imgr_data['configuration']['detector']['readmode']
    ngroup = imgr_data['configuration']['detector']['ngroup']
    nint = imgr_data['configuration']['detector']['nint']
    nexp = imgr_data['configuration']['detector']['nexp']
    line = '%s  %s  %2d    %2d   %2d  %8.2f  %7.2f' % (filt, readmode.ljust(8), ngroup, nint, nexp, exptime, snr)
    print line 

# RESULTS: ALL
def print_results():
    keys = results['scalar'].keys()
    keys.sort()
    for key in keys:
        print key.ljust(20), results['scalar'][key]

# LOAD DEFAULT PARAMETERS for NIRCam Imaging
jsonfile = 'nircam_imaging.json'  
with open(jsonfile) as f:
    imgr_data = json.load(f)

# LOAD BACKGROUND for RA, Dec, and date (computed by online ETC GUI and exported)
bg_file = 'backgrounds_Abell370_20190830.fits'
bg_table = pyfits.getdata(bg_file)
imgr_data['background'] = [bg_table['wavelength'],bg_table['background']] # wavelength in micron, SB in MJy/sr

# SCENE: Object magnitude
imgr_data['scene'][0]['spectrum']['normalization']['norm_flux'] = 28.1  # AB mag
imgr_data['scene'][0]['spectrum']['normalization']['norm_fluxunit'] = 'abmag'

# OBSERVATIONS: FILTER
filt = 'f200w'
imgr_data = assign_filter(imgr_data, filt)

# OBSERVATIONS: Detector Readout (Exposure Time)
imgr_data['configuration']['detector']['readmode'] = readmode = 'deep8'
imgr_data['configuration']['detector']['ngroup'] = ngroup = 5
imgr_data['configuration']['detector']['nint'] = nint = 1
imgr_data['configuration']['detector']['nexp'] = nexp = 6  # dithers

# RUN ETC
#results = perform_calculation(imgr_data)
#print_summary()

# LOOP OVER FILTERS and READOUT CONFIGURATIONS

config1 = 5, 'deep8'   # EXECUTED ONCE  (during NIRISS WFSS)
config2 = 4, 'medium8' # EXECUTED TWICE (during NIRISS direct images)
configs = config1, config2

filts = 'f090w f115w f150w f200w f277w f356w f410m f444w'.split()
print 'filter pattern ngroup nint nexp  exptime     snr'
for filt in filts:
    imgr_data = assign_filter(imgr_data, filt)
    fluxes = []
    noises = []
    
    # PHOTOMETRIC APERTURE FOR DETECTION
    if get_channel(filt) == 'sw':
        imgr_data['strategy']['aperture_size'] = 0.08  # radius (default 0.1")
        imgr_data['strategy']['sky_annulus'] = 0.6, 0.99  # (default 0.22" - 0.4")
    else:
        imgr_data['strategy']['aperture_size'] = 0.16  # radius (default 0.1")
        imgr_data['strategy']['sky_annulus'] = 1.2, 1.95  # (default 0.22" - 0.4")
    
    for config in configs:
        ngroup, readmode = config
        imgr_data['configuration']['detector']['ngroup'] = ngroup
        imgr_data['configuration']['detector']['readmode'] = readmode
        results = perform_calculation(imgr_data)
        print_summary()
        flux  = results['scalar']['extracted_flux']
        noise = results['scalar']['extracted_noise']
        fluxes.append(flux)
        noises.append(noise)
    # Determine total SNR for all 3 observations:
    #   config1 is executed once
    #   config2 is executed twice
    flux = fluxes[0] + fluxes[1] + fluxes[1]  # add fluxes
    noise = np.sqrt(noises[0]**2 + noises[1]**2 + noises[1]**2)  # add noise in quadrature
    snr = flux / noise
    print '%s  %6.4f  %6.4f  %6.4f  %6.4f  %5.2f' % (filt, fluxes[0], noises[0], fluxes[1], noises[1], snr)

# RESULT:
"""
f090w  deep8      5     1    6   5735.16     8.85
f090w  medium8    4     1    6   2513.16     5.29
f090w  0.3434  0.0388  0.3434  0.0649  10.34
f115w  deep8      5     1    6   5735.16    10.42
f115w  medium8    4     1    6   2513.16     6.23
f115w  0.4041  0.0388  0.4041  0.0648  12.18
f150w  deep8      5     1    6   5735.16    12.47
f150w  medium8    4     1    6   2513.16     7.49
f150w  0.4929  0.0395  0.4929  0.0658  14.62
f200w  deep8      5     1    6   5735.16    14.88
f200w  medium8    4     1    6   2513.16     8.88
f200w  0.5694  0.0383  0.5694  0.0641  17.35
f277w  deep8      5     1    6   5735.16    10.91
f277w  medium8    4     1    6   2513.16     6.94
f277w  0.6438  0.0590  0.6438  0.0928  13.42
f356w  deep8      5     1    6   5735.16    11.48
f356w  medium8    4     1    6   2513.16     7.28
f356w  0.6668  0.0581  0.6668  0.0915  14.10
f410m  deep8      5     1    6   5735.16     6.31
f410m  medium8    4     1    6   2513.16     3.88
f410m  0.2984  0.0473  0.2984  0.0769   7.55
f444w  deep8      5     1    6   5735.16     7.30
f444w  medium8    4     1    6   2513.16     4.92
f444w  0.6650  0.0911  0.6650  0.1351   9.42
"""
