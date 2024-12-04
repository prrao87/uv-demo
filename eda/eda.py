"""
EDA for the movie graph dataset
"""
import polars as pl
from pathlib import Path

data_path = Path("./data")

movies_file = data_path / "movie.csv"

df = pl.read_csv(movies_file, has_header=False, new_columns=["title", "year", "summary"])

# Find all the movies that were released before 2015
movies_before_2015 = df.filter(pl.col("year") < 2015)
