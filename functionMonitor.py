from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import col, to_timestamp, lit, max as spark_max
from datetime import datetime, timedelta
import os

# Global cache variables
df = None
df_date = None
driver_states = []

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Driver Monitor") \
    .getOrCreate()

# Define columns to expect from dataset files
schema = StructType([
    StructField("driverID", StringType(), True),
    StructField("carPlateNumber", StringType(), True),
    StructField("Latitute", StringType(), True),
    StructField("Longitude", StringType(), True),
    StructField("Speed", StringType(), True),
    StructField("Direction", StringType(), True),
    StructField("siteName", StringType(), True),
    StructField("Time", StringType(), True),
    StructField("isRapidlySpeedup", StringType(), True),
    StructField("isRapidlySlowDown", StringType(), True),
    StructField("isNeutralSlide", StringType(), True),
    StructField("isNeutralSlideFinished", StringType(), True),
    StructField("neutralSlideTime", StringType(), True),
    StructField("isOverspeed", StringType(), True),
    StructField("isOverspeedFinished", StringType(), True),
    StructField("overspeedTime", StringType(), True),
    StructField("isFatigueDriving", StringType(), True),
    StructField("isHthrottleStop", StringType(), True),
    StructField("isOilLeak", StringType(), True),
    StructField("etc", StringType(), True)
])

# List of known driverIDs
driver_ids = [
    "zengpeng1000000", "xiexiao1000001", "hanhui1000002", "likun1000003", "shenxian1000004",
    "panxian1000005", "xiezhi1000006", "zouan1000007", "haowei1000008", "duxu1000009"
]

# Initialize the speed dictionary for all drivers
for driver_id in driver_ids:
    driver_states.append({
        "driverID": driver_id,
        "details": {
            "speed": "0",
            "isOverspeed": ""
        }
    })

# Reset the speed dictionary for all drivers
def reset_driver_status():
    for idx, driver_id in enumerate(driver_ids):
        driver_states[idx]["details"]["speed"] = "0"
        driver_states[idx]["details"]["isOverspeed"] = ""

# Check cache and load all data for a given day
def load_data(start_time):
    # load the cached dataset file
    global df
    global df_date

    date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    # add 1 day to the start and end date, as files are named for the next day
    file_name = date + timedelta(days=1)

    if df is None or df_date != file_name.date():
        # set the target dataset file name and path, then load the dataset file
        target_file = file_name.strftime("detail_record_%Y_%m_%d_08_00_00")
        folder_path = "./detail-records/"
        target_file_path = os.path.join(folder_path, target_file)

        df = spark.read.option("header", "false").schema(schema).csv(target_file_path)

        # define the column names
        columns = [
            "driverID", "carPlateNumber", "Latitute", "Longitude", "Speed", "Direction", "siteName", "Time",
            "isRapidlySpeedup", "isRapidlySlowDown", "isNeutralSlide", "isNeutralSlideFinished", "neutralSlideTime",
            "isOverspeed", "isOverspeedFinished", "overspeedTime", "isFatigueDriving", "isHthrottleStop", "isOilLeak", "etc"
        ]

        df = df.toDF(*columns)
        df = df.withColumn("Time", to_timestamp("Time", "yyyy-MM-dd HH:mm:ss"))

        # check variable for caching
        df_date = file_name.date()

    return df

def get_monitor_data(start_time, end_time, df):
    # filter the df to only have records within the given period of time.
    df_filtered = df.filter(
        (col("Time") >= to_timestamp(lit(start_time))) &
        (col("Time") <= to_timestamp(lit(end_time)))
    )

    # update "speed" and "isOverspeed" for each driver
    for idx, driver_id in enumerate(driver_ids):
        # filter dataset by driverID and sort them in ascending order
        driver_df = df_filtered.filter(col("driverID") == driver_id)
        sorted_df = driver_df.orderBy(col("Time").asc())
        rows = sorted_df.select("Time", "Speed", "isOverspeed", "isOverspeedFinished").collect()

        # process data in order
        for row in rows:
            # if driver starts overspeeding
            if row["isOverspeed"] == "1":
                driver_states[idx]["details"]["isOverspeed"] = "1"
            # if driver stops overspeeding
            if row["isOverspeedFinished"] == "1":
                driver_states[idx]["details"]["isOverspeed"] = ""

            # always keep the latest speed
            driver_states[idx]["details"]["speed"] = row["Speed"]

    return driver_states
