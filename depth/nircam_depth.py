# NIRCam imaging 5-sigma depth vs. exposure time
# using the Pandeia JWST Exposure Time Calculator (ETC) python engine
# short wavelength channel: 0.08" diameter aperture; 0.6" - 0.99" diameter sky background annuli
# long  wavelength channel: 0.16" diameter aperture; 1.2" - 1.98" diameter sky background annuli
# Dan Coe 6/18/17

"""
STScI network
bash -l
source activate astroconda2
export PYSYN_CDBS=/eng/ssb/pyetc/cdbs_trees/cdbs.23.1.rc3
export pandeia_refdata=/Users/dcoe/JWST/ETC/pandeia/bugfix/workdir/pandeia/refdata
python nircam_depth_all.py
"""

import numpy as np  

# Create ladder of exposure times using recommended readout patterns and numbers of groups

#readmodes = 'rapid bright1 bright2 shallow2 shallow4 medium2 medium8 deep2 deep8'.split()
readmodes = 'bright1 shallow4 medium8 deep8'.split()  # bright2 ngroups > 4 not allowed

readpats = []
for readmode in readmodes:
    if 'bright' in readmode:
        ngroups = np.arange(5,11)  # NGROUPS = 1 doesn't work
    elif 'shallow' in readmode:
        ngroups = np.arange(5,11)  # NGROUPS = 1 doesn't work
    elif 'medium' in readmode:
        ngroups = np.arange(6,11)  # pick up where the last group left off
    elif 'deep' in readmode:
        ngroups = np.arange(6,21)  # pick up where the last group left off
    for ngroup in ngroups:
        readpat = readmode + ' %d' % ngroup
        readpats.append(readpat)
        #print readpat

# Import relevant libraries
from pandeia.engine.perform_calculation import perform_calculation
import json
import matplotlib.pyplot as plt
import astropy.io.fits as pyfits
import os

bg_file = '/Users/dcoe/JWST/ETC/pandeia/pandeia/backgrounds/minzodi12_12052016.fits'
#bg_file = '/Users/dcoe/JWST/ETC/pandeia/bugfix/backgrounds/macs0416_191130.fits'
#bg_file = 'backgrounds_Abell370_20190830.fits'

bg_table = pyfits.getdata(bg_file)
background = [bg_table['wavelength'],bg_table['background']] # wavelength in micron, SB in MJy/sr

jsonfile = 'nircam_imaging.json'  
with open(jsonfile) as f:
    imgr_data = json.load(f)

# Test
#results = perform_calculation(imgr_data)

######
# Edit parameters and try one calculation

imgr_data['scene'][0]['spectrum']['normalization']['norm_flux'] = mag = 29
imgr_data['scene'][0]['spectrum']['normalization']['norm_fluxunit'] = 'abmag'
imgr_data['configuration']['detector']['nexp'] = nexp = 4
imgr_data['configuration']['detector']['nint'] = nint = 1
imgr_data['configuration']['detector']['ngroup'] = ngroup = 5
imgr_data['configuration']['detector']['readmode'] = readmode = 'bright1'
imgr_data['configuration']['instrument']['filter'] = filt = 'f200w'
imgr_data['background'] = background

ch = 'sw'
imgr_data['configuration']['instrument']['aperture'] = ch
imgr_data['configuration']['instrument']['mode'] = ch+'_imaging'
imgr_data['strategy']['aperture_size'] = 0.08  # radius (default 0.1")
imgr_data['strategy']['sky_annulus'] = 0.6, 0.99  # (default 0.22" - 0.4")

results = perform_calculation(imgr_data)
exptime = results['scalar']['exposure_time']

line = readmode.ljust(10)
snr = results['scalar']['sn']
line += '%2d  %2d  %2d  %7.2f  %12.8f' % (ngroup, nint, nexp, exptime, snr)
print line
print "Initial test complete..."
print

######

outdir = 'results'
if not os.path.exists(outdir):
    os.mkdir(outdir)

filts = 'f090w f115w f150w f200w f277w f356w f410m f444w'.split()
for filt in filts:
    print filt
    lam = int(filt[1:4])
    if lam < 240:
        ch = 'sw'
        imgr_data['strategy']['aperture_size'] = 0.08  # radius (default 0.1")
        imgr_data['strategy']['sky_annulus'] = 0.6, 0.99  # (default 0.22" - 0.4")
    else:
        ch = 'lw'
        imgr_data['strategy']['aperture_size'] = 0.16  # radius (default 0.1")
        imgr_data['strategy']['sky_annulus'] = 1.2, 1.98  # (default 0.22" - 0.4")

    imgr_data['configuration']['instrument']['aperture'] = ch
    imgr_data['configuration']['instrument']['mode'] = ch+'_imaging'

    imgr_data['configuration']['instrument']['filter'] = filt

    ireadpat = 0

    mags = np.arange(25.9,31,0.2) + 0.1
    for mag in mags:
        print filt, 'mag', mag
        nexp = 4
        imgr_data['scene'][0]['spectrum']['normalization']['norm_flux'] = mag
        imgr_data['configuration']['detector']['nexp'] = nexp
    
        outfile = outdir + '/etc_snr_%dexp_%s_mag%5.2f.txt' % (nexp, filt, mag)
        if os.path.exists(outfile):
            print outfile, 'EXISTS.  SKIPPING...'
            continue
        
        fout = open(outfile, 'w')
        snr = 0
        ireadpat1 = ireadpat
        while snr < 5:
            readpat = readpats[ireadpat]
            #print filt, readpat
            readmode, ngroup = readpat.split()
            ngroup = int(ngroup)
            imgr_data['configuration']['detector']['ngroup'] = ngroup
            imgr_data['configuration']['detector']['readmode'] = readmode
            results = perform_calculation(imgr_data)
            exptime = results['scalar']['exposure_time']
            snr = results['scalar']['sn']
            line = readmode.ljust(10)
            line += '%2d  %2d  %2d  %7.2f  %12.8f' % (ngroup, nint, nexp, exptime, snr)
            print line
            if snr > 5:
                if ireadpat:
                    if ireadpat == ireadpat1:
                        # If SNR > 5 on the first attempt, then go back to previous shallower pattern
                        print 'Going back one...'
                        readpat = readpats[ireadpat-1]
                        readmode, ngroup = readpat.split()
                        ngroup = int(ngroup)
                        imgr_data['configuration']['detector']['ngroup'] = ngroup
                        imgr_data['configuration']['detector']['readmode'] = readmode
                        results1 = perform_calculation(imgr_data)
                        exptime1 = results1['scalar']['exposure_time']
                        snr1 = results1['scalar']['sn']
                        line1 = readmode.ljust(10)
                        line1 += '%2d  %2d  %2d  %7.2f  %12.8f' % (ngroup, nint, nexp, exptime1, snr1)
                        print line1
                        fout.write(line1+'\n')
                    
            fout.write(line+'\n')
            #print readmode, ngroup, exptime, snr
            if snr < 5:
                ireadpat += 1
                
            if ireadpat == len(readpats):
                break  # final read pattern didn't yield snr > 5

        fout.close()
        print outfile
        print
        
        if ireadpat == len(readpats):
            break  # mag loop; can't go fainter; final read pattern didn't yield snr > 5
        

