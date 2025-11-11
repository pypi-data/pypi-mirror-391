# Copyright (c) 2021-2025 Cubillos & Blecic
# Pyrat Bay is open-source software under the GNU GPL-2.0 license (see LICENSE)

__all__ = [
    'fetch_phoenix',
    'read_phoenix',
    ]

import os
import pathlib
import urllib

import numpy as np
import astropy.io.fits as fits

from .. import constants as pc


PHOENIX_WAVE = 'WAVE_PHOENIX-ACES-AGSS-COND-2011.fits'

def fetch_phoenix(metal, teff, logg, folder='.'):
    """
    Fetch the PHOENIX high-resolution stellar model that matches the
    closest to the input metallicity, effective temperature, and log(g).

    Parameters
    ----------
    metal: Float
       Requested stellar metallicity.
    teff: Float
    logg:Float
    folder: String

    Returns
    -------
    phoenix_file: String
    zmodel: Float
    tmodel: Float
    gmodel: Float

    Examples
    --------
    >>> metal = 0.1
    >>> teff = 5700.0
    >>> logg = 4.44
    >>> folder = '../run36_pandexo/'

    >>> metal = 0.1
    >>> teff = 6431.0
    >>> logg = 4.49

    >>> import pyratbay.spectrum.phoenix as phoenix
    >>> model = phoenix.fetch_phoenix(metal, teff, logg, folder=folder)
    """
    root = 'ftp://phoenix.astro.physik.uni-goettingen.de/v2.0/HiResFITS/'
    phoenix_ftp = root + 'PHOENIX-ACES-AGSS-COND-2011'
    phoenix_wave = root + PHOENIX_WAVE

    phoenix_Z = np.array(
        [-4.0, -3.0, -2.0, -1.5, -1.0, -0.5, -0.0, 0.5, 1.0])
    imetal = np.argmin(np.abs(phoenix_Z-metal))
    zmodel = f'Z{phoenix_Z[imetal]:+}'

    resp = urllib.request.urlopen(f'{phoenix_ftp}/{zmodel}/')
    models = np.array([
        content for content in resp.read().decode('utf-8').split()
        if content.startswith('lte')])

    # Match closest temperature first:
    temps = np.array([int(model[3:8]) for model in models])
    tmodel = temps[np.argmin(np.abs(temps-teff))]
    models = models[temps == tmodel]

    loggs = np.array([float(model[9:13]) for model in models])
    imodel = np.argmin(np.abs(loggs-logg))
    gmodel = loggs[imodel]
    model = models[imodel]

    url = f'{phoenix_ftp}/{zmodel}/{model}'
    phoenix_file = folder + '/' + model.replace('lte', f'lte_{zmodel}_')
    urllib.request.urlretrieve(url, phoenix_file)
    # Now the wavelengths, if necessary:
    wave_file = f'{folder}/{PHOENIX_WAVE}'
    if not os.path.isfile(wave_file):
        urllib.request.urlretrieve(phoenix_wave, wave_file)

    return os.path.abspath(phoenix_file), phoenix_Z[imetal], tmodel, gmodel


