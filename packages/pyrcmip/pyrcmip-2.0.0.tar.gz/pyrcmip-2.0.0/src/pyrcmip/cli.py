"""
Console script for rcmip.
"""

import gzip
import logging
import sys
from os.path import basename, join
from pathlib import Path

import boto3
import click
import jwt
import pandas as pd
import semver
import xarray as xr
from botocore.exceptions import ClientError

from pyrcmip.io import (
    _upload_file,
    read_results_submission,
    read_submission_model_comments,
    read_submission_model_metadata,
)
from pyrcmip.utils import tabular_to_netcdf
from pyrcmip.validate import validate_submission_bundle

LOGGER = logging.getLogger(__name__)
DEFAULT_LOG_FORMAT = "{process} {asctime} {levelname}:{name}:{message}"


class ColorFormatter(logging.Formatter):
    """
    Colour formatter for log messages

    A handy little tool for making our log messages look slightly prettier
    """

    colors = {
        "DEBUG": dict(fg="blue"),
        "INFO": dict(fg="green"),
        "WARNING": dict(fg="yellow"),
        "Error": dict(fg="red"),
        "ERROR": dict(fg="red"),
        "EXCEPTION": dict(fg="red"),
        "CRITICAL": dict(fg="red"),
    }

    def format(self, record):
        """
        Format a record so it has pretty colours

        Parameters
        ----------
        record : :obj:`logging.LogRecord`
            Record to format

        Returns
        -------
        str
            Formatted message string
        """
        formatted_message = super(ColorFormatter, self).format(record)

        level = record.levelname

        if level in self.colors:
            level_colour = click.style("{}".format(level), **self.colors[level])
            formatted_message = formatted_message.replace(level, level_colour)

        return formatted_message


class ClickHandler(logging.Handler):
    """
    Handler which emits using click when going to stdout
    """

    _use_stderr = True

    def emit(self, record):
        """
        Emit a record

        Parameters
        ----------
        record : :obj:`logging.LogRecord`
            Record to emit
        """
        try:
            msg = self.format(record)
            click.echo(msg, err=self._use_stderr)

        except Exception:  # pragma: no cover
            self.handleError(record)


_default_handler = ClickHandler()
_default_handler.formatter = ColorFormatter(DEFAULT_LOG_FORMAT, style="{")


@click.group(name="rcmip")
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION", "CRITICAL"]),
)
def cli(log_level):
    """
    Command-line interface for pyrcmip
    """
    root = logging.getLogger()
    root.handlers.append(_default_handler)
    root.setLevel(log_level)

    logging.captureWarnings(True)


def _read_bundle(timeseries, metadata, comments=None):
    try:
        scmrun = read_results_submission(timeseries)
    except Exception as e:
        LOGGER.exception("reading timeseries failed")
        raise click.ClickException(str(e))

    # Model metrics are not requested in the latest RCMIP round, but keeping it
    # around in case we want to re-enable it in the future.
    # try:
    #     model_reported_df = read_submission_model_reported(model_reported)
    # except Exception as e:
    #     LOGGER.exception("reading model_reported failed")
    #     raise click.ClickException(str(e))

    try:
        metadata_df = read_submission_model_metadata(metadata)
    except Exception as e:
        LOGGER.exception("reading metadata failed")
        raise click.ClickException(str(e))

    if comments is not None:
        try:
            comments_df = read_submission_model_comments(comments)
        except Exception as e:
            LOGGER.exception("reading comments failed")
            raise click.ClickException(str(e))
    else:
        comments_df = None

    return scmrun, metadata_df, comments_df


timeseries = click.argument(
    "timeseries", nargs=-1, required=True, type=click.Path(exists=True, dir_okay=False)
)
# Model metrics are not requested in the latest RCMIP round, but keeping it
# around in case we want to re-enable it in the future.
# model_reported = click.argument(
#     "model_reported",
#     nargs=1,
#     required=True,
#     type=click.Path(exists=True, dir_okay=False),
# )
metadata = click.argument(
    "metadata", nargs=1, required=True, type=click.Path(exists=True, dir_okay=False)
)


@cli.command()
@timeseries
@metadata
@click.option(
    "--comments",
    default=None,
    help="CSV with comments to upload along data.",
    type=click.Path(exists=True, dir_okay=False),
)
def validate(timeseries, metadata, comments=None):
    """
    Validate submission input.

    Two different types of input data are required for validation, namely:

    One or more ``TIMESERIES`` files in which the timeseries output is stored. These should be
    CSV or NetCDF files conforming to the format expected by ``scmdata``. Multiple
    timeseries inputs can be specified, but care must be taken to ensure that all of
    the individual timeseries have unique metadata.

    ``METADATA`` is the CSV file in which the metadata output is stored.

    Optionally, a CSV file with comments about the data to be uploaded can be included in the
    submission with the --comments flag. If included, it will also be validated.
    """
    for timeseries_fname in timeseries:
        scmrun, metadata_df, comments_df = _read_bundle(
            timeseries_fname, metadata, comments
        )

        try:
            validate_submission_bundle(scmrun, metadata_df, comments_df)
        except Exception as e:
            raise click.ClickException(str(e))


