# **Cortex Data Science Homework Problem**

## **Background**

Cortex is a rapidly growing technology startup in the Commercial Real Estate space.  We provide software that enables building operators, including the team at the Empire State Building, to run their buildings with significantly more precision. This is creating substantial financial savings, while also having a significant sustainability impact. Cortex does this by providing an application layer on top of highly underutilized data "pipes" (Building Management Systems (BMS), meters, etc.), which makes sense of thousands of data points, makes that information available anywhere, and gives proactive recommendations for decisions that have to be made daily.

One of these recommendations is the start time to turn on the building HVAC systems on operating days. To save energy, most commercial building HVAC systems are turned off after business hours end. The building cools down (or heats up) during the course of the night and on weekends. Early each morning, before business hours begin again, the building HVAC systems must be turned on so that the building's internal temperature is comfortable for its tenants. Cortex's goal is to recommend this HVAC start time as accurately as possible. We don't want to recommend a start time that is too early — then the building will be "at temp" too early and we will have wasted energy. At the same time, we don't want to recommend a start time that is too late — then the building is still too cold (or too hot) when people are coming in to work.

This homework problem deals with a sub-problem of the larger start time recommendation problem. One of the key requirements of solving the start time recommendation problem is having a clean labelled historical data set. We want to know on any given historical day two things:

1. When was the buildings HVAC systems started in the morning? This is called the **HVAC start time**.
2. When did the building reach the desired temperature in the morning? This is called the **lease obligation satisfied at time**.

Unfortunately, we do not get this labelled data coming from the BMS systems. We only get raw time series. We have to label the data ourselves. We want you to come up with an algorithm to solve the second problem: **estimating the lease obligation satisfied at time**.

This problem sounds simple, but it is not. With a single internal temperature sensor, like in a house, the problem is easier. The heat (or AC) turns on in the middle of the night and you can see when the internal temperature gets within the bounds of the desired operating temperature, e.g. between 70 and 75 degrees. This time is is when the lease obligation was satisfied. The figure below shows such an example.  Looking at just this single sensor we would say that the building reached its target temperature at 12:00 UTC.

