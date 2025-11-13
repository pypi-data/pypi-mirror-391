import numpy as np
import matplotlib.pyplot as plt
from astropy.cosmology import Planck13  # Planck 2013
from astropy.io import fits
from spectres import spectres
from .utils import filter_set
import os


# Load SSPs and resample
def resample_ssp_wavs(target_wavs):

    grid_raw_ages = np.zeros((master_base.shape[0], master_base.shape[1], target_wavs.shape[0]+1))
    grid_raw_ages[:, :, 0] = master_base[:, :, 0]
    grid_raw_ages[:, 0, 1:] = target_wavs

    old_wavs = master_base[0][0][1:]

    for i in range(master_base.shape[0]):
        for j in range(1, master_base.shape[1]):
            
            old_flux = master_base[i][j][1:]
            new_wavs = target_wavs
            new_flux = spectres(new_wavs, old_wavs, old_flux, fill=0)
            grid_raw_ages[i, j, 1:] = new_flux

    grid_raw_ages[0].T[0, 1:] = grid_raw_ages[0].T[0, 1:] / 1e9

    return grid_raw_ages

def resample_igm_grid(wavs):
    # Import IGM grid
    raw_igm_grid = fits.open(os.path.dirname(os.path.realpath(__file__)) + '/grids/d_igm_grid_inoue14.fits')[1].data
    igm_wavelengths = np.arange(1.0, 1225.01, 1.0)

    # Resample in wavelength
    grid = np.zeros((raw_igm_grid.shape[0], wavs.shape[0]))

    for i in range(raw_igm_grid.shape[0]):
        
        old_wavs = igm_wavelengths
        old_trans = raw_igm_grid[i]
        new_wavs = wavs
        new_trans = spectres(new_wavs, old_wavs, old_trans)
        grid[i] = new_trans
    
    return grid


hdul = fits.open(os.path.dirname(os.path.realpath(__file__)) + '/grids/ssps.fits')
master_base = np.array((hdul[1].data, hdul[2].data, hdul[3].data, hdul[4].data, hdul[5].data, hdul[6].data, hdul[7].data))

rest_target_wavs = np.arange(100., 50000., 25.)
grid = resample_ssp_wavs(rest_target_wavs)
igm_grid = resample_igm_grid(rest_target_wavs)


'''
# !!AGE RESAMPLING NOT WORKING!!

def resample_ssp_ages(grid_raw_ages, target_ages):

    grid = np.zeros((grid_raw_ages.shape[0], target_ages.shape[0]+1, grid_raw_ages.shape[2]))
    grid[:, 0, :] = grid_raw_ages[0, 0, :]
    grid[:, 1:, 0] = target_ages

    old_ages = grid_raw_ages[0].T[0, 1:] / 1e9

    for i in range(grid_raw_ages.shape[0]):
        for j in range(1, grid_raw_ages.shape[2]):

            old_age_flux = grid_raw_ages[i].T[j, 1:]
            new_ages = target_ages
            new_age_flux = spectres(new_ages, old_ages, old_age_flux, fill=0)
            grid[i].T[j, 1:] = new_age_flux

    return grid

num_agebins = 100
target_ages = np.linspace(0, Planck13.age(0).value, num_agebins)
grid = resample_ssp_ages(grid_resampled, target_ages)
'''



