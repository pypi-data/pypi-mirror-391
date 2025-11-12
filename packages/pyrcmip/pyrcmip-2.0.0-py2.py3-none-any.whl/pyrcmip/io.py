"""
Input and output handling
"""

import contextlib
import gzip
import io
import logging
import os
import os.path
import tempfile

import click
import pandas as pd
import xarray as xr
from botocore.exceptions import ClientError
from scmdata.run import ScmRun, run_append

LOGGER = logging.getLogger(__name__)

CSV_COLUMN_MAP = {
    "Climate Model": "climate_model",
    "Climate Model Name": "climate_model_name",
    "Climate Model Version": "climate_model_version",
    "Climate Model Configuration Label": "climate_model_configuration_label",
    "Climate Model Configuration Description": "climate_model_configuration_description",
    "Project": "project",
    "Name of Person": "name_of_person",
    "Literature Reference": "literature_reference",
}


def ensure_dir_exists(fp):
    """
    Ensure directory exists

    Parameters
    ----------
    fp : str
        Filepath of which to ensure the directory exists
    """
    dir_to_check = os.path.dirname(fp)
    if not os.path.isdir(dir_to_check):
        LOGGER.info("Creating {}".format(dir_to_check))
        os.makedirs(dir_to_check)


def read_results_submission(results):
    """
    Read results submission

    Parameters
    ----------
    results : str or list of str
        Files to read in. All files to be read should be formatted as csv or
        xlsx files following the formatting defined in the template
        spreadsheet.

    Returns
    -------
    :obj:`scmdata.ScmRun`
        Results read in from the submission(s)
    """
    if isinstance(results, str):
        results = [results]

    db = []
    for rf in results:
        LOGGER.info("Reading %s", rf)

        if rf.endswith(".nc"):
            LOGGER.info("Assuming netCDF format")
            loaded = ScmRun.from_nc(rf)
        else:
            if rf.endswith(".xlsx") or rf.endswith(".xls"):
                LOGGER.info("Assuming excel format")
                loaded = pd.read_excel(rf, sheet_name="your_data", engine="openpyxl")
            else:
                LOGGER.info("Assuming csv format")
                loaded = pd.read_csv(rf)

            LOGGER.debug("Converting all columns to lowercase")
            loaded.columns = loaded.columns.astype(str).str.lower()
            loaded = ScmRun(loaded)

        db.append(ScmRun(loaded))

    LOGGER.info("Joining results together")
    db = run_append(db)

    return db


def read_submission_model_reported(fp):
    """
    Read the model reported component of a submission

    Parameters
    ----------
    fp : str
        Filepath to read

    Returns
    -------
    :obj:`pd.DataFrame`
    """
    out = pd.read_csv(fp)

    return out


def read_submission_model_metadata(fp):
    """
    Read the model metadata component of a submission

    Parameters
    ----------
    fp : str
        Filepath to read

    Returns
    -------
    :obj:`pd.DataFrame`
    """
    LOGGER.info("Reading %s", fp)

    if fp.endswith(".xlsx"):
        LOGGER.info("Assuming excel format")

        meta_df = pd.read_excel(fp, sheet_name="meta_model")

        if len(meta_df) > 3:
            LOGGER.warning(
                "More than one line in 'meta_model' sheet. Only the first will be used."
            )
        elif len(meta_df) < 3:
            error_str = (
                "No model metadata found. Consider filling the 'meta_model' sheet."
            )
            LOGGER.exception(error_str)
            raise click.ClickException(str(error_str))

        meta_df = meta_df.iloc[2:4, :].drop(meta_df.columns[[0]], axis=1)
        meta_df = meta_df.rename(columns=CSV_COLUMN_MAP)

    elif fp.endswith(".csv"):
        LOGGER.info("Assuming CSV format")
        meta_df = pd.read_csv(fp)

        # Assuming the structure is the same as in the .xlsx file
        if "Combination of Climate" in str(meta_df.iloc[0]):
            meta_df = meta_df.iloc[2:, :]

        if len(meta_df) > 1:
            LOGGER.warning(
                "More than one line of metadata answers found. Only the first line will be used."
            )
        elif len(meta_df) < 1:
            error_str = "Metadata file does not have enough rows. Expecting headers + one line of values."
            LOGGER.exception(error_str)
            raise click.ClickException(str(error_str))

        # Make sure the column names are what we expect
        meta_df = meta_df.rename(CSV_COLUMN_MAP)

    return meta_df


