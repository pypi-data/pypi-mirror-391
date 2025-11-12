import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from astropy.visualization import (
    AsinhStretch, AsymmetricPercentileInterval,
    ImageNormalize,
)

from ..utils.file_handler import GalaxyImageSet
from ..utils.utility import useful_functions


plt.rcParams["font.family"] = "FreeSerif"

plt.rcParams['axes.labelsize'] = 7
plt.rcParams['xtick.labelsize'] = 7
plt.rcParams['ytick.labelsize'] = 7


class DrawGalaxy:
    def __init__(self):
        pass
    
    @classmethod
    def plot_galaxy(cls, image_set: GalaxyImageSet, galaxy: str, step: str):
        image_dict = {}
        
        galaxy_data = image_set.data[galaxy]
        
        for obs, obs_dict in galaxy_data.items():
            for band, band_im in obs_dict.items():
                image_dict[f"{obs}.{band}"] = band_im
        
             
        m, n = useful_functions.find_rec(len(image_dict))
        
        fig, axes = plt.subplots(m, n, dpi=200, figsize=(n * 1.5, m * 1.2))
        
        for ax, im_data in zip(axes.flatten(), image_dict.items()):
            
            norm = ImageNormalize(im_data[1], interval=AsymmetricPercentileInterval(50., 99.8), stretch=AsinhStretch())
            
            im = ax.imshow(im_data[1], cmap='gray', origin="lower", norm=norm)
            
            ax.tick_params(axis="both", which="both", direction="in")
            ax.tick_params(axis="both", which="major", width=1.2)
            
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical')
            
        for ax in axes.flatten()[len(image_dict):]:
            ax.remove()
        
        fig.suptitle(f"Step Name: {step}")
        fig.tight_layout()
        plt.show()
            