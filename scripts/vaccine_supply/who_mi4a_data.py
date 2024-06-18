import numpy as np
import pandas as pd

from scripts import config
from scripts.tools import update_key_number


def import_who_data() -> pd.DataFrame:
    """
    Imports the excel spreadsheet shared by WHO. Contains 4 tables which are not
    formatted for use in python. Needs cleaning below in `get_data_table`.

    Returns: pd.DataFrame of raw data.
    """
    return pd.read_excel(
        config.Paths.raw_data / "GVMR 2023 - ONE Campaign May 2024_vShared.xlsx",
        sheet_name="FOR ONE Campaign",
    )


def get_data_table(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Selects the relevant table from WHO excel spreadsheet. Table locations defined in
    table_location dictionary.

    Args:
        df: pd.DataFrame of raw data from WHO excel spreadsheet
        table_name: Table in the spreadsheet to be kept. All others removed.

    Returns: pd.DataFrame of selected table. If invalid table name provided, returns
             error.
    """

    # Dictionary to store dimensions / location of tables within spreadsheet.
    table_locations = {
        "with_covid_who_region": {"rows": slice(10, 17), "columns": slice(2, 6)},
        "with_covid_continent": {"rows": slice(18, 25), "columns": slice(2, 6)},
        "without_covid_who_region": {"rows": slice(29, 36), "columns": slice(2, 6)},
        "without_covid_continent": {"rows": slice(37, 44), "columns": slice(2, 6)},
    }

    # Sets dimensions from table_locations dictionary
    loc = table_locations.get(table_name)

    # Return the table defined above. If invalid table defined, return an error.
    if loc:
        return df.iloc[loc["rows"], loc["columns"]]
    else:
        raise ValueError(f"Table name '{table_name}' not found in table locations.")


def set_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Set the column names. All of the tables within table_locations dictionary above have
    the same column name.

    Args:
        df: pd.DataFrame with unnamed columned.

    Returns: pd.DataFrame with standardised column names.
    """
    df.columns = [
        "manufacturer_hq",
        "vaccines_to_world",
        "vaccines_to_africa",
        "share_of_production_to_africa",
    ]

    return df


def add_share_of_global_vaccine_supply_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'share_of_global_vaccine_supply' column by first isolating the total for
    2022 as `total_vaccines_to_world` numpy array, and then dividing every value in
    `vaccines_to_world` column by that total.

    Args:
        df: pd.DataFrame

    Returns: pd.DataFrame with additional column called `share_of_global_vaccine_supply'.
    """
    # Extract the 'TOTAL' value in the 'vaccines_to_africa' column
    total_vaccines_to_world = df[df["manufacturer_hq"] == "TOTAL"][
        "vaccines_to_world"
    ].values[0]

    # Add a new column that divides the 'vaccines_to_africa' by the total value (in %)
    df["share_of_global_vaccine_supply"] = (
        df["vaccines_to_world"] * 100 / total_vaccines_to_world
    )

    return df


def reorder_rows_for_data_vis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder rows to put Africa first for the data visualisation. The others were
    ordered in size value.
    Args:
        df: pd.DataFrame

    Returns: pd.DataFrame with Africa as first row, then remaining continents in
    descending value order
    """

    # List of continent names as strings in desired order
    desired_order = [
        "Africa",
        "Asia",
        "North America",
        "Europe",
        "South America",
        "Oceania",
    ]

    # Create the reordered DataFrame
    df_reordered = df.set_index("manufacturer_hq").reindex(desired_order).reset_index()

    return df_reordered


def add_new_columns_for_flourish(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds the additional columns required to have Africa as a seperate colour on Flourish.
    Creates 'africa' column which contains only the data for Africa. Creates 'non_africa'
    column for data to the other continents. Uses'share_of_global_vaccine_supply' data.

    Args:
        df: pd.DataFrame

    Returns: pd.DataFrame with additional columns containing Africa data ('africa') and
    data for other continents ('non_africa')
    """

    df["africa"] = np.where(
        df["manufacturer_hq"] == "Africa", df["share_of_global_vaccine_supply"], 0
    )
    df["non_africa"] = np.where(
        df["manufacturer_hq"] != "Africa", df["share_of_global_vaccine_supply"], 0
    )

    return df


def vaccine_supply_pipeline(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Pipeline function to reshape data from the WHO excel spreadsheet into data for the
    Flourish data visualisation. Function takes the raw data, cleans it, and conducts
    the analysis for the data visualisation.
    Args:
        df: pd.DataFrame of raw data from WHO spreadsheet.
        table_name (str): the required Table from the who spreadsheet.

    Returns: pd.DataFrame with Africa as first row, then remaining continents in
    descending value order
    """

    # Load correct table from WHO xlsx
    vaccine_supply = get_data_table(df=df, table_name=table_name).pipe(set_column_names)

    # Add add_share_of_africa_vaccine_supply_column
    vaccine_supply = add_share_of_global_vaccine_supply_column(vaccine_supply).loc[
        lambda d: d.manufacturer_hq != "TOTAL"
    ]

    # Reorder/reshape for flourish
    vaccine_supply = reorder_rows_for_data_vis(vaccine_supply).pipe(
        add_new_columns_for_flourish
    )

    return vaccine_supply


def supply_key_numbers(df: pd.DataFrame):
    """Create a dictionary of dictionaries for each indicator"""

    df = df.set_index("manufacturer_hq").astype(float).reset_index()

    afr_to_world = df.query("manufacturer_hq == 'Africa'")["vaccines_to_world"].sum()
    asia_to_world = df.query("manufacturer_hq == 'Asia'")["vaccines_to_world"].sum()
    na_to_world = df.query("manufacturer_hq == 'North America'")[
        "vaccines_to_world"
    ].sum()
    eur_to_world = df.query("manufacturer_hq == 'Europe'")["vaccines_to_world"].sum()
    afr_prod_share = afr_to_world / df.vaccines_to_world.sum()
    asia_prod_share = asia_to_world / df.vaccines_to_world.sum()
    na_prod_share = na_to_world / df.vaccines_to_world.sum()
    eur_prod_share = eur_to_world / df.vaccines_to_world.sum()

    world_to_afr = df.vaccines_to_africa.sum() / df.vaccines_to_world.sum()

    afr_imported = (
        df.query("manufacturer_hq != 'Africa'").vaccines_to_africa.sum()
        / df.vaccines_to_africa.sum()
    )

    key_numbers = {
        "africa_vaccine_production_value": f"{afr_to_world / 1e6:,.1f} million",
        "africa_vaccine_production_share": f"{afr_prod_share:.2%}",
        "asia_vaccine_production_share": f"{asia_prod_share:.1%}",
        "na_vaccine_production_share": f"{na_prod_share:.1%}",
        "eur_vaccine_production_share": f"{eur_prod_share:.1%}",
        "fold_increase_required_to_target": f"{1500 / (afr_to_world / 1e6):,.0f}",
        "share_of_global_vaccines_delivered_to_africa": f"{world_to_afr:.1%}",
        "share_of_vaccines_to_africa_imported": f"{afr_imported:.1%}",
        "share_of_vaccines_to_africa_produced_by_africa": f"{1 - afr_imported:.1%}",
    }

    # Update the key numbers
    update_key_number(config.Paths.output / "key_numbers.json", key_numbers)


if __name__ == "__main__":
    DATA = import_who_data()
    TABLE_NAME = "with_covid_continent"

    # Creates Flourish data visualisation as pd.DataFrame
    stacked_bar_chart = vaccine_supply_pipeline(df=DATA, table_name=TABLE_NAME)

    # Export the key numbers
    supply_key_numbers(stacked_bar_chart)

    # Exports above pd.DataFrame as CSV into the output folder
    stacked_bar_chart.to_csv(
        config.Paths.output / "african_vaccine_supply.csv", index=False
    )
