"""
Utility functions for the CLI tool
"""

import datetime
import logging

import numpy as np
import xarray as xr
from scmdata.run import ScmRun

LOGGER = logging.getLogger(__name__)


def tabular_to_netcdf(data_df, meta_df, version="0.0.0"):
    """
    Convert climate model data (CSV + metadata CSV OR Excel) into NetCDF format.

    Structure:
    - Dimensions: ensemble_member, variable, region, time
    - Attributes: model, unit for each variable + metadata

    Parameters
    ----------
    data_df : :obj:`scmdata.ScmRun` or :obj:`pd.DataFrame`
        Submission data.
    meta_df : :obj:`pd.DataFrame`
        Metadata associated with the submission data.
    version : str
        Version string to include in filename.

    Returns
    -------
    dict[str, xarray.Dataset]
        Dictionary mapping each scenario name to an :class:`xarray.Dataset`
        containing the climate model data and metadata in NetCDF format.
    """
    LOGGER.info("Coverting tabular data to NetCDF file")

    if isinstance(data_df, ScmRun):
        data_df = data_df.timeseries().reset_index()

    # Identify time columns (numeric strings)
    time_cols = [
        col
        for col in data_df.columns
        if isinstance(col, (int, datetime.datetime))
        or (isinstance(col, str) and col.isdigit())
    ]

    time = np.array(
        [
            col.year if isinstance(col, datetime.datetime) else int(col)
            for col in time_cols
        ]
    )

    # Identify climate model
    model_name = data_df["climate_model"].unique()
    if len(model_name) > 1:
        LOGGER.warning(
            "More than one climate model found. Only the first will be used."
        )
    model_name = model_name[0]

    # Extra model metadata
    headers = meta_df.columns
    values = meta_df.iloc[0]
    meta_attrs = dict(zip(headers, values))

    scenario_dict = {}
    # Group by scenario
    for scenario, group in data_df.groupby("scenario"):
        ensemble_members = group["ensemble_member"].unique()
        variables = group["variable"].unique()
        regions = group["region"].unique()

        # Identify IAM for the scenario
        iam_name = group["model"].unique()
        if len(iam_name) > 1:
            LOGGER.warning(
                "More than one IAM for {}. Only the first will be used.".format(
                    scenario
                )
            )
        iam_name = iam_name[0]

        # Prepare empty data array
        data = np.full(
            (len(ensemble_members), len(variables), len(regions), len(time)),
            np.nan,
            dtype=float,
        )

        # Metadata dict for variables
        metadata = {}

        # Fill in data
        for _, row in group.iterrows():
            var = row["variable"]
            em = row["ensemble_member"]
            re = row["region"]

            var_idx = np.where(variables == var)[0][0]
            em_idx = np.where(ensemble_members == em)[0][0]
            re_idx = np.where(regions == re)[0][0]

            data[em_idx, var_idx, re_idx, :] = row[time_cols].to_numpy(dtype=float)
            metadata[var] = {"unit": row["unit"]}

        LOGGER.info(f"Building netcdf file for {scenario}")
        # Build dataset
        ds = xr.Dataset(
            {
                var: (("ensemble_member", "region", "time"), data[:, vi, :, :])
                for vi, var in enumerate(variables)
            },
            coords={
                "variable": variables,
                "ensemble_member": ensemble_members,
                "region": regions,
                "time": time,
            },
        )

        # Add attributes
        for var in variables:
            ds[var].attrs.update(metadata[var])

        ds.attrs["version"] = version
        ds.attrs["scenario"] = scenario
        ds.attrs["model"] = iam_name
        ds.attrs.update(meta_attrs)

        scenario_dict[scenario] = ds

    return scenario_dict
