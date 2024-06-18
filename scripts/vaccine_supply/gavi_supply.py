"""
Script uses Gavi Shipment 2023 Vaccines - All Regions dataset (available here:
https://www.unicef.org/supply/media/20656/file/Gavi-shipments-2023.pdf) to calculate the
share of Gavi funded vaccines going to the six countries who are set to transition away
from Gavi support by 2030.

Our methodology goes as follows:
    - removes non-vaccine dose lines ("AD-Syringe, 0.5 ml", "AD-Syringe, 0.1 ml",
        "RUP-2.0 ml", "RUP-5.0 ml", "Safety Box, 5 Litre")
    - removes co-financing, keeping only fully GAVI funded lines
    - Aggregates remaining number of vaccine doses by country
    - Calculates share of total for each country (using the above aggregates)
    - Filters for the 6 transitioning countries ("Sao Tome & Principe", "Nigeria",
        "Kenya", "Ghana", "Djibouti", "Cote d'Ivoire")
    - Sums the 6 countries share of Gavi funded total
"""

import camelot
import pandas as pd
from bblocks import clean_numeric_series
from camelot.core import TableList
from scripts import config
from scripts.config import Paths
from scripts.tools import update_key_number

gavi_settings = {
    0: {"first_row": 4, "keep_cols": [0, 1, 2, 3, 4, 6, 8]},
    1: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    2: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    3: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    4: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    5: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    6: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    7: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    8: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    9: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    10: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    11: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    12: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 8]},
    13: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    14: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    15: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    16: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    17: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    18: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    19: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    20: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    21: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    22: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    23: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    24: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    25: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    26: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
    27: {"first_row": 0, "keep_cols": [0, 1, 2, 3, 4, 6, 7]},
}


def load_gavi_data(page_settings: dict) -> pd.DataFrame:
    """
    Scrapes the data from the Gavi Shipments 2023 Vaccines - All Regions PDF tables
    (available here:
    https://www.unicef.org/supply/media/20656/file/Gavi-shipments-2023.pdf). Reads the
    tables into a list of tables. 'gavi_settings' dictionary then identifies the
    relevant rows and columns that form each table (excluding 'planned delivery month'
    which was regularly blanked and therefore not scraped), before stacking the tables
    from each page into one pd.DataFrame. Function cleans final DataFrame to reflect
    original table in the PDF.

    Args:
        page_settings (dict): Dictionary describing the location of relevant data in
                              scraped tables.

    Returns: pd.DataFrame of Gavi Shipments 2023 Vaccines - All Regions dataset.
    """

    # Read the tables and stores as a list of tables.
    tables = read_tables()

    # Concatenates each table from the tables list into a dataframe. Filters each table
    # for relevant data.
    data = concatenate_tables(raw_data=tables, page_settings=page_settings)

    # Clean table columns (merging columns which contain the same data for different
    # countries).
    data = clean_numeric_series(data, series_columns=[7, 8], to=float)
    data["9"] = data[7].fillna(0) + data[8].fillna(0)
    data = data.drop(labels=[7, 8], axis=1)

    # Rename columns to match original PDFs
    data = set_column_names(data)

    return data


def read_tables():
    """
    Reads PDF tables and stores them as a list of tables.

    Returns: List of tables containing data from the Gavi Shipments 2023 Vaccines - All
    Regions report.
    """
    filepath = str(config.Paths.raw_data / "Gavi-shipments-2023.pdf")
    return camelot.read_pdf(filepath, pages="1-28", flavor="stream")


def concatenate_tables(
    raw_data: TableList,
    page_settings: dict,
) -> pd.DataFrame:
    """stacks tables from multiple pages of a pdf into a single dataframe. For each
    page, the tables are read, cleaned, and stacked under the page from the previous
    year's pdf.

    Args:
        raw_data (TableList): the list of tables scraped using the read_table function
        page_settings (dict): a dictionary with the required pdf characteristics to
                              determine how to clean the raw_data.

    Returns: pd.DataFrame containing all data from the PDF.
    """

    # Create an empty dataframe to store all the tables
    final_df = pd.DataFrame()

    # Loop through each page, locating the data tables and keeping relevant data
    for page, settings in page_settings.items():
        df = raw_data[page].df
        df = _filter_rows_columns(
            df=df,
            first_row=settings["first_row"],
            keep_cols=settings["keep_cols"],
        )

        # Add each table to final pd.DataFrame
        final_df = pd.concat([final_df, df], ignore_index=False)

    return final_df