def read_submission_model_comments(fp):
    """
    Read the submission comments.

    Parameters
    ----------
    fp : str
        Filepath to read

    Returns
    -------
    :obj:`pd.DataFrame`
    """
    LOGGER.info("Reading %s", fp)

    if fp.endswith(".xlsx"):
        LOGGER.info("Assuming excel format")

        comments_df = pd.read_excel(fp, sheet_name="comments")

        if len(comments_df) < 2:
            error_str = "No submission comments found in supplied file."
            LOGGER.exception(error_str)
            raise click.ClickException(str(error_str))

        comments_df = comments_df.iloc[1:, 2:]

    elif fp.endswith(".csv"):
        LOGGER.info("Assuming CSV format")
        comments_df = pd.read_csv(fp)

        # Assuming the structure is the same as in the .xlsx file
        if "Comments relating" in str(comments_df.iloc[0]):
            comments_df = comments_df.iloc[1:, :].drop(
                [
                    "Comments relating to your submitted data",
                    "Unnamed: 1",
                    "Unnamed: 10",
                ],
                axis=1,
            )

    if len(comments_df) < 1:
        error_str = "No submission comments found in supplied file."
        LOGGER.exception(error_str)
        raise click.ClickException(str(error_str))

    comments_df.columns = comments_df.columns.astype(str).str.lower()
    comments_df = comments_df.rename({"climate model": "climate_model"}, axis=1)

    comments_df = comments_df.dropna(how="all")

    return comments_df


@contextlib.contextmanager
def temporary_file_to_upload(df, max_size=1024, compress=False, file_format="csv"):
    """
    Create a gzipped temporary serialized version of a file to upload

    Attempts to keep the file in memory until it exceeds `max_size`. The file is then stored on-disk
    and cleaned up at the end of the context.

    The temporary location can be overriden using the `TMPDIR` environment variable as per
    https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir

    Notice that this only supports taking an :obj:`scmdata.ScmRun`|:obj:`xarray.Dataset` if the target
    format is CSV (file_format="csv"), and :obj:`xarray.Dataset` if the target format is netCDF
    (file_format="nc").

    Parameters
    ----------
    df : :obj:`scmdata.ScmRun` | :obj:`pd.DataFrame` | :obj:`xarray.Dataset`
        Run to store

    max_size: int or float
        Max size in MB before file is temporarily streamed to disk. Defaults to 1GB

    compress: bool
        whether to compress the file to upload

    file_format: str
        File format for the target file to upload. Allowed values are: "csv" and "nc".

    Returns
    -------
    :obj:`tempfile.SpooledTemporaryFile`
        Open file object ready to be streamed
    """
    # For the time being, this function only supports:
    # SCMrun instance and pandas dataframe if target format is nc
    # Xarray Dataset if target format is nc
    if file_format == "csv" and isinstance(df, (ScmRun, pd.DataFrame)):
        if isinstance(df, ScmRun):
            df = df.timeseries().reset_index()

        if compress:
            buffer = tempfile.SpooledTemporaryFile(max_size=max_size * 1024 * 1024)
            with gzip.GzipFile(mode="w", fileobj=buffer) as gz_file:
                df.to_csv(io.TextIOWrapper(gz_file, "utf8"), index=False)
        else:
            buffer = io.BytesIO(df.to_csv(index=False).encode("utf8"))
    elif file_format == "nc" and isinstance(df, (xr.Dataset)):
        if compress:
            buffer = tempfile.SpooledTemporaryFile(max_size=max_size * 1024 * 1024)
            # write to a real temp file first as a workaround to make this work
            with tempfile.NamedTemporaryFile(suffix=".nc") as tmp:
                df.to_netcdf(tmp.name)
                tmp.seek(0)
                with gzip.GzipFile(mode="w", fileobj=buffer) as gz_file:
                    gz_file.write(tmp.read())
        else:
            buffer = io.BytesIO(df.to_netcdf())
    else:
        raise ValueError(
            f"Unsupported file_format: {file_format} and input format combination"
        )

    buffer.seek(0)

    try:
        yield buffer
    finally:
        buffer.close()


def _upload_file(client, bucket, key, run, compress=True, file_format="csv"):
    """
    Upload a file (CSV or NetCDF) to S3.

    Small files are kept in memory while bigger files are written to disk and automatically cleaned up
    """
    LOGGER.info("Preparing {} for upload".format(key))
    with temporary_file_to_upload(
        run, max_size=1024, compress=compress, file_format=file_format
    ) as fh:
        try:
            if file_format in ("csv", "nc"):
                key += f".{file_format}"
            else:
                raise ValueError(f"Unsupported file_format: {format}")
            if compress:
                key += ".gz"
            LOGGER.info("Uploading {}".format(key))
            client.upload_fileobj(fh, Bucket=bucket, Key=key)
        except ClientError:  # pragma: no cover
            LOGGER.exception("Failed to upload file")
            raise click.ClickException("Failed to upload file")