def read_phoenix(filename, resolution=5000.0):
    """
    Extract stellar flux models from a Kurucz file.
    Kurucz model files can be found at http://kurucz.harvard.edu/grids.html

    Parameters
    ----------
    filename: String
       Name of a Kurucz model file.
    temp: Float
       Requested surface temperature for the Kurucz model.
       If temp and logg are not None, return the model with the closest
       surface temperature and gravity.
    logg: Float
       Requested log10 of the surface gravity for the Kurucz model
       (where g is in cgs units).

    Returns
    -------
    flux: 1D or 2D float ndarray
       If temp and logg are not None, a 1D array with the kurucz surface
       flux per unit wavenumber (erg s-1 cm-2 cm) of the closest model to
       the input temperature and gravity.
       Else, a 2D array with all kurucz models in file, of shape
       [nmodels, nwave].
    wavenumber: 1D ndarray
       Wavenumber sampling of the flux models (in cm-1 units).
    ktemp: Scalar or 1D float ndarray
       Surface temperature of the output models (in Kelvin degrees).
    klogg: Scalar or 1D float ndarray
       log10 of the stellar surface gravity of the output models (in cm s-2).
    continuum: 2D ndarray
       The models' fluxes with no line absorption.  Same units and
       shape of flux. Returned only if temp and logg are None.

    Examples
    --------
    >>> import pyratbay.spectrum as ps
    >>> import pyratbay.constants as pc
    >>> import numpy as np
    >>> # Download a Kurucz stellar model file from:
    >>> # http://kurucz.harvard.edu/grids/gridp00odfnew/fp00k0odfnew.pck
    >>> # Read a single model from the kurucz file:
    >>> kfile = 'fp00k0odfnew.pck'
    >>> tsun = 5770.0  # Sun's surface temperature
    >>> gsun = 4.44    # Sun's surface gravity (log)
    >>> flux, wn, ktemp, klogg = ps.read_kurucz(kfile, tsun, gsun)
    >>> # Compute brightness at 1 AU from a 1 Rsun radius star:
    >>> s = np.trapezoid(flux, wn) * (pc.rsun/pc.au)**2
    >>> print("Solar constant [T={:.0f} K, logg={:.1f}]:  S = {:.1f} W m-2".
    >>>       format(ktemp, klogg, s * 1e-3))
    Solar constant [T=5750 K, logg=4.5]:  S = 1340.0 W m-2
    >>> # Pretty close to the solar constant: ~1361 W m-2

    >>> # Read the whole set of models in file:
    >>> # (in this case, ktemp and klogg are 1D arrays)
    >>> fluxes, wn, ktemp, klogg, continua = ps.read_kurucz(kfile)

    >>> pfile = 'lte_Z-0.0_05700-4.50-0.0.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits'
    """
    # '/Users/pato/Dropbox/IWF/projects/2014_pyratbay/run36_pandexo/'
    # '/home/pcubillos/Dropbox/IWF/projects/2014_pyratbay/run36_pandexo/'
    PHOENIX_WAVE = 'WAVE_PHOENIX-ACES-AGSS-COND-2011.fits'
    # erg s-1 cm-2 cm-1
    pflux, header = fits.getdata(pfile, header=True)
    dirname = os.path.dirname(os.path.abspath(pfile))
    pwave = fits.getdata(f'{dirname}/{PHOENIX_WAVE}')

    # Convert wavelength to cm
    pwave *= pc.A
    # Convert flux (erg s-1 cm-2 A-1) to (erg s-1 cm-2 cm):
    pflux *= pwave**2


    from scipy.ndimage import gaussian_filter1d as gaussf
    import pysynphot as psyn
    import pyratbay.spectrum as ps

    gauss_pflux = gaussf(pflux,50)

    bb = ps.bbflux(1.0/pwave, model[2])
    plt.figure(2)
    plt.clf()
    plt.plot(pwave/pc.um, gauss_pflux)
    plt.plot(pwave/pc.um, bb)
    #plt.plot(phoenix.wave, phoenix.flux*pc.c/1e23, alpha=0.6)
    plt.xlim(0.1, 6.0)
    plt.xlim(2.0, 6.0)
    plt.ylim(0, 1.5e6)

    plt.figure(2)
    plt.clf()
    wl = np.logspace(-0.5, 0.4, 212027)
    plt.plot(wl, data/np.amax(data)*3.4e19)
    plt.plot(phoenix.wave, phoenix.flux/phoenix.wave**2, alpha=0.6)
    plt.xlim(0.1, 3)

    phoenix = psyn.Icat("phoenix", 5700, 0.0, 4.5)
    phoenix.convert("um")
    phoenix.convert("jy")

    #http://phoenix.astro.physik.uni-goettingen.de/?page_id=15
    #lte04500-4.00-0.0.PHOENIX-ACES-AGSS-COND-2011-HiRes.fits
    psyn600 = psyn.Icat("phoenix", 5600, 0.0, 4.5)
    psyn700 = psyn.Icat("phoenix", 5700, 0.0, 4.5)
    psyn800 = psyn.Icat("phoenix", 5800, 0.0, 4.5)
    psyn600.convert("jy")
    psyn700.convert("jy")
    psyn800.convert("jy")

    sigma = 300.0
    plt.figure(3)
    plt.clf()
    plt.plot(pwave/pc.um, pwave**2*gaussf(pflux600,sigma))
    plt.plot(pwave/pc.um, pwave**2*gaussf(pflux700,sigma), alpha=0.6)
    plt.plot(pwave/pc.um, pwave**2*gaussf(pflux800,sigma), alpha=0.6)
    plt.plot(1e4/wn, flux, 'k')
    plt.xlim(0.5, 3.0)
    plt.plot(phoenix.wave, psyn600.flux*pc.c/1e23, alpha=0.6, c='navy')
    plt.plot(phoenix.wave, psyn700.flux*pc.c/1e23, alpha=0.6, c='r')
    plt.plot(phoenix.wave, psyn800.flux*pc.c/1e23, alpha=0.6, c='g')

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # TBD: What's all this?
    # Read file into memory:
    with open(filename, 'r') as f:
        lines = f.readlines()

    iheaders = [i for i,line in enumerate(lines) if line.startswith('TEFF')]
    headers = [lines[i].strip() for i in iheaders]
    ktemp = np.array([line[ 5:12] for line in headers], np.double)
    klogg = np.array([line[22:29] for line in headers], np.double)

    # Get wavelength array (in nm):
    i = 0
    while lines[i].strip() != 'END':
        i += 1
    wl_start = i + 1
    wl_end = iheaders[0]
    wavelength = np.array(''.join(lines[wl_start:wl_end]).split(), np.double)
    wavenumber = 1.0/(wavelength*pc.nm)
    # Sort by increasing wavenumber:
    wavenumber = np.flip(wavenumber, axis=0)

    nmodels = len(headers)
    nwave   = len(wavenumber)
    nlines = (iheaders[1] - iheaders[0] - 1) // 2
    vsize = 10

    if temp is not None and logg is not None:
        tmodel = ktemp[np.argmin(np.abs(ktemp-temp))]
        gmodel = klogg[np.argmin(np.abs(klogg-logg))]
        imodels = np.where((ktemp == tmodel) & (klogg == gmodel))[0]
    else:
        imodels = range(nmodels)

    # Read intensity per unit frequency (erg s-1 cm-2 Hz-1 ster-1):
    intensity = np.zeros((nmodels, nwave), np.double)
    continuum = np.zeros((nmodels, nwave), np.double)
    for k,i in enumerate(imodels):
        istart = iheaders[i] + 1
        data = ''.join(lines[istart:istart+nlines]).replace('\n','')
        intensity[k] = [data[j*vsize:(j+1)*vsize] for j in range(nwave)]

        data = ''.join(lines[istart+nlines:istart+2*nlines]).replace('\n','')
        continuum[k] = [data[j*vsize:(j+1)*vsize] for j in range(nwave)]

    # Convert intensity per unit frequency to surface flux per unit
    # wavenumber (erg s-1 cm-2 cm):
    flux = np.flip(intensity, axis=1) * 4.0*np.pi * pc.c
    continuum = np.flip(continuum, axis=1) * 4.0*np.pi * pc.c

    if temp is not None and logg is not None:
        return flux[0], wavenumber, tmodel, gmodel

    return flux, wavenumber, ktemp, klogg, continuum
