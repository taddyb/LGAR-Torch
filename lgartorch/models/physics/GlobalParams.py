from omegaconf import DictConfig
import logging
import numpy as np
import torch
from torch import Tensor

log = logging.getLogger("models.physics.GlobalParams")


class GlobalParams:
    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()

        # Defining all of the variables required by LGAR
        self.layer_thickness_cm = None
        self.cum_layer_thickness = None
        self.num_layers = None
        self.soil_depth_cm = None
        self.initial_psi = None
        self.ponded_depth_max_cm = None
        self.layer_soil_type = None
        self.num_soil_types = None
        self.wilting_point_psi_cm = None
        self.giuh_ordinates = None
        self.num_giuh_ordinates = None

        self.timestep_h = None
        self.endtime_s = None
        self.forcing_resolution_h = None

        self.soils_df = None
        self.soil_temperature = None
        self.soil_temperature_z = None
        self.num_cells_z = None
        self.forcing_interval = None
        self.frozen_factor = None

        self.ponded_depth_cm = None
        self.nint = None
        self.num_wetting_fronts = None
        self.time_s = None
        self.timesteps = None
        self.shape = None
        self.volprecip_cm = None
        self.volin_cm = None
        self.volend_cm = None
        self.volAET_cm = None
        self.volrech_cm = None
        self.volrunoff_cm = None
        self.volrunoff_giuh_cm = None
        self.volQ_cm = None
        self.volon_cm = None
        self.volprecip_cm = None
        self.volon_timestep_cm = None
        self.precip_previous_timestep_cm = None
        self.volQ_cm = None

        self.soil_depth_wetting_fronts = None
        self.soil_moisture_wetting_fronts = None
        self.precipitation_mm_per_h = None
        self.PET_mm_per_h = None

        # Setting these options to false (default)
        self.sft_coupled = False
        self.use_closed_form_G = False

        self.initialize_config_parameters(cfg)

    def initialize_config_parameters(self, cfg: DictConfig) -> None:
        """
        Reading variables from the config file specific to each testcase
        :param cfg: The config file
        :return: None

        Here are a list of the variables created:
        - layer_thickness_cm: the thickness of each soil layer
        - cum_layer_thickness: A list of the cumulative depth as we traverse through the soil layers
        - num_layers: The number of soil layers
        - soil_depth_cm
        - initial_psi
        - ponded_depth_max_cm
        - layer_soil_type
        - num_soil_types
        - wilting_point_psi_cm
        - layer_thickness_cm
        - giuh_ordinates
        - num_giuh_ordinates
        """
        self.layer_thickness_cm = torch.tensor(
            cfg.data.layer_thickness, device=cfg.device
        )
        self.cum_layer_thickness = torch.zeros(
            [len(cfg.data.layer_thickness)], device=cfg.device
        )
        self.cum_layer_thickness[0] = self.layer_thickness_cm[0]
        for i in range(1, self.cum_layer_thickness.shape[0]):
            self.cum_layer_thickness[i] = (
                    self.cum_layer_thickness[i - 1].clone() + self.layer_thickness_cm[i]
            )
        self.num_layers = len(cfg.data.layer_thickness)
        self.soil_depth_cm = self.cum_layer_thickness[-1]

        self.initial_psi = torch.tensor(cfg.data.initial_psi, device=cfg.device)
        self.ponded_depth_max_cm = torch.max(
            torch.tensor(cfg.data.ponded_depth_max, device=cfg.device)
        )

        self.use_closed_form_G = cfg.data.use_closed_form_G

        # HARDCODING A 1 SINCE PYTHON is 0-BASED FOR LISTS AND C IS 1-BASED
        self.layer_soil_type = np.array(cfg.data.layer_soil_type) - 1

        self.num_soil_types = torch.tensor(cfg.data.max_soil_types, device=cfg.device)

        self.wilting_point_psi_cm = torch.tensor(
            cfg.data.wilting_point_psi, device=cfg.device
        )

        self.giuh_ordinates = np.array(cfg.data.giuh_ordinates)