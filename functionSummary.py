from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import col, to_timestamp, lit, sum as spark_sum
from datetime import datetime, timedelta
import os

spark = SparkSession.builder \
    .appName("Driver Summary") \
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

summary_features = [
    "isRapidlySpeedup",
    "isRapidlySlowDown",
    "isNeutralSlideFinished",
    "isOverspeedFinished",
    "isFatigueDriving",
    "isHthrottleStop",
    "isOilLeak"
]

# Load all data for given time period for a specific driverID.
def load_data(driver_id, start_time, end_time):
    start_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    # add 1 day to the start and end date, as files are named for the next day
    start_name = start_date + timedelta(days=1)
    end_name = end_date + timedelta(days=1)

    # put the target record filename to load in a list
    target_dataset = []
    temp = start_name
    while temp <= end_name:
        target_dataset.append(temp.strftime("detail_record_%Y_%m_%d_08_00_00"))
        temp += timedelta(days=1)

    # load all record from the files in the list
    folder_path = "./detail-records/"
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f in target_dataset]

    if not files:
        print("No matching files")
        return None

    df = spark.read.option("header", "false").schema(schema).csv(files)

    # define the column names
    columns = [
        "driverID", "carPlateNumber", "Latitute", "Longitude", "Speed", "Direction", "siteName", "Time",
        "isRapidlySpeedup", "isRapidlySlowDown", "isNeutralSlide", "isNeutralSlideFinished", "neutralSlideTime",
        "isOverspeed", "isOverspeedFinished", "overspeedTime", "isFatigueDriving", "isHthrottleStop", "isOilLeak", "etc"
    ]

    df = df.toDF(*columns)
    df = df.withColumn("Time", to_timestamp("Time", "yyyy-MM-dd HH:mm:ss"))

    # filter the dataset to only contain the required information
    df_filtered = df.filter(
        (col("driverID") == driver_id) &
        (col("Time") >= to_timestamp(lit(start_time))) &
        (col("Time") <= to_timestamp(lit(end_time)))
    )

    return df_filtered

# Convert seconds to "minutes:seconds" format
def format_seconds(seconds):
    if seconds is None or seconds == 0:
        return "0:00"
    result_minutes = seconds // 60
    result_seconds = seconds % 60
    return f"{int(result_minutes)}:{int(result_seconds):02}"


def get_driver_summary(driver_id, start_time, end_time):
    # a dictionary variable for return
    result_dict = {
        "driverID": driver_id
    }

    # load the data
    df = load_data(driver_id, start_time, end_time)

    # summarize the counts of bad behaviors and save to the dictionary variable
    for feature in summary_features:
        result_dict[feature] = df.filter(col(feature) == "1").count()

    # sum the duration of total Neutral Slide time and Overspeed time
    df_duration = df.withColumn("neutralSlideTime", col("neutralSlideTime").cast("int")) \
                    .withColumn("overspeedTime", col("overspeedTime").cast("int"))

    neutral_slide_seconds = df_duration.agg(spark_sum("neutralSlideTime")).first()[0] or 0
    overspeed_seconds = df_duration.agg(spark_sum("overspeedTime")).first()[0] or 0

    # save the total duration time as formatted string to the dictionary variable
    result_dict["neutralSlideDuration"] = format_seconds(neutral_slide_seconds)
    result_dict["overspeedDuration"] = format_seconds(overspeed_seconds)

    return result_dict