![Single Sensor Graph](https://user-images.githubusercontent.com/25503/43617345-7cd89438-968f-11e8-99ec-a5d0742ab0f6.png)

The situation is far more complicated in large commercial buildings because of various factors:

* There are multiple indoor temperature sensors. Is the building "at target temperature" when all of the sensors are within a the target range? Do we only have to wait for some of the sensors?
* Some internal temperature sensors may not be relevant, e.g. they are measuring a space that may not be under direct building HVAC control, like a server room, a sub-basement, etc. We don't know which of these sensors are relevant ahead of time, we have to make this determination ourselves.
* Some internal temperature sensors may be broken, e.g. they are not measuring the temperature appropriately or are providing invalid values, e.g. -10 degrees. 
* Some buildings, like large skyscrapers, have thousands of internal temperature sensors. Some buildings, only have a handful.

For example, let's look at a building with over 400 internal temperature sensors. The lease obligation for this building in the wintertime is to be between 70 and 75 degrees during operating hours. Looking at the time series values for just 10 internal temperature sensors, when would you say the lease obligation was satisfied?  Some zones get to temperature early, some later, some not at all. 

![Multiple Sensor Graph](https://user-images.githubusercontent.com/25503/43617344-7cc8b568-968f-11e8-9c80-f4c18006639f.png)

## **Problem**

We have delivered a dataset of relevant data for four buildings. We want you to come up with an algorithm that estimates the lease obligation satisfied at time for all of the historical operating days for these four buildings. We want you to deliver this algorithm as Python code. In addition, we would like you to make a short presentation about your approach, what you learned about the data, and a roadmap for future improvements/experiments.

For your convenience we have already created a framework for you to write your code in.  The framework should greatly accelerate your ability to focus on the algorithm instead of the surrounding infrastructure for testing and generating the required CSV outputs. The framework contains three top level directories:

1. `\src`. This contains all the algorithm source code. It is organized into two Python modules. One for data access, called `data_loading.py`, and one for the algorithm code, called `lease_satisfied_estimator.py`. Most of your code should be written in this directory.

2. `\tests`. This contains all the unit tests. Your unit tests should be written here. In addition, you will be running the tests that are already here to check that you implemented the data access appropriately.

3. `\scripts`. This contains a script called `run_historical_estimation.py`. This scripts calls your algorithm and uses it to generate a set of historical predictions for all the buildings.  You should be using it to generate the required CSVs for this homework.

As it stands, there are three places you must write your own code.

1. You must implement the `get_internal_temps()` method in `\src\data_loading.py`.  This is the main function that accesses the database and reshapes the data into a reasonable format for downstream processing. There are tests already written for this function in the `\tests\test_data_loading.py` module.  If you implement this function correctly, the unit tests should pass. A good implementation should us a combination of SQL on the database and some Pandas data munging.  The resulting data frame should look as follows:

|Measurement Time|Sensor Data|Sensor Data|Sensor Data|Sensor Data|Sensor Data|
|---|---|---|---|---|---|
||17525|17526|17614|17615|...|
|2018-02-04 00:00:00|68.699997|62.599998|68.599998|67.300003|...|
|2018-02-04 00:15:00|68.699997|62.599998|68.599998|68.300003|...|
|2018-02-04 00:30:00|68.500000|62.500000|68.800003|69.300003|...|
|2018-02-04 00:45:00|68.300003|62.500000|69.000000|67.199997|...|
|2018-02-04 01:00:00|68.300003|62.400002|67.199997|68.300003|...|
|...|...|...|...|...|...|

Where the `measured_at` time is used as each row's index and points to the `measurement` value for each individual sensor at that time.

2. You must implement a Python class that conforms to the interface specified by the abstract base class `LeaseSatisfiedTimeEstimator` in `\src\lease_satisfied_estimator.py`.  We have an example in that same file for your reference.  Of course, you can have many other helper classes and modules under the hood.

3. You must implement good unit tests for your algorithm in `\tests\test_lease_satisfied_estimator.py`.  There are example tests and stubs that you may find useful in that directory already. Note that we use pytest to run the unit tests. You can run them by typing `python -m pytest tests`. You can call specific tests as well. See more in the documentation for pytest [here](https://docs.pytest.org/en/latest/).

If you have written your code appropriately, you should be able to add your algorithm class to `\scripts\run_historical_estimation.py` and run the script:

```
python run_historical_estimation.py </path/to/config.yml>
```

The script should output separate CSVs with estimates for the lease obligation satisfied at time for all the historical operating dates and buildings specified in the `config.yml` file.  An example config file is in included in the `\scripts` directory. It already includes all of the buildings in the database and the entire range of dates we expect historical estimations for.  Also, as it is written, `run_historical_estimation.py` generates all of the required columns for this homework assignment. You can add additional columns of metadata if you wish.  The files for each building should look like:

|date|building_id|operating|lease_satisfied_time
|---|---|---|---|
|2018-02-04|8|False|NaN|
|2018-02-05|8|True|2018-02-05 06:45:00|
|2018-02-06|8|True|2018-02-06 08:15:00|
|2018-02-07|8|True|2018-02-07 07:00:00|

Note that just delivering a Jupyter notebook is *not* what we are looking for. We would like you to write your algorithm inside the production infrastructure that we have provided. Of course you can use Jupyter notebooks to test your algorithm, make visualizations, and write scratch code. Please include these in your pull request as well if you believe that they will help us better assess your abilities.

So, to be clear, there are three expected deliverables for this homework assignment:

1. A Pull Request against this GitHub repository that contains your fully coded solution to this problem.
2. A set of CSVs with estimated lease obligation start times for all the buildings between 1/1/2018 and 7/1/2018.
3. A presentation about your approach, learnings, any relevant visualizations, and a roadmap for future improvements.

We expect candidates to spend about _8 hours_ on this project. You can spend longer if you want, but it is not expected of you. We do not expect you to come up with the best possible algorithm in that time nor solve all the corner cases in the data, rather we would like you explore the data, come up with a proposed plan of work, code up a reasonable "Version 1" algorithm (that may ignore many of the corner cases), and have a game plan of how you would like to improve the algorithm based on what you have learned. 

## **Assessment Criteria**

Your performance on this homework problem will be judged on four factors:

1. **Algorithmic Creativity.** A big part of being a good Machine Learning (ML) engineer is coming up with creative algorithms that balance accuracy with complexity. To that end, we'll assess your solution by asking questions like the ones below:
    1. How accurate is your algorithm?
    2. How complex is your algorithm?
    3. How did you choose to assess error?

2. **Organizing Your Work.** ML engineering is an experimental science. A big part of being a good ML engineer is the ability to sequence experiments and effort, learn from it, and iterate toward a better solution. To that end, we'll assess your approach by asking questions like the ones below:
    1. How organized is your data science thinking?
    2. How did you sequence/roadmap your work? Did you start with a simple baseline and iterate from there?
    3. What experiments would you do next?

3. **Software Code Quality.** In the end, ML engineers have to deploy software to production. A good ML engineer is as much a software engineer as they are an algorithm developer. You must be able to write code that is maintainable, testable, modular, well organized, and well documented. To that end, we'll assess your source code by asking questions like the ones below:
    1. How modular is your code? e.g. Is it easy to replace the models in your code?
    2. How maintainable is your code? e.g. Is it easy to understand and reason about? Is it well documented? Does it use good naming and style conventions?
    3. Are you using standard libraries where possible? e.g. NumPy, pandas, scikit-learn, SciPy, etc.

4. **Communication.** ML engineers have to communicate with their peers all the time. This includes other ML experts, software engineers, and business stakeholders. This is a critical element of success. To that end, we'll assess your presentation by asking questions like:
    1. How clearly are you able to articulate your ideas?
    2. Do you ask clarifying questions when you need to? 
    3. Can you defend your ideas when scrutinized?
    4. Can you make meaningful visualizations of the data?
    5. Can you explain technical concepts to non-technical stakeholders to allow for business decisions to be made?

## **System Requirements and Initial Project Setup**

In order to complete this homework assignment you will need to have Python Version 3+ installed on your system. For your convenience, we host the dataset in an Internet accessible PostgreSQL instance.  You should have received `read-only` credentials to this database when this homework was initially assigned.  You are more than welcome to use `pg_dump` and `pg_restore` to download and load this dataset onto your local machine if you would like.

To get started with this homework assignment, follow these steps:

1. Fork this repository to your GitHub account.
2. Clone the repository to your local machine.
3. Set the `HW_DATABASE_URL` enviornment variable to the URL String provided along with this homework assignment.
4. Run `pip install -r requirements.txt` to install this project's dependencies.
5. Ensure your environment is properly configured by running `python -m pytest tests`. This should run the unit tests that should fail with a `NotImplementedError` because you have not written your solution yet.

## **About the Data**

There are three tables in the database. A quick primer on the tables:

*   `buildings` - holds simple profile information for a building and most importantly for this exercise its primary key (`id`).  The primary key can be used to tie all other data together.
*   `building_sensor_configs` - holds sensor related information.  Note that there can be dozens of different sensor types , but for this exercise we've limited the data to Floor Temperature sensors only.  Additionally, we sometimes know when sensors are not providing good readings.  In this case we ignore these sensors by setting the `ignore` column's flag to true.  Sensors are associated with a particular building through the `building_id` foreign key.
*   `floor_temperature_measurements` - holds time series measurement values for sensors.  Measurements are associated with a particular sensor through the `building_sensor_config_id` foreign key.  Note that sometimes even good sensors give bad measurement values.  We mark these bad measurement readings by setting the `bad_data` column flag to true.

## Questions

You should have been invited to private channel called `<your name>-interview-room` in the "Cortex Interview" Slack Workspace.  If you have any questions about this homework assignment, please feel free to message `@sprad` in this channel.

Good Luck!!!
