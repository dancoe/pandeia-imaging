# pandeia-imaging
Python wrapper for the JWST Pandeia Exposure Time Calculator (ETC): NIRCam Imaging

JWST ETC online GUI:
https://jwst.etc.stsci.edu

For installation instructions and more, see:
https://github.com/kvangorkom/pandeia-coronagraphy

My quick start guide to installing AstroConda:
1. http://astroconda.readthedocs.io/en/latest/getting_started.html
1. Download `Miniconda2-latest-MacOSX-x86_64.sh` (or a different variant if desired) from https://conda.io/miniconda.html
(Note the ETC Pandeia engine currently works with Python 2.7, not 3.x.)
1. `bash Miniconda2-latest-MacOSX-x86_64.sh`
1. Open a new terminal
1. If running tcsh, run: `bash -l`
1. `conda install anaconda-client`
1. `conda config --add channels http://ssb.stsci.edu/astroconda`
1. `conda create -n astroconda stsci`
1. `source activate astroconda`
1. `conda install stsci`
