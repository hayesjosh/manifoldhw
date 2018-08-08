"""
This module contains estimators that determine the time a building satisfied its lease obligation on any given day.
:copyright: Cortex
:author: Sourav Dey <sdey@manifold.ai>
"""
from abc import ABC, abstractmethod

from .data_loading import (
    get_lease_obligations,
    get_lease_obligation_temp_range,
)


class LeaseSatisfiedTimeEstimator(ABC):
    """
    Abstract base class for all the lease satisfied time estimators.
    """

    def __init__(
        self, building_id, **kwargs
    ):
        self.building_id = building_id
        self.lease_obligations = get_lease_obligations(building_id)
        super().__init__()

    @abstractmethod
    def compute_lease_satisfied_time(self, estimation_date):
        """
        This is the function that has be overloaded to implement your algorithm.
        :param estimation_date: A date in string format.
        :return: A tuple of (operating_day, datetime) where the operating_day is a boolean denoting if the day was an
        operating day or not. Time is a Python datetime object. If it's not an operating day, or the satisfied time
        can't be found for some reason this datetime might be None.
        """
        pass


class YourEstimator(LeaseSatisfiedTimeEstimator):
    """
    TODO: This is where you should implement your algorithm. Note that you can have other classes and helper functions,
    but the top level estimator must adhere to this interface.
    """

    def compute_lease_satisfied_time(self, estimation_date):
        """
        :param estimation_date: date in string format
        :return: A tuple of (operating_day, datetime) where the operating_day is a boolean denoting if the day was an
        operating day or not. Time is a Python datetime object.  If it's not an operating day this datetime will be
        None. Even if it IS an operating day and the satisfied time can't be found for some reason (e.g. no data
        for that day, logic does not lead to a result) this datetime can be None.
        """
        raise NotImplementedError()
