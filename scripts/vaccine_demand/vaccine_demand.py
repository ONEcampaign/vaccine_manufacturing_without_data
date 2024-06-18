"""
This file uses Linksbridge's Vaccine Almanac dataset to produce key stats on vaccine
demand and produce the following Flourish data visualisation:
https://public.flourish.studio/visualisation/17972868/

DATA COMES FROM BEHIND A PAYWALL. DO NOT SHARE RAW DATA PUBLICLY.
"""

import pandas as pd
from scripts import config
from bblocks import add_iso_codes_column, clean_numeric_series, convert_id
import numpy as np
from scripts.tools import update_key_number


def read_vaccine_almanac_data() -> pd.DataFrame:
    """
    Reads the vaccine almanac 'Demand: Total Required Supply by Country' csv which was
    manually downloaded from Linksbridge's Vaccine Almanac. Reads in the columns with
    corrected names.

    Returns: pd.DataFrame of raw vaccine demand data
    """
    return pd.read_csv(
        config.Paths.raw_data / "demand_total_required_supply_by_country.csv"
    ).rename(
        columns={
            "Year": "year",
            "Country": "country",
            "Vaccine": "vaccine",
            "Total Required Supply": "total_required_supply",
        }
    )


def add_iso_codes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds ISO3 codes to data based on country names. Manually adds Central African
    Republic which is abbreviated to "CAR" in the original dataset. Sets Global Stockpile
    ISO3 code to 'global_stockpile'.

    Args:
        df: pd.DataFrame of vaccine demand data

    Returns: pd.DataFrame with additional column ('iso_code') for ISO3 codes.
    """

    # Standardises India entry names to 'India'. India has multiple rows for each year
    # as entries are divided by region.
    df = _convert_india_region_entries_to_india(df)

    # Change CAR to central african republic as CAR not recognised
    df.country = df.country.replace("CAR", "Central African Republic")

    # add iso columns based on country names
    df = add_iso_codes_column(
        df,
        id_column="country",
        id_type="regex",
        target_column="iso_code",
    )

    # Global stockpile is the only unmatched entry. Manually change iso_code to
    # global_stockpile.
    df["iso_code"] = np.where(
        df["country"] == "Global Stockpile", "global_stockpile", df["iso_code"]
    )

    return df


def _convert_india_region_entries_to_india(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardises India entry names to 'India'. India is the only country that has
    multiple rows for individual regions, in the format "India: Region". Later, we
    groupby country name, so we need to uniform India's data such that there is only one
    entry per year for India.

    Args:
        df: pd.DataFrame of raw vaccine almanac data.

    Returns: pd.DataFrame of raw data with 'India: Region' rows changed to 'India'.
    """

    df["country"] = np.where(
        df["country"].str.startswith("India:"), "India", df["country"]
    )

    return df


def add_continent_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds continent column based on ISO3 code. Manually sets 'global_stockpile' as
    'global_stockpile'.

    Args:
        df: pd.DataFrame of raw vaccine demand data.

    Returns: pd.DataFrame with additional 'continent' column.
    """

    manual_changes = {"global_stockpile": "global_stockpile"}

    df["continent"] = convert_id(
        df.iso_code,
        from_type="ISO3",
        to_type="Continent",
        additional_mapping=manual_changes,
    )

    return df


def vaccine_demand_by_region_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups data by year and continent, aggregating the total_required_supply column.

    Args:
        df: pd.DataFrame of vaccine demand data.

    Returns: pd.DataFrame with total_required_supply data aggregated by continent and
            year.
    """

    return (
        df.groupby(["year", "continent"], observed=True, dropna=False)[
            "total_required_supply"
        ]
        .sum()
        .reset_index()
    )