def validate_version(ctx, param, value):
    """
    Validate version string

    Parameters
    ----------
    ctx
        Not used

    param
        Not used

    value : str
        Version string to validate

    Returns
    -------
    str
        Validated version string

    Raises
    ------
    :obj:`click.BadParameter`
        Version string cannot be passed or does not follow semantic versioning
    """
    try:
        s = semver.VersionInfo.parse(value)

        if s.prerelease is None and s.build is None:
            return value
        else:
            raise click.BadParameter(
                "Version must only contain major, minor and patch values"
            )
    except ValueError:
        raise click.BadParameter("Cannot parse version string")


@cli.command()
@click.option(
    "--token",
    required=True,
    help="Authentication token. Contact eearp@leeds.ac.uk for a token",
)
@click.option("--bucket", default="alexrom-ns9188k-rcmip")
@click.option("--model", required=True)
@click.option(
    "--version",
    required=True,
    callback=validate_version,
    help="Version of the data being uploaded. Must be a valid semver version string (https://semver.org/). "
    "For example 2.0.0",
)
@timeseries
# @model_reported
@metadata
@click.option(
    "--comments",
    default=None,
    help="CSV with comments to upload along data.",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--endpoint", default="https://s3.nird.sigma2.no", help="S3 endpoint (for testing)"
)
def upload(token, bucket, model, version, timeseries, metadata, comments, endpoint):
    """
    Validate and upload data to RCMIP's S3 bucket.

    All the files for a given version have to be uploaded together. Notice that this command
    will convert the data into a netCDF file prior to uploading it to the remote server if not
    already in that format.

    One or more ``TIMESERIES`` files in which the timeseries output is stored. These should be
    CSV or NetCDF files conforming to the format expected by ``scmdata``. Multiple
    timeseries inputs can be specified, but care must be taken to ensure that all of
    the individual timeseries have unique metadata. Each timeseries file will be validated and
    uploaded independently. Each file must contain all the variables pertaining to any simulation
    scenarios included in that file.

    ``METADATA`` is the CSV file in which the metadata output is stored.

    Optionally, a CSV file with comments about the data to be uploaded can be included in the
    submission with the --comments flag.
    """
    # Prepare client to upload data to S3
    t = jwt.decode(token, options={"verify_signature": False})
    session = boto3.session.Session(
        aws_access_key_id=t["access_key_id"],
        aws_secret_access_key=t["secret_access_key"],
    )
    client = session.client("s3", endpoint_url=endpoint)

    root_key = "{}/{}/{}".format(t["org"], model, version)

    for file_idx, timeseries_fname in enumerate(timeseries):
        LOGGER.info("Reading and validating {}".format(timeseries_fname))
        try:
            scmrun, metadata_df, comments_df = _read_bundle(
                timeseries_fname, metadata, comments
            )
            (
                scmrun_rcmip_compatible,
                metadata_rcmip_compatible,
                comments_rcmip_compatible,
            ) = validate_submission_bundle(scmrun, metadata_df, comments_df)
        except Exception as e:
            LOGGER.exception(e)
            raise click.ClickException("Validation failed. Fix issues and rerun")

        # Check if this version is already uploaded (using the {key}-complete dummy file)
        try:
            LOGGER.debug("Checking if object with key {} exists".format(root_key))
            client.head_object(Bucket=bucket, Key=root_key + "-complete")

            raise click.ClickException(
                "Data for this version has already been uploaded. Increment the version and try again"
            )
        except ClientError:
            LOGGER.debug("Object with key {} does not exist".format(root_key))

        def _get_fname(data_type, scenario=None):
            if data_type == "data":
                if scenario:
                    fname = "rcmip-{}-{}-{}-{}-{:03}".format(
                        model, version, data_type, scenario, file_idx
                    )
                else:
                    fname = "rcmip-{}-{}-{}-{:03}".format(
                        model, version, data_type, file_idx
                    )
            else:
                fname = "rcmip-{}-{}-{}".format(model, version, data_type)
            return join(root_key, fname)

        # Create netcdf file with SCM data
        scenarios_to_upload = tabular_to_netcdf(
            scmrun_rcmip_compatible, metadata_rcmip_compatible, version=version
        )

        for scenario, df in scenarios_to_upload.items():
            # upload it
            _upload_file(
                client,
                bucket=bucket,
                key=_get_fname("data", scenario),
                run=df,
                file_format="nc",
            )

        # If any comments were detected, upload them to the folder
        if comments is not None:
            _upload_file(
                client,
                bucket=bucket,
                key=_get_fname("comments"),
                run=comments_rcmip_compatible,
                file_format="csv",
            )

    # Finally mark the upload as complete by uploading a dummy file
    # Writing this dummy file will be used to start the processing of the upload
    client.put_object(Bucket=bucket, Key=root_key + "-complete")

    LOGGER.info("All files uploaded successfully")


