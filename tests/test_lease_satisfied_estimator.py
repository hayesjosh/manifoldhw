"""
Tests for the lease satisfied estimator algorithms.
TODO: You should implement additional tests here. The code below is just a stub.
"""
from datetime import datetime
import pytest

from src.lease_satisfied_estimator import YourEstimator


def test_your_estimator():
    me = YourEstimator(building_id=37)
    # Check operating day
    operating, lease_satisfied_time = me.compute_lease_satisfied_time("2018-02-05")
    assert operating == True
    assert lease_satisfied_time is not None
    # Check non-operating day
    operating, lease_satisfied_time = me.compute_lease_satisfied_time("2018-02-04")
    assert operating == False
    assert lease_satisfied_time is None
