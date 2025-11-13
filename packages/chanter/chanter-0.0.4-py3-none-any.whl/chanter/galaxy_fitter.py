import numpy as np
from nautilus import Sampler
from .model_galaxy import modelgalaxy
from .utils import filter_set
import time


class galaxyfitter(object):

    # Generative function for the likelihood (calls model galaxy)
    def gen_phot(self, fit_instruc, filt_files):
        """ Linear function.

        Parameters
        ----------
        
        par : numpy.ndarray
            Free parameters.
        """
        model = modelgalaxy(fit_instruc)
        wavs, flux = model.get_spectrum()
        effwavs, phot = model.get_photometry(wavs, flux, filt_files)

        return phot

    # Liklihood function for a certain point in parameter space
    def log_likelihood(self, data, gen_func, filt_files, param_dict):
        """ Return the natural logarithm of the Likelihood. Constructed from a single gaussian.

        Parameters
        ----------

        data :  numpy.ndarray
            Dataset containing x, y and y_uncert values arranged in 3 rows.

        gen_func : function
            Generative function used to model the data.

        params : numpy.ndarray
            Free parameters of the generative model.
        """

        # Given Data
        yi, yisig = data[0], data[1]

        exp = {}
        exp["age"] = param_dict["age"]
        exp["tau"] = param_dict["tau"]
        exp["massformed"] = param_dict["massformed"]
        #exp["metallicity"] = param_dict["metallicity"]        # Z/Z_oldsolar
        dust = {}
        dust["type"] = "Calzetti"
        dust["Av"] = param_dict["Av"]
        fit_instruc = {}
        fit_instruc["redshift"] = param_dict["redshift"]
        fit_instruc["exponential"] = exp   
        fit_instruc["dust"] = dust


        # Likelihood of belonging to the 'good' gaussian
        log_li = np.log((1/(np.sqrt(2*np.pi*(yisig**2))))) + ((-(yi - gen_func(fit_instruc, filt_files))**2) / (2*(yisig**2)))

        # Sum likelihood and take logarithm (note sometimes recieve underflow error due to small likelihoods)
        log_l_total = np.sum(log_li)
        
        return(log_l_total)

    # Fit an array of photometry, output the best galaxy parameters
    def fit(self, photdata, prior, filt_files):

        filt = filter_set(filt_files)
        effwavs = filt.eff_wavs

        # Run fitter
        t0 = time.time()

        # Load data
        dat= photdata.T
        dat[0] = 2.99792458E-05 * ((1e-6 * dat[0]) / ((effwavs)**2))
        dat[1] = 2.99792458E-05 * ((1e-6 * dat[1]) / ((effwavs)**2))

        # Run the nested sampler over the likelihood function
        sampler = Sampler(prior, lambda param_dict: self.log_likelihood(dat, self.gen_phot, filt_files, param_dict), n_live=1000)
        success = sampler.run(verbose=True, discard_exploration=True, timeout=1800)

        # Plot results
        points, log_w, log_l = sampler.posterior()

        dic = {}
        # Plot bestfit
        for i in range(len(prior.keys)):
            key = prior.keys[i]
            points_i = points.T[i]
            samples = np.random.choice(points_i, size = points_i.shape[0], p=np.exp(log_w))
            dic[key + "_50"] = np.percentile(samples, 50)

        exp = {}
        exp["age"] = dic['age_50']
        exp["tau"] = dic['tau_50']
        exp["massformed"] = dic['massformed_50']
        dust = {}
        dust["type"] = "Calzetti"
        dust["Av"] = dic['Av_50']
        fit_instructions = {}
        fit_instructions["redshift"] = dic['redshift_50']
        fit_instructions["exponential"] = exp   
        fit_instructions["dust"] = dust

        print('Finished in ' + str(time.time() - t0)+ ' seconds.')
        print(' ')

        return fit_instructions






