"""
Utility functions for validating RCMIP submissions
"""
import os.path

import pandas as pd

# For Python 3.9+
try:
    from importlib.resources import files
except ImportError:
    # For Python 3.7-3.8
    from importlib_resources import files

SUBMISSION_TEMPLATE = os.path.join(
    "..", "data", "rcmip3-data-submission-template-v1-0-0.xlsx"
)


def load_submission_template_definitions(fp=None, component="variables"):
    """
    Load submission template definitions

    Parameters
    ----------
    fp : str
        Filepath from which to load the definitions. If ``None``, definitions
        will be loaded from
        ``pyrcmip/data/rcmip-data-submission-template-v4-0-0.xlsx``.

    component : {"variables", "regions", "scenarios"}
        Definitions section to load

    Returns
    -------
    :obj:`pd.DataFrame`
    """
    if fp is None:
        # Get the package's data directory and open the resource
        package_files = files("pyrcmip.validate").joinpath(SUBMISSION_TEMPLATE)
        fp = package_files.open("rb")

    if component == "variables":
        component_kwargs = {
            "sheet_name": "variable_definitions",
            "usecols": range(1, 8),
        }

    elif component == "regions":
        component_kwargs = {
            "sheet_name": "region_definitions",
        }

    elif component == "scenarios":
        component_kwargs = {
            "sheet_name": "scenario_info",
            "skiprows": 2,
            "usecols": range(1, 7),
        }

    else:
        raise NotImplementedError("Unrecognised component: {}".format(component))

    out = pd.read_excel(fp, engine="openpyxl", **component_kwargs)
    out.columns = out.columns.str.lower()

    if component == "variables":
        out["tier"] = out["tier"].astype("category")

    elif component == "scenarios":
        out = out.dropna()
        column_map = {
            "# scenario id": "scenario_id",
            "# type": "idealised_tag",
            "# scenario description": "description",
            "# scenario specification": "specification",
            "# scenario duration": "duration",
            "# tier in rcmip": "tier",
        }
        out.columns = out.columns.map(column_map)
        out["tier"] = out["tier"].astype("category")

    unnamed_cols = [c for c in out if c.startswith("unnamed:")]
    if unnamed_cols:
        out = out.drop(unnamed_cols, axis="columns")

    return out
