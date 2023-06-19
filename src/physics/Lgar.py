#####################################################################################
# Python Author: Tadd Bindas
# C authors : Ahmad Jan, Fred Ogden, and Peter La Follette
# year    : 2022
# email   : tkb5476@psu.edu
# - The file contains lgar subroutines
#####################################################################################

"""
LL          GGG
LL        GGG GGG       AAA  A    RR   RRRR
LL       GG    GGG    AAA AAAA     RR RR  RR
LL       GG     GG   AA     AA     RRR
LL      GGG    GGG  AAA     AA     RR
LL       GG  GG GG   AA     AAA    RR
LL        GGGG  GG    AAA  AA A    RR
LL              GG      AAAA   AA  RR
LL              GG
LLLLLLLL  GG   GG
             GGGG

The lgar specific functions based on soil physics

SKETCH SHOWING 3 SOIL LAYERS AND 4 WETTING FRONTS

theta_r                                  theta1             theta_e
  --------------------------------------------------------------   --depth_cm = 0    -------> theta
  r                                        f                   e
  r                                        f                   e
  r                                --------1                   e   --depth_cm(f1)
  r                               f         \                  e
  r     1st soil layer            f          \                 e
  r                               f wetting front number       e
  r                               f /                          e
  r                               f/                           e
  --------------------------------2-----------------------------  -- depth_cm(f2)
     r                                      f              e
     r     2nd soil layer                   f              e
     r                                      f              e
|      ---------------------------------------3---------------      -- depth_cm(f3)
|        r                                          f     e
|        r                                          f     e
|        r       3rd  soil layer                    f     e
|        r                                          f     e
V        -------------------------------------------4------         -- depth_cm(f4)
depth

############################################################################################
@param soil_moisture_wetting_fronts  : 1D array of thetas (soil moisture content) per wetting front;
                                       output to other models (e.g. soil freeze-thaw)
@param soil_depth_wetting_fronts : 1D array of absolute depths of the wetting fronts [meters];
				   output to other models (e.g. soil freeze-thaw)
############################################################################################
"""
import logging
from omegaconf import DictConfig
import torch

log = logging.getLogger("physics.Lgar")


class LGAR:
    def __init__(self, cfg: DictConfig) -> None:
        log.debug(
            "------------- Initialization from config file ----------------------"
        )

        # Setting these options to false (default)
        self.sft_coupled = False
        self.use_closed_form_G = False

        # Setting the parameter check variables to False
        is_layer_thickness_set = False
        is_initial_psi_set = False
        is_timestep_set = False
        is_endtime_set = False
        is_forcing_resolution_set = False
        is_layer_soil_type_set = False
        is_wilting_point_psi_cm_set = False
        is_soil_params_file_set = False
        is_max_soil_types_set = False
        is_giuh_ordinates_set = False
        is_soil_z_set = False
        is_ponded_depth_max_cm_set = False

        # Setting soil parameters based on the cfg file
        self.layer_thickness_cm = torch.zeros([len(cfg.data.layer_thickness) + 1])
        self.layer_thickness_cm[1:] = torch.tensor(cfg.data.layer_thickness)
        self.cum_layer_thickness = torch.zeros([len(cfg.data.layer_thickness) + 1])
        for i in range(1, self.cum_layer_thickness.shape[0]):
            self.cum_layer_thickness[i] = (
                self.cum_layer_thickness[i - 1].clone() + self.layer_thickness_cm[i]
            )
        self.num_layers = self.layer_thickness_cm.shape[0]
        self.soil_depth_cm = self.cum_layer_thickness[-1]
        is_layer_thickness_set = True

        log.debug(f"Number of Layers: {self.num_layers}")
        [log.debug(f"Thickness, cum. depth {x.item()}") for x in self.cum_layer_thickness]

        self.initial_psi = cfg.data.initial_psi
        is_initial_psi_set = True

        unit = cfg.data.timestep_unit
        timestep_h = torch.tensor(cfg.data.timestep)
        if unit in ["[s]", "[sec]", ""]:  # default time unit is seconds
            self.timestep_h = torch.tensor(timestep_h / 3600)  # convert to hours
        elif unit in ["[min]", "[minute]"]:
            self.timestep_h = torch.tensor(timestep_h / 60)  # convert to hours
        elif unit in ["[h]", "[hr]"]:
            self.timestep_h = torch.tensor(timestep_h / 1)  # already in hours

        assert self.timestep_h > 0  # Checking to make sure the time is right
        is_timestep_set = True

        unit = cfg.data.endtime_unit
        if unit in ["[s]", "[sec]", ""]:
            self.endtime_s = torch.tensor(float(cfg.data.timestep))
        elif unit in ["[min]", "[minute]"]:
            self.endtime_s = torch.tensor(float(cfg.data.timestep) * 60.0)
        elif unit in ["[h]", "[hr]"]:
            self.endtime_s = torch.tensor(float(cfg.data.timestep) * 3600.0)
        elif unit in ["[d]", "[day]"]:
            self.endtime_s = torch.tensor(float(cfg.data.timestep) * 86400.0)
        log.debug(f"Config time unit is: {unit}")
        assert self.endtime_s > 0  # Checking to make sure the endtime is actually an endtime
        is_endtime_set = True


        is_forcing_resolution_set = True


        is_layer_soil_type_set = True


        is_wilting_point_psi_cm_set = True


        is_soil_params_file_set = True


        is_max_soil_types_set = True


        is_giuh_ordinates_set = True


        is_soil_z_set = True


        is_ponded_depth_max_cm_set = True



