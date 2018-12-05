"""
This module contains estimators that determine the time a building satisfied its lease obligation on any given day.
:copyright: Cortex
:author: Sourav Dey <sdey@manifold.ai>
"""
from abc import ABC, abstractmethod
import os
from sqlalchemy import create_engine
from .data_loading import (
    get_lease_obligations,
    get_lease_obligation_temp_range,
    get_internal_temps
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
        # db = create_engine(os.environ["HW_DATABASE_URL"])
        db = create_engine('postgresql://postgres:Winter1234@localhost/Manifold1')
        #Gather the correct data to use
        df_est = get_internal_temps(db, self.building_id, start_time=estimation_date, end_time=estimation_date)
        #Determine if it is a valid date
        valid_date = operatingDayCheck(df_est, estimation_date)

        #Find the first time of lease-obligation
        #Regretably, the good_sensors list is hardcoded in right now. Given more time, I'd automate it.
        good_sensors = good_sensors = [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 67, 68, 69, 70, 71, 72, 3025, 3027, 3032, 3036, 3049, 3083, 3099, 3101, 3106, 3129, 3133, 3141, 3153, 3156, 3158, 3163, 3164, 3169, 3197, 3201, 3209, 3220, 3228, 3234, 3269, 3350, 15163, 11493, 11494, 11496, 11497, 11500, 11501, 11502, 11504, 11510, 11512, 11513, 11515, 11516, 11517, 11518, 11527, 11528, 11529, 11550, 11551, 11552, 11553, 11560, 11561, 11562, 11564, 11565, 11566, 11568, 11569, 11577, 11578, 11580, 11592, 11594, 11596, 11598, 11599, 11600, 11603, 11608, 11617, 11618, 11620, 11621, 11625, 11627, 11628, 11629, 11630, 11635, 11637, 11640, 11641, 11643, 11645, 11649, 11657, 11674, 11675, 11676, 17525, 17617, 18780]

        result_time = getPred2(df_est, good_sensors)
            #Note the method of prediction can be hot-swapped here very easily e.g. getPred1(), getPred2(), getPred3()...

        #Format return based on whether the day is a work day or not
        if valid_date:
            return (valid_date, result_time)
        else:
            return (valid_date, None)

def operatingDayCheck(df, estimation_date):
    """
    This is a function that makes determines if a specified date is a work day.
    :param df: a dataframe that contains only data on one building
    :param estimation_date: date in string format
    :return: A  boolean denoting if the day was an operating day or not.
    """
    #Gather day of week from index. Create boolean values by work-week days.
    try:
        df['weekday'] = df.index.dayofweek
        df['work_day'] = df['weekday'].between(0,4, inclusive=True)
        #Return a single value for specified day
        return df['work_day'][0]
    except IndexError:
        return None

def getPred1(df):
    """
    This is a function that makes an assessment about when a building is 'at lease obligation temperature.'
    :param df: a dataframe that contains only data on one building
    :param estimation_date: date in string format
    :return: A tuple of (operating_day, datetime) where the operating_day is a boolean denoting if the day was an
    operating day or not. Time is a Python datetime object.  If it's not an operating day this datetime will be
    None. Even if it IS an operating day and the satisfied time can't be found for some reason (e.g. no data
    for that day, logic does not lead to a result) this datetime can be None.
    """
    #Gather specified day's data. Calculate sensors' mean temperature and create boolean if it is in range.
    df_pred1 = df
    df_pred1 = df_pred1.assign(mean_temp = df_pred1.mean(axis=1))
    df_pred1 = df_pred1.assign(valid=df_pred1['mean_temp'].between(70.0,75.0, inclusive=True))

    #Return the first time of day that is in the valid temperature range, if it exists. Else return "Not Satisfied"
    if df_pred1['valid'].any():
        ans = (df_pred1['valid'] == True).idxmax()
        return ans
    else:
        return "Not Satisfied"

#CALCULATE LEASE OBLIGATION TIMES
def getPred2(df, good_sensors):
    """
    This is a function that makes an assessment about when a building is 'at lease obligation temperature.'
    :param df: a dataframe that contains only data on one building
    :param estimation_date: date in string format
    :return: A tuple of (operating_day, datetime) where the operating_day is a boolean denoting if the day was an
    operating day or not. Time is a Python datetime object.  If it's not an operating day this datetime will be
    None. Even if it IS an operating day and the satisfied time can't be found for some reason (e.g. no data
    for that day, logic does not lead to a result) this datetime can be None.
    """
    #Gather specified day's data. Calculate sensors' mean temperature and create boolean if it is in range.
    df_pred1 = df.loc[:,df.columns.isin(good_sensors)]
    df_pred1 = df_pred1.assign(mean_temp = df_pred1.mean(axis=1))
    df_pred1 = df_pred1.assign(valid=df_pred1['mean_temp'].between(70.0,75.0, inclusive=True))

    #Return the first time of day that is in the valid temperature range, if it exists. Else return "Not Satisfied"
    if df_pred1['valid'].any():
        ans = (df_pred1['valid'] == True).idxmax()
        return ans
    else:
        return "Not Satisfied"