class modelgalaxy(object):
    

    def __init__(self, fit_instructions):
        self.fit_instructions = fit_instructions
        self.universe_age = Planck13.age(0).value
        self.lookback_time = Planck13.lookback_time(self.fit_instructions["redshift"]).value

    
    def sfr(self, age, ageform, tau, massformed):
        
        # Create exp time
        t = ageform - age
        sfr = np.exp(-t/ tau)
        # Enforce no SF before ageform
        sfr[t<0]=0
        # Normalise to massformed
        tdiff = np.diff(age)
        area = np.sum(tdiff * sfr[:-1])
        if area!=0:
            sfr = sfr * ((10**massformed) / area)
        else:
            sfr  = sfr * 0

        if ageform + self.lookback_time > self.universe_age:
            sfr *= 0
            
        return sfr


    def calzetti_dust(self, wavs):
        """ Calculate the ratio A(lambda)/A(V) for the Calzetti et al.
        (2000) attenuation curve. """

        A_lambda = np.zeros_like(wavs)

        wavs_mic = wavs*10**-4

        mask1 = (wavs < 1200.)
        mask2 = (wavs < 6300.) & (wavs >= 1200.)
        mask3 = (wavs < 31000.) & (wavs >= 6300.)

        A_lambda[mask1] = ((wavs_mic[mask1]/0.12)**-0.77
                           * (4.05 + 2.695*(- 2.156 + 1.509/0.12
                                            - 0.198/0.12**2 + 0.011/0.12**3)))

        A_lambda[mask2] = (4.05 + 2.695*(- 2.156
                                         + 1.509/wavs_mic[mask2]
                                         - 0.198/wavs_mic[mask2]**2
                                         + 0.011/wavs_mic[mask2]**3))

        A_lambda[mask3] = 2.659*(-1.857 + 1.040/wavs_mic[mask3]) + 4.05

        A_lambda /= 4.05

        return A_lambda
    

    def transmission_neutral(self, wavs):
        trans = 10**(-self.fit_instructions["dust"]["Av"]*self.calzetti_dust(wavs) / 2.5)
        return trans
    
    def transmission_igm(self, redshift):

        max_redshift=10.
        igm_redshifts = np.arange(0.0, max_redshift + 0.01, 0.01)

        """ Get the IGM transmission at a given redshift. """

        redshift_mask = (igm_redshifts < redshift)
        zred_ind = igm_redshifts[redshift_mask].shape[0]

        zred_fact = ((redshift - igm_redshifts[zred_ind-1])
                     / (igm_redshifts[zred_ind]
                        - igm_redshifts[zred_ind-1]))

        if zred_ind == 0:
            zred_ind += 1
            zred_fact = 0.

        weights = np.array([[1. - zred_fact, zred_fact]])

        igm_trans = np.sum(weights.T*igm_grid[zred_ind-1:zred_ind+1], axis=0)

        igm_trans[np.isnan(igm_trans)] = 1.

        return igm_trans


    def redshift_effects(self, wavs, lum):

        obswavs = (1+self.fit_instructions["redshift"]) * wavs
        lum_distance = Planck13.luminosity_distance(self.fit_instructions["redshift"]).value
        lum = 3.826e33 * lum # change luminosity units to erg/s
        lum_distance = lum_distance * 1e6 * 3.086e16 * 100 # change distance units to cm
        flux = lum / (4 * np.pi * (1+self.fit_instructions["redshift"]) * (lum_distance**2)) # * IGM transmission function
        return obswavs, flux


    def get_spectrum(self):

        # Get model spectra, use a single population
        ssp_age = grid[0].T[0, 1:]
        wavs = grid[0, 0, 1:]
        fluxes = grid[4, 1:, 1:]

        
        agebinwidths = np.diff(ssp_age)
        sfrs = self.sfr(ssp_age[1:], self.fit_instructions["exponential"]["age"], self.fit_instructions["exponential"]["tau"], self.fit_instructions["exponential"]["massformed"])
        ssps = fluxes[1:]
        trans_neutral = self.transmission_neutral(wavs)
        trans_igm = self.transmission_igm(self.fit_instructions["redshift"])

        # Find the total product
        lums = (np.array(([(agebinwidths * sfrs)])).T * ssps) * trans_neutral
        lumtot = np.sum(lums, axis=0)

        lumtot *= trans_igm

        # Add in the effects of ISM dust attenuation (calzetti)
        obswavs, obsflux = self.redshift_effects(wavs, lumtot)

        self.wavs = obswavs
        self.flux = obsflux

        return obswavs, obsflux
    

    def get_photometry(self, wavs, flux, filt_list):
        filt = filter_set(filt_list)
        filt.resample_filter_curves(wavs)
        effwavs = filt.eff_wavs
        phot = filt.get_photometry(flux, 0)
        return effwavs, phot
    

    def plot_spec(self, ax, kwargs):

        #effwavs, phot = self.get_photometry(self.wavs, self.flux)

        self.get_spectrum()

        ax.plot(self.wavs, self.flux, **kwargs)
        ax.set_ylabel('Observed Flux / erg s$^{-1}$ cm$^{-2}$ Å$^{-1}$')
        ax.set_xlabel('Observed Wavelength / Å')
    

    
    def plot_sfh(self, ax):
        ssp_age = grid[0].T[0, 1:]        
        sfrs = self.sfr(ssp_age, self.fit_instructions["exponential"]["age"], self.fit_instructions["exponential"]["tau"], self.fit_instructions["exponential"]["massformed"])

        ax.set_xlabel('Age / Gyr')
        ax.set_ylabel(' Star Formation / M$_{sun}$ Gyr$^{-1}$')
        ax.plot((self.universe_age-self.lookback_time) - ssp_age, sfrs/1e9, color='black', lw=1)
        ax.axvline((self.universe_age-self.lookback_time) - ssp_age[0], 0, 1, color='black', ls='dashed', lw=1)

        #ax.plot(-ssp_age, sfrs/1e9, color='black')
        ax.invert_xaxis()
        ax.set_xlim(self.universe_age,0)
        ax.set_ylim(0, )
    














