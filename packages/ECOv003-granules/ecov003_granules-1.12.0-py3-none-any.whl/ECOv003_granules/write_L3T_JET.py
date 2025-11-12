from os.path import exists, basename
from datetime import datetime
import numpy as np
import rasters as rt
import logging

import shutil

import colored_logging as cl

from rasters import Raster

from .constants import L3T_JET_SHORT_NAME, L3T_JET_LONG_NAME
from .colors import ET_COLORMAP, WATER_COLORMAP, CLOUD_COLORMAP
from .L3TJET import L3TJET

logger = logging.getLogger(__name__)

def write_L3T_JET(
            L3T_JET_zip_filename: str,
            L3T_JET_browse_filename: str,
            L3T_JET_directory: str,
            orbit: int,
            scene: int,
            tile: str,
            time_UTC: datetime,
            build: str,
            product_counter: int,
            LE_instantaneous_PTJPLSM_Wm2: Raster,
            ET_daylight_PTJPLSM_kg: Raster,
            LE_instantaneous_STICJPL_Wm2: Raster,
            ET_daylight_STICJPL_kg: Raster,
            LE_instantaneous_BESSJPL_Wm2: Raster,
            ET_daylight_BESSJPL_kg: Raster,
            LE_instantaneous_PMJPL_Wm2: Raster,
            ET_daylight_PMJPL_kg: Raster,
            ET_daylight_kg: Raster,
            ET_daylight_uncertainty_kg: Raster,
            LE_canopy_fraction_PTJPLSM: Raster,
            LE_canopy_fraction_STIC: Raster,
            LE_soil_fraction_PTJPLSM: Raster,
            LE_interception_fraction_PTJPLSM: Raster,
            water_mask: Raster,
            cloud_mask: Raster,
            metadata: dict):
        L3T_JET_granule = L3TJET(
            product_location=L3T_JET_directory,
            orbit=orbit,
            scene=scene,
            tile=tile,
            time_UTC=time_UTC,
            build=build,
            process_count=product_counter
        )

        LE_instantaneous_PTJPLSM_Wm2.nodata = np.nan
        LE_instantaneous_PTJPLSM_Wm2 = rt.where(water_mask, np.nan, LE_instantaneous_PTJPLSM_Wm2)
        LE_instantaneous_PTJPLSM_Wm2 = LE_instantaneous_PTJPLSM_Wm2.astype(np.float32)

        ET_daylight_PTJPLSM_kg.nodata = np.nan
        ET_daylight_PTJPLSM_kg = rt.where(water_mask, np.nan, ET_daylight_PTJPLSM_kg)
        ET_daylight_PTJPLSM_kg = ET_daylight_PTJPLSM_kg.astype(np.float32)

        ET_to_LE_scale_factor_PTJPLSM = LE_instantaneous_PTJPLSM_Wm2 / ET_daylight_PTJPLSM_kg
        ET_to_LE_scale_factor_PTJPLSM_mean = np.nanmean(ET_to_LE_scale_factor_PTJPLSM)

        ET_daylight_STICJPL_kg.nodata = np.nan
        ET_daylight_STICJPL_kg = rt.where(water_mask, np.nan, ET_daylight_STICJPL_kg)
        ET_daylight_STICJPL_kg = ET_daylight_STICJPL_kg.astype(np.float32)
        
        ET_to_LE_scale_factor_STICJPL = LE_instantaneous_STICJPL_Wm2 / ET_daylight_STICJPL_kg
        ET_to_LE_scale_factor_STICJPL_mean = np.nanmean(ET_to_LE_scale_factor_STICJPL)

        ET_daylight_BESSJPL_kg.nodata = np.nan
        ET_daylight_BESSJPL_kg = rt.where(water_mask, np.nan, ET_daylight_BESSJPL_kg)
        ET_daylight_BESSJPL_kg = ET_daylight_BESSJPL_kg.astype(np.float32)
        
        ET_to_LE_scale_factor_BESSJPL = LE_instantaneous_BESSJPL_Wm2 / ET_daylight_BESSJPL_kg
        ET_to_LE_scale_factor_BESSJPL_mean = np.nanmean(ET_to_LE_scale_factor_BESSJPL)
        
        ET_daylight_PMJPL_kg.nodata = np.nan
        ET_daylight_PMJPL_kg = rt.where(water_mask, np.nan, ET_daylight_PMJPL_kg)
        ET_daylight_PMJPL_kg = ET_daylight_PMJPL_kg.astype(np.float32)
        
        ET_to_LE_scale_factor_PMJPL = LE_instantaneous_PMJPL_Wm2 / ET_daylight_PMJPL_kg
        ET_to_LE_scale_factor_PMJPL_mean = np.nanmean(ET_to_LE_scale_factor_PMJPL)
        
        ET_daylight_kg.nodata = np.nan
        ET_daylight_kg = ET_daylight_kg.astype(np.float32)
        
        ET_daylight_uncertainty_kg.nodata = np.nan
        ET_daylight_uncertainty_kg = rt.where(water_mask, np.nan, ET_daylight_uncertainty_kg)
        ET_daylight_uncertainty_kg = ET_daylight_uncertainty_kg.astype(np.float32)
        
        LE_canopy_fraction_PTJPLSM.nodata = np.nan
        LE_canopy_fraction_PTJPLSM = rt.where(water_mask, np.nan, LE_canopy_fraction_PTJPLSM)
        LE_canopy_fraction_PTJPLSM = LE_canopy_fraction_PTJPLSM.astype(np.float32)
        
        LE_canopy_fraction_STIC.nodata = np.nan
        LE_canopy_fraction_STIC = rt.where(water_mask, np.nan, LE_canopy_fraction_STIC)
        LE_canopy_fraction_STIC = LE_canopy_fraction_STIC.astype(np.float32)
        
        LE_soil_fraction_PTJPLSM.nodata = np.nan
        LE_soil_fraction_PTJPLSM = rt.where(water_mask, np.nan, LE_soil_fraction_PTJPLSM)
        LE_soil_fraction_PTJPLSM = LE_soil_fraction_PTJPLSM.astype(np.float32)
        
        LE_interception_fraction_PTJPLSM.nodata = np.nan
        LE_interception_fraction_PTJPLSM = rt.where(water_mask, np.nan, LE_interception_fraction_PTJPLSM)
        LE_interception_fraction_PTJPLSM = LE_interception_fraction_PTJPLSM.astype(np.float32)
        
        water_mask = water_mask.astype(np.uint8)
        cloud_mask = cloud_mask.astype(np.uint8)

        L3T_JET_granule.add_layer("PTJPLSMinst", LE_instantaneous_PTJPLSM_Wm2, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("PTJPLSMdaily", ET_daylight_PTJPLSM_kg, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("STICJPLdaily", ET_daylight_STICJPL_kg, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("BESSJPLdaily", ET_daylight_BESSJPL_kg, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("PMJPLdaily", ET_daylight_PMJPL_kg, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("ETdaily", ET_daylight_kg, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("ETuncertainty", ET_daylight_uncertainty_kg, cmap="jet")
        L3T_JET_granule.add_layer("PTJPLSMcanopy", LE_canopy_fraction_PTJPLSM, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("STICJPLcanopy", LE_canopy_fraction_STIC, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("PTJPLSMsoil", LE_soil_fraction_PTJPLSM, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("PTJPLSMinterception", LE_interception_fraction_PTJPLSM, cmap=ET_COLORMAP)
        L3T_JET_granule.add_layer("water", water_mask, cmap=WATER_COLORMAP)
        L3T_JET_granule.add_layer("cloud", cloud_mask, cmap=CLOUD_COLORMAP)

        percent_good_quality = 100 * (1 - np.count_nonzero(np.isnan(ET_daylight_PTJPLSM_kg)) / ET_daylight_PTJPLSM_kg.size)
        metadata["ProductMetadata"]["QAPercentGoodQuality"] = float(percent_good_quality)
        metadata["ProductMetadata"]["ETtoLEScaleFactorPTJPLSM"] = float(ET_to_LE_scale_factor_PTJPLSM_mean)
        metadata["ProductMetadata"]["ETtoLEScaleFactorSTICJPL"] = float(ET_to_LE_scale_factor_STICJPL_mean)
        metadata["ProductMetadata"]["ETtoLEScaleFactorBESSJPL"] = float(ET_to_LE_scale_factor_BESSJPL_mean)
        metadata["ProductMetadata"]["ETtoLEScaleFactorPMJPL"] = float(ET_to_LE_scale_factor_PMJPL_mean)

        metadata["StandardMetadata"]["BuildID"] = build
        metadata["StandardMetadata"]["LocalGranuleID"] = basename(L3T_JET_zip_filename)
        metadata["StandardMetadata"]["SISName"] = "Level 3/4 JET Product Specification Document"

        short_name = L3T_JET_SHORT_NAME
        logger.info(f"L3T JET short name: {cl.name(short_name)}")
        metadata["StandardMetadata"]["ShortName"] = short_name

        long_name = L3T_JET_LONG_NAME
        logger.info(f"L3T JET long name: {cl.name(long_name)}")
        metadata["StandardMetadata"]["LongName"] = long_name

        metadata["StandardMetadata"]["ProcessingLevelDescription"] = "Level 3 Tiled Evapotranspiration Ensemble"

        L3T_JET_granule.write_metadata(metadata)
        logger.info(f"writing L3T JET product zip: {cl.file(L3T_JET_zip_filename)}")
        L3T_JET_granule.write_zip(L3T_JET_zip_filename)
        logger.info(f"writing L3T JET browse image: {cl.file(L3T_JET_browse_filename)}")
        L3T_JET_granule.write_browse_image(PNG_filename=L3T_JET_browse_filename, cmap=ET_COLORMAP)
        logger.info(f"removing L3T JET tile granule directory: {cl.dir(L3T_JET_directory)}")
        shutil.rmtree(L3T_JET_directory)
