# Import relevant libraries
from pandeia.engine.perform_calculation import perform_calculation
import json
import astropy.io.fits as pyfits

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

# PHOTOMETRIC APERTURE FOR DETECTION
#imgr_data['strategy']['aperture_size'] = 0.08  # radius (default 0.1")
#imgr_data['strategy']['sky_annulus'] = 0.72, 0.96  # (default 0.22" - 0.4")

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
results = perform_calculation(imgr_data)
#print_summary()

# LOOP OVER FILTERS
filts = 'f090w f115w f150w f200w f277w f356w f410m f444w'.split()
print 'filter pattern ngroup nint nexp  exptime     snr'
for filt in filts:
    imgr_data = assign_filter(imgr_data, filt)

    # PHOTOMETRIC APERTURE FOR DETECTION
    if get_channel(filt) == 'sw':
        imgr_data['strategy']['aperture_size'] = 0.08  # radius (default 0.1")
        imgr_data['strategy']['sky_annulus'] = 0.6, 0.99  # (default 0.22" - 0.4")
    else:
        imgr_data['strategy']['aperture_size'] = 0.16  # radius (default 0.1")
        imgr_data['strategy']['sky_annulus'] = 1.2, 1.95  # (default 0.22" - 0.4")
    
    results = perform_calculation(imgr_data)
    print_summary()

"""
filter pattern ngroup nint nexp  exptime     snr
f090w  deep8      5     1    6   5735.16     8.85
f115w  deep8      5     1    6   5735.16    10.42
f150w  deep8      5     1    6   5735.16    12.47
f200w  deep8      5     1    6   5735.16    14.88
f277w  deep8      5     1    6   5735.16    10.91
f356w  deep8      5     1    6   5735.16    11.48
f410m  deep8      5     1    6   5735.16     6.31
f444w  deep8      5     1    6   5735.16     7.30
"""
