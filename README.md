# Vaccine Manufacturing DataDive

This repository contains analysis for the updated manufacturing datadive, prepared for health-related summits in June. 

Around 99% of vaccines administered in Africa are produced outside the continent. This has contributed to unequal access to life-saving vaccines and significant health disparities between regions.

The COVID-19 pandemic put a spotlight on this problem when rich countries monopolized the majority of vaccines. In response the African Union set a target of producing 60% of its own vaccines by 2040. 

The analysis in this Data Dive can be divided into:
- [Vaccine Supply: WHO MI4A Dataset (Provided by WHO)](#vaccine-supply-who-mi4a-dataset-provided-by-who)
- [Vaccine Demand: Linksbridge's Vaccine Almanac](#vaccine-demand-linksbridges-vaccine-almanac-access-granted-may-2024)
- [Manufacturing Facility Commitments](#manufacturing-facility-commitments)
- [COVID-19 Vaccine Hoarding](#covid-19-vaccine-hoarding)
- [Gavi-related Statistics](#gavi-related-statistics)

This repository uses data provided by WHO (vaccine supply), Linksbridge (vaccine demand), and PATH/CHAI (manufacturing commitments), alongside various reports (gavi-specific statistics) to complete all analysis. 

Below outlines each data source, the data visualisations they provide, alongside other useful information. 

## Vaccine Supply: WHO MI4A Dataset (Provided by WHO)

### Data Visualisation(s)

Data visualisation: Waffle chart
Link: https://public.flourish.studio/story/2435672/
Embed codes: <div class="flourish-embed" data-src="story/2435672?1105200"><script src="https://public.flourish.studio/resources/embed.js"></script></div>

Data visualisation: "Africa produces a fraction of the world's vaccines"
Link: https://public.flourish.studio/story/2439096/
Embed codes: `<div class="flourish-embed" data-src="story/2439096?1105200"><script src="https://public.flourish.studio/resources/embed.js"></script></div>`

### Relevant files
Core analysis is completed on `who_mi4a_data.py`. Analysed data is stored in `african_vaccine_supply.csv`.

### More information

The World Health Organisation has a [publicly available dataset of vaccine purchase data](https://www.who.int/publications/m/item/mi4a-2023-public-database). This dataset is self-reported by governments based on their purchases of vaccines. There is an additional data which is not publicly available which contains similar data but from the manufacturers perspective. WHO have compiled this data but cannot share publicly for privacy and relationship reasons. Instead, they shared with us an [aggregated version of their dataset](https://github.com/ONEcampaign/vaccine_manufacturing/blob/15-in-text-statistics/raw_data/GVMR%202023%20-%20ONE%20Campaign%20May%202024_vShared.xlsx) which shows the number of vaccines distributed by each continent to both the World and Africa, including and excluding COVID-19 vaccines. 

We used this data for all vaccine_supply related statistics in the paper. This includes the above data visualisation and the key statistics related to supply of vaccines. 




## Vaccine Demand: Linksbridge's Vaccine Almanac (access granted May 2024)

### Data Visualisation(s)

Data visualisation: "Africa's share of global vaccine demand is increasing"
Link: https://public.flourish.studio/story/2439166/
Embed codes: `<div class="flourish-embed" data-src="story/2439166?1105200"><script src="https://public.flourish.studio/resources/embed.js"></script></div>`

### Relevant files
Core analysis is completed on `vaccine_demand.py`. Analysed data is stored in `vaccine_demand_by_region.csv`.

### More information

The Vaccine Almanac showcases market information across multiple vaccine markets. You can find the 2024 vaccine almanac report [here](https://4550bf57-cdn.agilitycms.cloud/vaccine-almanac/2024%20Vaccine%20Almanac.pdf?utm_medium=email&_hsmi=295322802&utm_content=295322802&utm_source=hs_email). The Vaccine Almanac is powered by the GVMM dataset. Not all the data in the GVMM is available in the Almanac. 

The dataset is split into 6 main branches, each containing different sub-datasets. The dataset is structured as follows:
```
Vaccine Almanac
│
├─> Demand
│   │
│   ├──> Total Required Supply
│   ├──> Total Required Supply by Country
│   └──> Childhood Immunisation Schedule
│
├─> Supply
│   │
│   ├──> Vaccine Pipeline
│   ├──> PQ'd Vaccines
│   └──> UNICEF Contract Values
│
├─> Market Value
│   └──> Market Value
│
├─> Price
│   └──> Price Reference
│
├─> Private Markets
│   │
│   ├──> Overview
│   ├──> Private Market
│   └──> Traveler and Military Market
│
└─> Market Share
    └──> Market Share
```

We focused on vaccine demand analysis. This data excludes COVID-19 data. You can see overviews of how vaccine demand is estimated [here](https://dcvmn.org/wp-content/uploads/2015/07/use_of_gvmm_data_in_decision_making_circulation.pdf) and [here](https://4550bf57-cdn.agilitycms.cloud/help-guides/Introduction%20to%20GVMM%20v6.1.pdf). 

We clarified some issues with the data in [issue 12](https://github.com/ONEcampaign/vaccine_manufacturing/issues/12). You can see Linksbridge's privacy and data use policies [here](https://linksbridge.com/data-use).


## Manufacturing Facility Commitments

### Data Visualisation(s)
Data Visualisation: "30 public investment annoucements have been made in Africa"
Link: https://public.flourish.studio/story/2439172/
Embed codes: `<div class="flourish-embed" data-src="story/2439172?1105200"><script src="https://public.flourish.studio/resources/embed.js"></script></div>`

### Relevant Files
To be added.

### More Information

Updated data on manufacturing commitments is extremely difficult to find. ONE attempted to find updates on the 30 manufacturing commitments referenced in the health space, but had little luck. Instead, case studies were provided to show that some projects have continued nicely, others slowly, many with unclear progress, and some cancelled. 

The actual name, location, and partnering companies involved in the 30 often referenced projects are disputed. We opted to follow the most recent data from research by CHAI and PATH, following a call in June. They kindly provided us with data via email. CHAI and PATH, in partnership with Africa CDC plan to update this data very soon. We will update our data visualisation accordingly with this data. 

## COVID-19 Vaccine Hoarding

More detail to be added. Data from an old repository. 

### Data Visualisation(s)

Data Visualisation: "But no example is as stark as the “vaccine apartheid” of COVID-19."
Link: https://public.flourish.studio/story/2430143/
Embed codes: `<div class="flourish-embed" data-src="story/2430143?1105200"><script src="https://public.flourish.studio/resources/embed.js"></script></div>`


## Gavi-related Statistics

Aim: Produce the below statistic on current share of Gavi vaccines going to countries predicted to transition away from Gavi support by 2030.  

> Meanwhile, Africa’s demand for vaccine sovereignty will only become more critical. Six African countries—
> São Tomé and Príncipe, Nigeria, Kenya, Ghana, Djibouti, and Côte d'Ivoire—are projected to transition out
> of Gavi support by 2030. These countries represented **18%** of vaccine doses fully supported by Gavi funding in 2023...


We use data from the [Gavi Shipment 2023 Vaccines - All Regions](https://www.unicef.org/supply/media/20656/file/Gavi-shipments-2023.pdf) dataset. We calculate the share of Gavi funded vaccines going to the six countries who are set to transition away from Gavi support by 2030.

Our methodology goes as follows:
- removes non-vaccine dose lines ("AD-Syringe, 0.5 ml", "AD-Syringe, 0.1 ml", "RUP-5.0 ml", "Safety Box, 5 Litre")
- removes co-financing, keeping only fully GAVI funded lines
- Aggregates remaining number of vaccine doses by country
- Calculates share of total for each country (using the above aggregates)
- Filters for the 6 transitioning countries ("Sao Tome & Principe", "Nigeria", "Kenya", "Ghana", "Djibouti", "Cote d'Ivoire")
- Sums the 6 countries share of Gavi funded total

### Relevant Files
To be added once branch merged. 