@cli.command()
@click.option(
    "--token",
    required=True,
    help="Authentication token. Contact eearp@leeds.ac.uk for a token",
)
@click.option("--bucket", default="alexrom-ns9188k-rcmip")
@click.option("--model", required=True)
@click.option(
    "--version",
    required=True,
    callback=validate_version,
    help="Version of the data that was uploaded. Must be a valid semver version string (https://semver.org/). "
    "For example 2.0.0",
)
@click.option(
    "--unzip",
    is_flag=True,
    default=False,
    help="If set, unzip .gz files directly instead of saving compressed file.",
)
@click.argument("outdir", required=True, type=click.Path(exists=True, dir_okay=True))
@click.option(
    "--endpoint", default="https://s3.nird.sigma2.no", help="S3 endpoint (for testing)"
)
def download(token, bucket, model, version, unzip, outdir, endpoint):
    """
    Download submitted files.
    """
    t = jwt.decode(token, options={"verify_signature": False})
    session = boto3.session.Session(
        aws_access_key_id=t["access_key_id"],
        aws_secret_access_key=t["secret_access_key"],
    )
    client = session.client("s3", endpoint_url=endpoint)

    root_key = "{}/{}/{}/".format(t["org"], model, version)  # trailing / is important

    resp = client.list_objects(Bucket=bucket, Prefix=root_key)

    if "Contents" not in resp:
        raise click.ClickException(
            "No files for {}=={} have been uploaded".format(model, version)
        )

    for o in resp["Contents"]:
        key = o["Key"]
        LOGGER.info("Downloading {}".format(key))
        resp = client.get_object(Bucket=bucket, Key=key)

        local_path = join(outdir, basename(key))

        if unzip and local_path.endswith(".gz"):
            local_path = local_path[:-3]  # remove .gz from saved file name
            LOGGER.info("Unzipping {} -> {}".format(key, local_path))

            # Stream gzip from S3 and write uncompressed to disk
            with gzip.open(resp["Body"], "rb") as f_in, open(local_path, "wb") as f_out:
                for chunk in iter(lambda: f_in.read(1024 * 1024), b""):
                    f_out.write(chunk)
        else:
            # Save as-is
            with open(local_path, "wb") as f:
                for chunk in resp["Body"]:
                    f.write(chunk)

    LOGGER.info("All files downloaded successfully")


@cli.command()
@click.argument(
    "file", nargs=1, required=True, type=click.Path(exists=True, dir_okay=False)
)
@click.argument("outdir", required=True, type=click.Path(exists=True, dir_okay=True))
def convert_to_csvs(file, outdir):
    """
    Convert a NetCDF scenario file to CSVs.

    This command will produce two CSV files:

    - a main data CSV file with the numerical values of the scenario variables

    - a metadata CSV file
    """
    LOGGER.info("Loading {}".format(file))
    ds = xr.open_dataset(file, engine="netcdf4")

    # Extract attributes
    scenario = ds.attrs.get("scenario", "unknown")
    model_name = ds.attrs.get("climate_model", "unknown")
    version = ds.attrs.get("version", "unknown")

    # Build metadata CSV
    # Grab only keys that are in our mapping
    metadata_keys = [k for k in ds.attrs.keys()]
    metadata_values = [ds.attrs.get(k) for k in metadata_keys]

    metadata_df = pd.DataFrame([metadata_keys, metadata_values])
    metadata_output = (
        Path(outdir) / f"rcmip-{model_name}-{version}-metadata-{scenario}.csv"
    )
    metadata_df.to_csv(metadata_output, index=False, header=False)

    LOGGER.info("Successfully created metadata CSV file: {}".format(metadata_output))

    # Build data CSV
    rows = []
    time = ds.coords["time"].values
    for var in ds.data_vars:
        unit = ds[var].attrs.get("unit", "unknown")
        for em in ds.coords["ensemble_member"].values:
            for re in ds.coords["region"].values:
                values = ds[var].sel(ensemble_member=em, region=re).values
                row = {
                    "climate_model": model_name,
                    "model": ds.attrs.get("model", "unknown"),
                    "scenario": scenario,
                    "variable": var,
                    "ensemble_member": em,
                    "region": re,
                    "unit": unit,
                }
                row.update({str(t): v for t, v in zip(time, values)})
                rows.append(row)

    df_out = pd.DataFrame(rows)
    data_output = Path(outdir) / f"rcmip-{model_name}-{version}-data-{scenario}.csv"
    df_out.to_csv(data_output, index=False)

    LOGGER.info("Successfully created values CSV file: {}".format(data_output))


def run_cli():
    """
    Run command-line interface

    TODO: fix this so environment variables can be used
    """
    sys.exit(cli(auto_envvar_prefix="RCMIP"))  # pragma: no cover


if __name__ == "__main__":
    run_cli()  # pragma: no cover