def pivot_by_continent(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivots the table to create columns for each continent, filled with the
    total_required_supply, for each year.

    Args:
        df: pd.DataFrame of vaccine demand data by continent and year.

    Returns: pd.DataFrame with year index and columns for each continent filled with
            'total_required_supply' values.
    """
    return df.pivot_table(
        index="year", columns="continent", values="total_required_supply", sort=True
    ).reset_index()


def add_all_other_regions_and_total_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates new totals columns for 'non_africa' and (global) 'Total'.

    Args:
        df: pd.DataFrame of vaccine demand data by continent and year.

    Returns: pd.DataFrame with additional columns for 'non_africa' and global 'Total'
    """

    # convert global_stockpile's NaN values to 0s to prevent error in later aggregation
    df.global_stockpile = df.global_stockpile.fillna(0)

    # Add non_africa column
    df["non_Africa"] = (
        df["America"]
        + df["Asia"]
        + df["Europe"]
        + df["Oceania"]
        + df["global_stockpile"]
    )

    # Add total column
    df["Total"] = df["Africa"] + df["non_Africa"]

    return df


def add_share_of_total_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new rows for continent's share of global total with the name
    'continent_share'.

    Args:
        df: pd.DataFrame of vaccine demand data by continent and year.

    Returns: pd.DataFrame with additional columns for each continents share of total,
            with naming format 'continent_share'.
    """

    # Create list of continent names to loop through
    continents = [
        "Africa",
        "Asia",
        "America",
        "Europe",
        "Oceania",
        "global_stockpile",
        "non_Africa",
    ]

    # Loop through each continent, calculating a new share of total column.
    for continent in continents:
        share_column = f"{continent}_share"
        df[share_column] = df[continent] / df["Total"]

    return df


def reformat_data_for_dashed_projections(
    df: pd.DataFrame, last_year_measured: int
) -> pd.DataFrame:
    """
    Add new columns for 'africa_share_measured' and 'africa_share_projected', which
    allows us to make the projected data dashed in the data visualisation.
    'africa_share_measured' contains 'Africa_share' data when year is less than or equal
     to last_year_measured. For 'africa_share_projected', 'Africa_share' data is
     included when year is greater than or equal to last_year_measured. Otherwise, both
     columns are filled with np.nan values.

    Args:
        df: pd.DataFrame of vaccine demand data by continent and year.
        last_year_measured (int): the last year with measured data.

    Returns: pd.DataFrame with additional columns for 'Africa_share_measured', which
    contains 'Africa_share' data up to the date projections start, and
    'Africa_share_projected', which shows the data after projections have started.
    """

    # Add measured data column
    df["Africa_share_measured"] = np.where(
        df["year"] <= last_year_measured, df["Africa_share"], np.nan
    )

    # Add projected data column
    df["Africa_share_projected"] = np.where(
        df["year"] >= last_year_measured, df["Africa_share"], np.nan
    )

    return df


def vaccine_dose_demand_by_country_year_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline function to transform Vaccine Almanac's 'Demand: total required supply by
    country' dataset into a flourish visualisation showing Africa's share of global
    demand between 2000 to 2030. Pipeline takes the raw data (as df argument), adds ISO3
    codes and continent names, aggregates by continent and year, and calculates
    additional columns for each continent's share of total vaccines.

    Args:
        df: pd.DataFrame of raw vaccine almanac data.

    Returns: Clean
    """

    # add iso codes and continent columns
    df = add_iso_codes(df).pipe(add_continent_column)

    # convert total_required_supply to float
    df = clean_numeric_series(data=df, series_columns="total_required_supply", to=float)

    # Aggregate 'total_required_supply' column by continent and year
    df = vaccine_demand_by_region_year(df)

    # Pivot for continent columns
    df = pivot_by_continent(df)

    # add all other regions columns
    df = add_all_other_regions_and_total_columns(df)

    # calculate share of total
    df = add_share_of_total_column(df)

    # Reformat Africa data to be split between Africa projections and measured.
    df = reformat_data_for_dashed_projections(df, last_year_measured=2024)

    return df.filter(
        items=["year", "Africa_share_measured", "Africa_share_projected"], axis=1
    )


def vaccine_demand_key_numbers(df: pd.DataFrame):
    """
    Creates a dictionary for the `africa_share_of_global_vaccine_demand_2030` indicator

    Args:
        df: pd.DataFrame of final vaccine demand data export.

    Return: Dictionary of indicator name and value.
    """

    africa_demand_2030 = df.query("year == 2030")["Africa_share_projected"].item()

    key_numbers = {
        "africa_share_of_global_vaccine_demand_2030": f"{africa_demand_2030:.1%}"
    }

    update_key_number(config.Paths.output / "key_numbers.json", key_numbers)


if __name__ == "__main__":
    DATA = read_vaccine_almanac_data()

    # Creates flourish data visualisation as pd.DataFrame
    dose_demand_by_country = vaccine_dose_demand_by_country_year_pipeline(df=DATA)

    # Exports pd.DataFrame as CSV into the output folder
    dose_demand_by_country.to_csv(
        config.Paths.output / "vaccine_demand_by_region_year.csv", index=False
    )

    # Exports the key numbers into the key_numbers.json file
    vaccine_demand_key_numbers(dose_demand_by_country)
