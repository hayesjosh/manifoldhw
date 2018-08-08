"""
Tests for loading data from the Cortex homework database.
"""
from datetime import datetime
import numpy as np
import os
import pandas as pd
import pytest
from sqlalchemy import create_engine
from dateutil.tz import tzutc
from dotenv import load_dotenv, find_dotenv

from src.data_loading import (
    get_internal_temps,
    get_lease_obligations,
    get_lease_obligation_temp_range,
    get_operating_period_in_utc,
)

load_dotenv(find_dotenv(), verbose=True)


def test_get_internal_temps():
    """
    This is a test to see if your implementation of get_internal_temps returns what we expect it to. You can
    add more tests if you like, but this should be sufficient to ensure that your implementation returns what
    is expected.
    """
    db = create_engine(os.environ["HW_DATABASE_URL"])
    df = get_internal_temps(db, 37, start_time="2018-02-04", end_time="2018-02-06")
    assert len(df) == 193
    assert len(df.columns) == 9
    sensor_ids = [17525, 17526, 17614, 17615, 17616, 17617, 17618, 17619, 17620]
    for sensor_id in sensor_ids:
        assert sensor_id in df.columns
    assert df.index[0].to_datetime64() == np.datetime64("2018-02-04T00:00:00.000000000")
    assert df.index[192].to_datetime64() == np.datetime64(
        "2018-02-06T00:00:00.000000000"
    )


def test_get_lease_obligations():
    lease_df = get_lease_obligations(37)
    assert lease_df.shape[0] == 7
    required_columns = [
        "local_operating_start_hour",
        "local_operating_end_hour",
        "local_timezone",
        "lower_operating_temp",
        "upper_operating_temp",
        "operating",
    ]
    for column_name in required_columns:
        assert column_name in lease_df.columns

    for dow in range(0, 5):
        assert lease_df.loc[dow]["operating"] == True
        assert lease_df.loc[dow]["local_operating_end_hour"] == 18
        assert lease_df.loc[dow]["local_operating_start_hour"] == 9
        assert lease_df.loc[dow]["lower_operating_temp"] == 70
        assert lease_df.loc[dow]["upper_operating_temp"] == 75

    for dow in range(5, 7):
        assert lease_df.loc[dow]["operating"] == False
        assert pd.isna(lease_df.loc[dow]["local_operating_end_hour"])
        assert pd.isna(lease_df.loc[dow]["local_operating_start_hour"])
        assert pd.isna(lease_df.loc[dow]["lower_operating_temp"])
        assert pd.isna(lease_df.loc[dow]["upper_operating_temp"])


def test_get_lease_obligation_temp_range():
    lease_df = get_lease_obligations(37)
    # test weekdays
    assert get_lease_obligation_temp_range(lease_df, "2018-02-05") == (70, 75)
    assert get_lease_obligation_temp_range(lease_df, "2018-08-03") == (70, 75)
    assert get_lease_obligation_temp_range(lease_df, "2018-05-18") == (70, 75)

    # test weekend
    assert pd.isna(get_lease_obligation_temp_range(lease_df, "2018-02-04")[0])
    assert pd.isna(get_lease_obligation_temp_range(lease_df, "2018-02-04")[1])
    assert pd.isna(get_lease_obligation_temp_range(lease_df, "2018-05-05")[0])
    assert pd.isna(get_lease_obligation_temp_range(lease_df, "2018-05-05")[1])


def test_get_operating_period():
    lease_df = get_lease_obligations(37)
    # test weekdays before daylight savings
    start_dt, end_dt = get_operating_period_in_utc(lease_df, "2018-02-05")
    assert start_dt == datetime(2018, 2, 5, 14, 0, tzinfo=tzutc())
    assert end_dt == datetime(2018, 2, 5, 23, 0, tzinfo=tzutc())
    # test weekdays after daylight savings
    start_dt, end_dt = get_operating_period_in_utc(lease_df, "2018-08-03")
    assert start_dt == datetime(2018, 8, 3, 13, 0, tzinfo=tzutc())
    assert end_dt == datetime(2018, 8, 3, 22, 0, tzinfo=tzutc())
    # test weekend
    assert pd.isna(get_operating_period_in_utc(lease_df, "2018-02-04")[0])
    assert pd.isna(get_operating_period_in_utc(lease_df, "2018-02-04")[1])
    assert pd.isna(get_operating_period_in_utc(lease_df, "2018-05-05")[0])
    assert pd.isna(get_operating_period_in_utc(lease_df, "2018-05-05")[1])
