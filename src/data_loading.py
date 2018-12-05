"""
This module houses helper functions to access the sensor time series data and lease obligation data.
:copyright: Cortex
:author: Sourav Dey <sdey@manifold.ai>
"""
from datetime import timedelta, datetime
from dateutil.parser import parse
from dateutil import tz
import pandas as pd


def get_internal_temps(db, building_id, start_time, end_time):
    """
    Get a portion of all the internal temperature time series for a building.
    :param db: an active sql engine - ex. `db = create_engine(os.environ["HW_DATABASE_URL"])`
    :param building_id: integer
    :param start_time: start time string - 'yyyy-dd-mm' treated differently than 'yyyy-dd-mm hh:mm:ss'
    :param end_time: end time string - 'yyyy-dd-mm' treated differently than 'yyyy-dd-mm hh:mm:ss'
    :return: DataFrame with time as index and columns as internal temperature sensors.
    """
    #Need to create the SQL query. But that depends on a number of ways that the dates are input.
    """
    The gnarly bit of code that follows is largely because the query strings differ between test_*.py and run_historical_estimation.py,
    and rather than alter your code (because I wasn't sure if you would test my functions with other code snippets) I wrote a series
    of if statements to respond to the different submission types.
    """
    #Determining if range is one day, or a date range
    if start_time != end_time:
        #Identifying if start_time end_time are 'yyyy-dd-mm hh:mm:ss'
        if len(start_time) > 10:
            #Define a custom SQL query based on the inputs
            sql_query = 'SELECT f1.measured_at as time, f1.measurement as temperature, b2.id as sensor_id FROM building_sensor_configs b2 JOIN floor_temperature_measurements f1 ON b2.id = f1.building_sensor_config_id WHERE b2.building_id = ' \
            + str(building_id) + \
            ' and b2.ignore = False and  f1.bad_data = False and f1.measured_at >= ' \
            + "'" + start_time + "'" +\
            ' AND f1.measured_at <= ' \
            + "'" + end_time + "'"
        #otherwise our start_time and end_time are 'yyy-dd-mm'
        else:
            start_ = start_time + " 00:00:00"
            end_ = end_time + " 00:00:00"
            #Define a custom SQL query based on the inputs
            sql_query = 'SELECT f1.measured_at as time, f1.measurement as temperature, b2.id as sensor_id FROM building_sensor_configs b2 JOIN floor_temperature_measurements f1 ON b2.id = f1.building_sensor_config_id WHERE b2.building_id = ' \
            + str(building_id) + \
            ' and b2.ignore = False and  f1.bad_data = False and f1.measured_at >= ' \
            + "'" + start_ + "'" +\
            ' AND f1.measured_at <= ' \
            + "'" + end_ + "'"
    #In this case, the input dates are the same
    else:
        if len(start_time) > 10:
            #Define a custom SQL query based on the inputs
            sql_query = 'SELECT f1.measured_at as time, f1.measurement as temperature, b2.id as sensor_id FROM building_sensor_configs b2 JOIN floor_temperature_measurements f1 ON b2.id = f1.building_sensor_config_id WHERE b2.building_id = ' \
            + str(building_id) + \
            ' and b2.ignore = False and  f1.bad_data = False and f1.measured_at between ' \
            + "'" + start_time + "'" +\
            ' AND ' \
            + "date '" + start_time + "' + interval '23 hour';"
        else:
            start_ = start_time + " 00:00:00"
            end_ = start_time + " 23:59:59"
            #Define a custom SQL query based on the inputs
            sql_query = 'SELECT f1.measured_at as time, f1.measurement as temperature, b2.id as sensor_id FROM building_sensor_configs b2 JOIN floor_temperature_measurements f1 ON b2.id = f1.building_sensor_config_id WHERE b2.building_id = ' \
            + str(building_id) + \
            ' and b2.ignore = False and  f1.bad_data = False and f1.measured_at >= ' \
            + "'" + start_ + "'" +\
            ' AND f1.measured_at <= ' \
            + "'" + end_ + "'"

    #Run that query and put results into a dataframe
    df = pd.read_sql(sql_query, db)
    df['time'] = pd.to_datetime(df['time'])
    df_a = df.pivot(index='time', columns='sensor_id', values='temperature')
    return df_a


def get_lease_obligations(building_id):
    """
    Get the lease obligations for a particular building.
    :param building_id: integer
    :return: DataFrame with day of week as index and columns for {operating, lower_operating_temp, upper_operating_temp,
     local_operating_start_hour, local_operating_end_hour, local_timezone}
    """
    # TODO: Note that this is a mocked function that returns some reasonable hard-coded defaults.
    # The lease obligations are actually held in the database.  They are different across buildings and on
    # different days of the week.  Even more complex, they may even change over time in a single building,
    # e.g. winter vs. summer.
    lease_obligations = []
    for dow in range(0, 5):
        lease_obligation_weekday = {
            "dow": dow,
            "operating": True,
            "lower_operating_temp": 70.,
            "upper_operating_temp": 75.,
            "local_operating_start_hour": 9,
            "local_operating_end_hour": 18,
            "local_timezone": "America/New_York",
        }
        lease_obligations.append(lease_obligation_weekday)

    for dow in range(5, 7):
        lease_obligation_weekend = {
            "dow": dow,
            "operating": False,
            "lower_operating_temp": None,
            "upper_operating_temp": None,
            "local_operating_start_hour": None,
            "local_operating_end_hour": None,
            "local_timezone": "America/New_York",
        }
        lease_obligations.append(lease_obligation_weekend)

    return pd.DataFrame(lease_obligations).set_index("dow")


def get_lease_obligation_temp_range(lease_obligations, estimation_date):
    """
    Extract the lower and upper lease obligation temperatures for a building on a single day.
    :param lease_obligations: DataFrame of lease obligations
    :param estimation_date: date in string format
    :return:
    """
    dow = parse(estimation_date).weekday()
    return (
        lease_obligations.loc[dow]["lower_operating_temp"],
        lease_obligations.loc[dow]["upper_operating_temp"],
    )


def get_operating_period_in_utc(lease_obligations, estimation_date):
    """
    Extract the the begin and end date times for operating period for a building on a single day in UTC.
    :param lease_obligations: DataFrame of lease obligations
    :param estimation_date: date in string format
    :return: tuple (utc_operating_start, utc_operating_end) of datetimes
    """
    dow = parse(estimation_date).weekday()
    if not lease_obligations.loc[dow]["operating"]:
        return None, None

    local_operating_start_hour = lease_obligations.loc[dow][
        "local_operating_start_hour"
    ]
    local_operating_end_hour = lease_obligations.loc[dow]["local_operating_end_hour"]

    from_zone = tz.gettz(lease_obligations.loc[dow]["local_timezone"])
    local_dt = parse(estimation_date, default=datetime(2018, 1, 1, tzinfo=from_zone))
    local_operating_start = local_dt + timedelta(hours=local_operating_start_hour)
    local_operating_end = local_dt + timedelta(hours=local_operating_end_hour)

    to_zone = tz.UTC
    utc_operating_start = local_operating_start.astimezone(to_zone)
    utc_operating_end = local_operating_end.astimezone(to_zone)
    return utc_operating_start, utc_operating_end
