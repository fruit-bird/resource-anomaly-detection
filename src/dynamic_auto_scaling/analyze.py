import os
import pandas as pd
from adtk.data import validate_series
from adtk.visualization import plot
import matplotlib.pyplot as plt
import seaborn as sns
from adtk.detector import (
    SeasonalAD,
    QuantileAD,
    InterQuartileRangeAD,
    GeneralizedESDTestAD,
)
from dotenv import load_dotenv

AVAILABLE_METRICS = [
    "cpu_percent",
    "memory_percent",
    "disk_usage",
    "bytes_sent",
    "bytes_recv",
]

AVAILABLE_MODELS = [
    "SeasonalAD",
    "QuantileAD",
    "InterQuartileRangeAD",
    "GeneralizedESDTestAD",
]


def analyze(metric_to_analyze: str, model_to_analyze: str):
    if (
        metric_to_analyze not in AVAILABLE_METRICS
        or model_to_analyze not in AVAILABLE_MODELS
    ):
        return

    load_dotenv()
    uri = os.environ.get("DB_URL")

    df = pd.read_sql_table("metrics", uri, parse_dates=["time"])
    df["time"] = pd.date_range(start=df["time"].min(), periods=len(df), freq="2s")
    df.set_index("time", inplace=True)
    df = validate_series(df)

    anomaly_detector = globals()[model_to_analyze]()
    anomalies = anomaly_detector.fit_detect(df[metric_to_analyze])

    return df, anomalies
