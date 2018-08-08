"""
This module runs the lease satisfied estimation algorithm for all historical days.
:copyright: Cortex
:author: Sourav Dey <sdey@manifold.ai>
"""
import click
from dotenv import load_dotenv, find_dotenv
import logging
import os
import pandas as pd
import yaml
import sys

sys.path.append("..")

from src.lease_satisfied_estimator import YourEstimator

load_dotenv(find_dotenv(), verbose=True)


def _parse_config_and_setup_directory(config_file):
    """
    Helper function to parse config file and setup the directory structure of the error directory.
    :param config_file:
    :return:
    """
    with open(config_file, "rb") as f:
        config = yaml.load(f)

    # Create error output directory
    if not os.path.exists(config["error_analysis_dir"]):
        os.makedirs(config["error_analysis_dir"])
    else:
        choice = input(
            "Directory {} exists. Do you want to overwrite? (Hit y to overwrite, any other key to abort): ".format(
                config["error_analysis_dir"]
            )
        )
        if choice != "y":
            sys.exit("Aborting run. Error analysis directory exists.")

    # Copy config file into error_analysis_dir so that we can keep the configuration of the experiment with the results.
    # This way the entire directory can be zipped up and sent around with the bookkeeping intact.
    with open(os.path.join(config["error_analysis_dir"], "config.yml"), "w") as f:
        yaml.dump(config, f)

    return config


@click.command()
@click.argument("config_file", type=click.Path(exists=True))
def estimate_lease_satisfied_times(config_file):
    """
    Main function that estimates lease satisfied times for all historical days for all buildings.
    :param config_file:
    :return:
    """
    config = _parse_config_and_setup_directory(config_file)
    dates = pd.date_range(start=config["start_date"], end=config["end_date"])
    for building_id in config["buildings"]:
        logging.info(
            "Estimating lease obligation satisfied times for building = {}".format(
                building_id
            )
        )
        me = YourEstimator(building_id=building_id)
        df_dict = {}
        for date in dates:
            logging.debug(
                "Estimating for building = {}, date = {}".format(building_id, date)
            )
            operating, lease_satisfied_time = me.compute_lease_satisfied_time(str(date))
            df_dict[str(date)] = {
                "building_id": building_id,
                "operating": operating,
                "lease_satisfied_time": lease_satisfied_time,
            }
            logging.debug(df_dict[str(date)])

        lease_satisfied_time_df = pd.DataFrame.from_dict(df_dict, orient="index")
        lease_satisfied_time_df.to_csv(
            os.path.join(
                config["error_analysis_dir"],
                "lease_obligation_satisfied_times_{}.csv".format(building_id),
            )
        )
        logging.info("Wrote CSV for building = {}".format(building_id))


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)
    estimate_lease_satisfied_times()
