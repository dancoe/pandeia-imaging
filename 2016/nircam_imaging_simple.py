# Import relevant libraries
from pandeia.engine.perform_calculation import perform_calculation
import json
import astropy.io.fits as pyfits

# LOAD DEFAULT PARAMETERS for NIRCam Imaging
jsonfile = 'nircam_imaging.json'  
with open(jsonfile) as f:
    imgr_data = json.load(f)

# LOAD BACKGROUND for RA, Dec, and date (computed by online ETC GUI and exported)
bg_file = 'backgrounds_Abell370_20190830.fits'
bg_table = pyfits.getdata(bg_file)
imgr_data['background'] = [bg_table['wavelength'],bg_table['background']] # wavelength in micron, SB in MJy/sr

# SCENE: Object magnitude
imgr_data['scene'][0]['spectrum']['normalization']['norm_flux'] = 28.1
imgr_data['scene'][0]['spectrum']['normalization']['norm_fluxunit'] = 'abmag'

# PHOTOMETRIC APERTURE FOR DETECTION
imgr_data['strategy']['aperture_size'] = 0.08  # radius (default 0.1")
imgr_data['strategy']['sky_annulus'] = 0.6, 0.99  # (default 0.22" - 0.4")

# OBSERVATIONS: FILTER
filt = 'f200w'
ch = 'sw'  # Short Wavelength Channel
imgr_data['configuration']['instrument']['filter'] = filt
imgr_data['configuration']['instrument']['aperture'] = ch
imgr_data['configuration']['instrument']['mode'] = ch+'_imaging'

# OBSERVATIONS: Detector Readout (Exposure Time)
imgr_data['configuration']['detector']['readmode'] = readmode = 'deep8'
imgr_data['configuration']['detector']['ngroup'] = ngroup = 5
imgr_data['configuration']['detector']['nint'] = nint = 1
imgr_data['configuration']['detector']['nexp'] = nexp = 6  # dithers

# RUN ETC
results = perform_calculation(imgr_data)

# RESULTS: SUMMARY
exptime = results['scalar']['exposure_time']
snr = results['scalar']['sn']
line = '%s  %s  %2d    %2d   %2d  %8.2f  %7.2f' % (filt, readmode.ljust(8), ngroup, nint, nexp, exptime, snr)
print 'filter pattern ngroup nint nexp  exptime     snr'
print line 
# f200w  deep8      5     1    6   5735.16    14.87

# RESULTS: ALL
keys = results['scalar'].keys()
keys.sort()
for key in keys:
    print key.ljust(20), results['scalar'][key]
