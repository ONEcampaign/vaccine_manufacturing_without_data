import pandas as pd
from scripts.common import manufacturer_to_country, who_regional_mapping
from bblocks import add_iso_codes_column

from scripts import config


def read_excel(file_name: str, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(config.Paths.raw_data / file_name, sheet_name=sheet_name)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns = {
        "Region": "region",
        "Income Group": "income_group",
        "Gavi/Non-Gavi": "gavi_non_gavi",
        "Country alias 2022": "country",
        "Year": "year",
        "Vaccine": "vaccine",
        "Manufacturer": "manufacturer",
        "Presentation": "presentation",
        "Dosage Number": "dosage_number",
        "Annual Number of Doses": "annual_doses",
        "WHO PQ": "who_pq",
        "CommercialName": "commerical_name",
        "Procurement Mechanism": "procurement_mechanism",
        "ContractLength": "contract_length",
        "Price per Dose in USD": "price_per_dose_usd",
        "INCOTerm": "incoterm",
        "VATPercent": "vat",
        "VATName": "vat_name",
    }

    return df.rename(columns=columns)


def testing_dosage_number_times_annual_dosage(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"annual_doses": "annual_doses_original"})

    df["annual_doses"] = df["annual_doses_original"] * df["dosage_number"]

    return df


def map_manufacturer_to_country_region(
    df: pd.DataFrame, location_mapping: dict, region_mapping: dict
) -> pd.DataFrame:

    df["manufacturer_location"] = df["manufacturer"].map(location_mapping)

    df = add_iso_codes_column(
        df,
        id_column="manufacturer_location",
        id_type="regex",
        target_column="manufacturer_iso_code",
    )

    df["manufacturer_region"] = df["manufacturer_iso_code"].map(region_mapping)

    return df


def keep_year_range(df: pd.DataFrame, year: range) -> pd.DataFrame:

    return df.loc[lambda d: d.year.isin(year)]


def aggregate_by_year_manufacturer_region(df: pd.DataFrame) -> pd.DataFrame:
    groupby = [
        # "region",
        # "region_name",
        # "manufacturer_region",
        "year"
    ]

    return df.groupby(by=groupby)["annual_doses"].sum().reset_index()


def pivot_for_flourish(df: pd.DataFrame) -> pd.DataFrame:
    return df.pivot_table(
        index=["region", "region_name"], columns="manufacturer", values="annual_doses"
    ).reset_index()


def who_mi4a_pipeline(years: range) -> pd.DataFrame:
    df = (
        read_excel(
            file_name="2023_mi4a_public_database.xlsx",
            sheet_name="Vaccine Purchase Data",
        )
        .pipe(rename_columns)
        .pipe(keep_year_range, year=years)
        # .pipe(
        #     map_manufacturer_to_country_region,
        #     location_mapping=manufacturer_to_country,
        #     region_mapping=who_regional_mapping,
        # )
        .pipe(aggregate_by_year_manufacturer_region)
        # .pipe(pivot_for_flourish)
    )

    return df


def total_checks(final_dataset: pd.DataFrame, years=range) -> pd.DataFrame:

    final_overall_total = (
        final_dataset.filter(items={"annual_doses"}, axis=1).sum().item()
    )

    original_dataset = (
        read_excel(
            file_name="2023_mi4a_public_database.xlsx",
            sheet_name="Vaccine Purchase Data",
        )
        .pipe(rename_columns)
        .pipe(testing_dosage_number_times_annual_dosage)
        .loc[lambda d: d.year.isin(years)]
    )

    overall_total = original_dataset.filter(items={"annual_doses"}, axis=1).sum().item()

    check = pd.DataFrame(
        {"final_overall_total": [final_overall_total], "overall_total": [overall_total]}
    )

    check["check"] = check["final_overall_total"] == check["overall_total"]

    return check


if __name__ == "__main__":
    YEARS = range(2019, 2021 + 1)
    data = who_mi4a_pipeline(years=YEARS)
    # data.to_csv(config.Paths.output / "vaccine_production_by_region.csv", index=False)

    # total_checks = total_checks(final_dataset=data, years=YEARS)
