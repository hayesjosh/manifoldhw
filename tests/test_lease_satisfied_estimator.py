"""
Tests for the lease satisfied estimator algorithms.
TODO: You should implement additional tests here. The code below is just a stub.
"""
from datetime import datetime
import pandas as pd
import pytest
import os
from sqlalchemy import create_engine
from src.data_loading import (
    get_internal_temps,
    get_lease_obligations,
    get_lease_obligation_temp_range,
    get_operating_period_in_utc,
)

from src.lease_satisfied_estimator import YourEstimator, operatingDayCheck, getPred1



def test_your_estimator():
    # db = create_engine('postgresql://postgres:Winter1234@localhost/Manifold1')
    me = YourEstimator(building_id=37)

    # Check operating day
    operating, lease_satisfied_time = me.compute_lease_satisfied_time("2018-02-05")
    assert operating == True
    assert lease_satisfied_time is not None
    # Check non-operating day
    operating, lease_satisfied_time = me.compute_lease_satisfied_time("2018-02-04")
    assert operating == False
    assert lease_satisfied_time is None
