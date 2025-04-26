from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import col, to_timestamp, lit, max as spark_max
from datetime import datetime, timedelta
import os

df = None
df_date = None

spark = SparkSession.builder \
    .appName("Driver Monitor") \
    .getOrCreate()

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

# Load all data for a given day
def load_data(start_time):
    global df
    global df_date

    date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    # add 1 day to the start and end date, as files are named for the next day
    file_name = date + timedelta(days=1)

    if df is None or df_date != file_name.date():
        print("Loading new dataset file.  .. ")
        # set the target data file name and path, then load the data file
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

        df_date = file_name.date()

    return df

def get_monitor_data(start_time, end_time, df):
    # filter the df to only have records within the given period of time.
    df_filtered = df.filter(
        (col("Time") >= to_timestamp(lit(start_time))) &
        (col("Time") <= to_timestamp(lit(end_time)))
    )

    # a dictionary variable for return
    results = []

    # fetch the latest record of each driver within the given period of time
    for driver_id in driver_ids:
        driver_df = df_filtered.filter(col("driverID") == driver_id)

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
                    "isOverspeed": latest_row["isOverspeed"] or ""
                }
            })

    return results