def _filter_rows_columns(df: pd.DataFrame, first_row: int, keep_cols: list[int]):
    """
    Takes the pdf tables in DataFrame form and removes (1) the top columns down to
    (but excluding) the specified first row, and keeps only the specified columns.
    Args:
        df (pd.DataFrame): DataFrame containing the PDF tables.
        first_row (int): Row index of the first relevant row.
        keep_cols (int): Column indices to keep.

    Returns: pd.DataFrame of relevant rows and columns
    """
    return df.iloc[first_row:, keep_cols]


def set_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sets column names to match the original PDF.

    Args:
        df: pd.DataFrame of 2023 Gavi vaccine shipments data

    Returns: pd.DataFrame with standardised column names
    """

    df.columns = [
        "country",
        "product",
        "gavi_approval_year",
        "gavi_business_key",
        "gavi_non_gavi",
        "delivery_date",
        "total_quantity_in_doses",
    ]

    return df


def remove_non_vaccines(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes lines in 'Gavi Shipments 2023 Vaccines - All Regions' dataset that are not
    vaccines.

    Args:
        df: pd.DataFrame of 2023 Gavi vaccine shipments data

    Returns: pd.DataFrame of 'Gavi Shipments 2023 Vaccines' data excluding non-vaccine
            data
    """

    # List of non-vaccine lines in dataset
    non_vaccines = [
        "AD-Syringe, 0.5 ml",
        "AD-Syringe, 0.1 ml",
        "RUP-2.0 ml",
        "RUP-5.0 ml",
        "Safety Box, 5 Litre",
    ]

    return df.loc[lambda d: ~d["product"].isin(non_vaccines)]


def add_share_of_total_column(df: pd.DataFrame) -> pd.DataFrame:

    # Calculate total
    total = df["total_quantity_in_doses"].sum()

    # Add share of total column
    df["total_quantity_in_doses_share_of_total"] = df["total_quantity_in_doses"] / total

    return df


def filter_for_six_transitioning_countries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters for the six African countries anticipated to transition away from Gavi
    support over 2024 to 2030. See Figure 9 below for list:
    https://www.gavi.org/sites/default/files/investing/funding/resource-mobilisation/MTR23_Report_FULL_eng.pdf

    Args:
        df: pd.DataFrame of 2023 Gavi vaccine shipments data

    Returns: pd.DataFrame of gavi vaccines supplied to the six African countries
             anticipated to move away from Gavi support by 2030
    """

    # List of countries transitioning away from Gavi support
    countries = [
        "Sao Tome & Principe",
        "Nigeria",
        "Kenya",
        "Ghana",
        "Djibouti",
        "Cote d'Ivoire",
    ]

    return df.loc[lambda d: d.country.isin(countries)]


def share_of_gavi_vaccine_supply_to_six_transitioning_countries_pipeline(
    data: pd.DataFrame,
):
    """
    Pipeline function to calculate the share of gavi vaccines that go to the six
    transitioning countries. Function removes non vaccine lines, filters for gavi funded
    vaccines, aggregates by country, and calculates the share of total, before filtering
    for the six countries that are transitioning away from vaccine support. Outputs
    number in the key_numbers.json as
    `share_of_gavi_vaccine_supply_for_six_transitioning_countries`.

    Args:
        data: pd.DataFrame of cleaned 2023 Gavi vaccine shipments data

    Returns: share_of_gavi_vaccine_supply_for_six_transitioning_countries key number
                and merges it with other key numbers in key_numbers.json
    """

    # Filter to remove non-vaccine transfers
    data = remove_non_vaccines(data)

    # Filter for fully gavi funded data
    data = data.loc[lambda d: d.gavi_non_gavi == "GAVI"]

    # Sum by country
    data = data.groupby(["country"])["total_quantity_in_doses"].sum().reset_index()

    # Calculate share of total vaccines by country
    data = add_share_of_total_column(data)

    # Filter then sum for 6 transitioning countries' share of gavi supply
    transitioning_countries = filter_for_six_transitioning_countries(data)

    # Isolate key figure, setting as indicator
    return transitioning_countries["total_quantity_in_doses_share_of_total"].sum()


def gavi_supply_key_number(key_number: float):
    key_numbers = {
        "share_of_gavi_vaccine_supply_for_six_transitioning_countries": f"{key_number:.1%}"
    }

    update_key_number(config.Paths.output / "key_numbers.json", key_numbers)


if __name__ == "__main__":
    # Read PDF into pd.DataFrame
    DATA = load_gavi_data(page_settings=gavi_settings)

    # Save raw data to output folder
    DATA.to_excel(Paths.output / "gavi_vaccine_supply.xlsx", index=False)

    # Calculate key number
    gavi_supply_share = (
        share_of_gavi_vaccine_supply_to_six_transitioning_countries_pipeline(DATA)
    )

    # Add gavi_supply_share to key_number.json file
    gavi_supply_key_number(gavi_supply_share)
