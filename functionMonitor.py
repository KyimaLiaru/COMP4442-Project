from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, lit, max as spark_max
from datetime import datetime, timedelta
import os

spark = SparkSession.builder \
    .appName("Driver Monitor") \
    .getOrCreate()

# List of known driverIDs
driver_ids = [
    "zengpeng1000000", "xiexiao1000001", "hanhui1000002", "likun1000003", "shenxian1000004",
    "panxian1000005", "xiezhi1000006", "zouan1000007", "haowei1000008", "duxu1000009"
]

# Load all data for a given day
def load_data(start_time, end_time):
    date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    # add 1 day to the start and end date, as files are named for the next day
    file_name = date + timedelta(days=1)

    # set the target data file name and path, then load the data file
    target_file = file_name.strftime("detail_record_%Y_%m_%d_08_00_00")

    folder_path = "./detail-records/"
    target_file_path = os.path.join(folder_path, target_file)

    df = spark.read.option("header", "false").csv(target_file_path)

    # define the column names
    columns = [
        "driverID", "carPlateNumber", "Latitute", "Longitude", "Speed", "Direction", "siteName", "Time",
        "isRapidlySpeedup", "isRapidlySlowDown", "isNeutralSlide", "isNeutralSlideFinished", "neutralSlideTime",
        "isOverspeed", "isOverspeedFinished", "overspeedTime", "isFatigueDriving", "isHthrottleStop", "isOilLeak"
    ]

    df = df.toDF(*columns)
    df = df.withColumn("Time", to_timestamp("Time", "yyyy-MM-dd HH:mm:ss"))

    # filter the dataframe to only include records within given period of time
    df_filtered = df.filter(
        (col("Time") >= to_timestamp(lit(start_time))) &
        (col("Time") <= to_timestamp(lit(end_time)))
    )

    return df_filtered

def get_simulation_data(start_time, end_time):
    # a dictionary variable for return
    results = []

    # load the data
    df = load_data(start_time, end_time)

    # fetch the latest record of each driver within the given period of time
    for driver_id in driver_ids:
        driver_df = df.filter(col("driverID") == driver_id)

        latest_row = driver_df.orderBy(col("Time").desc()).select("Speed", "isOverspeed").limit(1).first()

        # add an empty record if the driver has not departed yet.
        if latest_row is None:
            results.append({
                "driverID": driver_id,
                "details": {
                    "speed": "0",
                    "isOverspeed": ""
                }
            })
        # add the latest record if the driver has already departed.
        else:
            results.append({
                "driverID": driver_id,
                "details": {
                    "speed": latest_row["Speed"],
                    "isOverspeed": "1" if latest_row["isOverspeed"] == 1 else ""
                }
            })

    return results
