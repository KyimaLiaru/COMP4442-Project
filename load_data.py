from pyspark.sql import SparkSession

column_names = [
    "driverID", "carPlateNumber", "Latitude", "Longitude", "Speed", "Direction",
    "siteName", "Time", "isRapidlySpeedup", "isRapidlySlowdown", "isNeutralSlide",
    "isNeutralSlideFinished", "neutralSlideTime", "isOverspeed", "isOverspeedFinished",
    "overspeedTime", "isFatigueDriving", "isHthrottleStop", "isOilLeak"
]

def load_driver_data(folder_path="detail-records/"):
    spark = SparkSession.builder.appName("DriverDataLoad").getOrCreate()

    df = spark.read \
        .option("header", "false") \
        .option("mode", "PERMISSIVE") \
        .csv(folder_path)

    df = df.select(df.columns[:len(column_names)])  # trim to expected size
    df = df.toDF(*column_names)
    return df

# Main test entry
if __name__ == "__main__":
    df = load_driver_data("data/")  # folder containing raw files
    df.printSchema()
    df.show(5, truncate=False)