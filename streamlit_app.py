import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data
# import geopandas as gpd
import json

st.title("Let's analyze some CO2 emission data :)")

@st.cache  # add caching so we load the data only once
def load_data():
    climate_url = "https://raw.githubusercontent.com/ZeningQu/World-Bank-Data-by-Indicators/master/climate-change/climate-change.csv"
    country_url = "https://raw.githubusercontent.com/ZeningQu/World-Bank-Data-by-Indicators/master/climate-change/Metadata_Country_API_19_DS2_en_csv_v2_10137883.csv"
    climate_df = pd.read_csv(climate_url)
    climate_df.set_index("Country Code")
    country_df = pd.read_csv(country_url)
    country_df.set_index("Country Code")
    climate = climate_df.merge(country_df, on='Country Code', how='inner')

    country_loc = "https://gist.githubusercontent.com/tadast/8827699/raw/3cd639fa34eec5067080a61c69e3ae25e3076abb/countries_codes_and_coordinates.csv"
    country_loc_df = pd.read_csv(country_loc)
    country_loc_df.replace('"', '', regex=True, inplace=True)
    climate = climate.merge(country_loc_df, left_on="Country Name", right_on="Country", how="inner")
    return climate


df = load_data()
country_map_df = pd.read_table(
    "https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv")
countries = alt.topo_feature(data.world_110m.url, 'countries')

if st.checkbox("Show Raw Data"):
    st.write(df)

alt.data_transformers.disable_max_rows()


def preprocess_data(df):
    df = df.rename(columns={"CO2 emissions from gaseous fuel consumption (% of total)": "gaseous fuel % of total",
                            "CO2 emissions from liquid fuel consumption (% of total)": "liquid fuel % of total",
                            "CO2 emissions from solid fuel consumption (% of total)": "solid fuel % of total",
                            "CO2 emissions (metric tons per capita)": "CO2 emissions per capita",
                            "CO2 emissions (kg per PPP $ of GDP)" : "CO2 emissions per GDP",
                            "Renewable electricity output (% of total electricity output)":"Renewable electricity output % of total"})
    df = df[df['Year'] <= 2011]
    df = df[df['Year'] > 1990]
    df = df[df['CO2 emissions (kt)'] > 0]
    # df = df[df["Population growth (annual %)"] >= 0]
    return df


def world_map(highlight, highlight2):
    slider = alt.binding_range(min=1991, max=2011, step=1)
    select_year = alt.selection_single(name="Year", fields=['Year'],
                                       bind=slider, init={'Year': 2011})

    map = alt.Chart(df).mark_geoshape(
        stroke='#aaa', strokeWidth=0.25
    ).encode(
        color=alt.condition(highlight2 | highlight, 'CO2 emissions (kt):Q', alt.value('lightgrey'), scale=alt.Scale(scheme='redyellowblue', reverse=True)),
        tooltip=["Country Name", "CO2 emissions (kt)", "CO2 emissions per capita"]
    ).transform_lookup(
        lookup='Country Name',
        from_=alt.LookupData(
            "https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv",
            'name', ['id', "name"])
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(countries, 'id', fields=["id", "type", "properties", "geometry"])
    ).project(
        type="equirectangular"
    ).properties(
        width=1100,
        height=650,
        title='worldwide CO2 total emissions and emissions per capita'
    ).add_selection(highlight, highlight2)

    percapita = alt.Chart(df).mark_circle(
        opacity=0.4 ,
    ).encode(
        size=alt.Size('CO2 emissions per capita:Q', scale=alt.Scale(range=[10, 3000])),
        color=alt.condition(highlight2 | highlight, alt.value('red'), alt.value('lightgrey')),
        longitude='Longitude (average):Q',
        latitude='Latitude (average):Q'
    ).transform_lookup(
        lookup='Country Name',
        from_=alt.LookupData(
            "https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv",
            'name', ['id', "name"])
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(countries, 'id', fields=["id", "type", "properties", "geometry"])
    ).project(
        type="equirectangular"
    ).properties(
        width=900,
        height=400,
    )
    return alt.layer(map, percapita) \
        .add_selection(select_year) \
        .transform_filter(select_year)


def next_block():
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")
    st.write("\n")


def process_data(df):
    df2 = df  # [["Country Name", "Year", "CO2 emissions (kt)", "CO2 emissions from gaseous fuel consumption (kt)", "CO2 emissions from liquid fuel consumption (kt)", "CO2 emissions from solid fuel consumption (kt)"]]

    df2 = df2[df2["Country Name"].isin(dataset)]


    return df2.melt(id_vars=["Country Name", "Year", "CO2 emissions (kt)", "CO2 emissions per capita"],
                    value_vars=["solid fuel % of total", "liquid fuel % of total", "gaseous fuel % of total"],
                    var_name="type",
                    value_name="CO2 emissions from different consumptions (%)")


def scatter_plot():
    point = alt.Chart(df2).mark_circle().encode(
        x=alt.X('Year:O', title="Year"),
        y=alt.Y('CO2 emissions (kt)', title='Total CO2 emissions (kt)', scale=alt.Scale(zero=False, padding=1)),
        # color = alt.Color('Country Name:N',scale=alt.Scale(domain=dataset,type='ordinal'))
        # color = alt.Color('CO2 emissions (kt):Q')
        color=alt.condition(picked_interval, "CO2 emissions (kt):Q", alt.value("lightgray"),
                            scale=alt.Scale(scheme='redyellowblue', reverse=True), title="Total CO2 emissions (kt)")
        , size=alt.Size('CO2 emissions per capita:Q',
                        scale=alt.Scale(range=[200, 1000]))
        # , tooltip=["Country Name", "CO2 emissions (kt)", "CO2 emissions per capita", "Year"]
    )

    line = alt.Chart(df2).mark_line(
        strokeWidth=0.7
    ).encode(
        x=alt.X('Year:N', title="Year"),
        y=alt.Y('CO2 emissions (kt):Q', title='Total CO2 emissions (kt)'),
        color = alt.condition(picked_interval, "Country Name", alt.value("lightgray"), legend=None),
        # color = alt.Color('CO2 emissions (kt):Q')
        # color=alt.condition(picked_interval, "CO2 emissions (kt):Q", alt.value("lightgray"),
        #                     scale=alt.Scale(scheme='redyellowblue', reverse=True), title="Total CO2 emissions (kt)")
        # , size=alt.Size('CO2 emissions per capita:Q',
        #                 scale=alt.Scale(range=[100, 500]))
        tooltip=["Country Name", "CO2 emissions (kt)", "CO2 emissions per capita", "Year"]
    ).properties(
        width=650,
        height=500,
        title='CO2 total emission and emission per capita overtime'
    )

    labels = alt.Chart(df2).mark_text(align='center', dx=-20, dy=-25).encode(
        alt.X('Year:O', aggregate='max'),
        alt.Y('CO2 emissions (kt)', aggregate={'argmax': 'Year'}),
        alt.Text('Country Name'),
        alt.Color('CO2 emissions (kt):Q', aggregate={'argmax': 'Year'},
                  scale=alt.Scale(scheme='redyellowblue', reverse=True), legend=None),
        size=alt.value(17)
    ).properties(title='CO2 total emission and emission per capita', width=600)

    points = line+point+labels
    return points


def shape_plot():
    shape = alt.Chart(df2).mark_circle(
        opacity=0.35
    ).encode(
        alt.X('CO2 emissions (kt):Q'),
        alt.Y('CO2 emissions per capita:Q'),
        color=alt.Color('Country Name:N', scale=alt.Scale(scheme="tableau10")),
        shape=alt.Shape('Country Name:N', legend=None),
        size=alt.value(250),
        # size=alt.Size('CO2 emissions per capita:Q',
        #                 scale=alt.Scale(range=[100, 500]), legend=None)
    ).properties(
        width=300,
        height=250,
        title='CO2 total emissions and emissions per capita'
    )

    shape_labels = shape.mark_text(
        align='center',
        baseline='middle',
        dy=-25
    ).encode(
        text='Country Name',
        size=alt.value(15)
    )
    shapes = shape # + shape_labels
    return shapes



def world_map_for_factors(highlight, dataset, select_year):

    cols=alt.hconcat()
    for val in dataset:
        map = alt.Chart(df).mark_geoshape(
            stroke='#aaa', strokeWidth=0.25
        ).encode(
            x = alt.X("Country Name"),
            color=alt.condition(highlight, val, alt.value('lightgrey'), scale=alt.Scale(scheme='yelloworangered'), title=""),
            tooltip=["Country Name"] + dataset
        ).transform_lookup(
            lookup='Country Name',
            from_=alt.LookupData(
                "https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv",
                'name', ['id', "name"])
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(countries, 'id', fields=["id", "type", "properties", "geometry"])
        ).project(
            type="equirectangular"
        ).properties(
            width=500,
            height=200,
            title=val,
        ).add_selection(select_year, highlight) \
            .transform_filter(select_year)

        cols &= map
    return cols.resolve_scale(color='independent')

def total_trend(highlight, highlight2):
    total = alt.Chart(df).mark_bar().encode(
        alt.X('Year:N', title="Year"),
        alt.Y('CO2 emissions (kt)', title='Total CO2 emissions (kt)'),
        color=alt.Color('Country Name', scale=alt.Scale(scheme="set3"), title='Countries'),
        order=alt.Order(
            # Sort the segments of the bars by this field
            'CO2 emissions (kt)',
            sort='ascending'
        ),
        tooltip=["Country Name", 'CO2 emissions (kt)']
    ).properties(
        width=530,
        height=350,
        title='Total CO2 emissions world trend'
    ).transform_filter(highlight | highlight2)
    return total

def percapita_trend(highlight, highlight2):
    total = alt.Chart(df).mark_bar().encode(
        alt.X('Year:N', title="Year"),
        alt.Y('CO2 emissions per capita', title='CO2 emissions per capita (kt)'),
        color=alt.Color('Country Name', scale=alt.Scale(scheme="set3"), title='Countries'),
        order=alt.Order(
            # Sort the segments of the bars by this field
            'CO2 emissions per capita',
            sort='ascending'
        ),
        tooltip=["Country Name", 'CO2 emissions per capita']
    ).properties(
        width=530,
        height=350,
        title='CO2 emissions per capita world trend'
    ).transform_filter(highlight | highlight2)
    return total

################# main plots ############
df = preprocess_data(df)

st.header("Explore the worldwide CO2 emissions trend!")

highlight1 = alt.selection_multi(on='click', fields=['Country Name'], empty='all')
highlight2 = alt.selection_single(on='mouseover', fields=['Country Name'], empty='all')
st.write((world_map(highlight1, highlight2) & alt.hconcat(total_trend(highlight1, highlight2), percapita_trend(highlight1, highlight2))).resolve_scale(
    y='independent',
    size='independent'
))
next_block()

st.header("CO2 emissions from different consumptions")
st.write("Add countries and select year interval to explore CO2 emissions over time!")

dataset = st.multiselect("Choose countries you want to explore!", country_map_df["name"].to_list(),
                         ["China", "United States", "India", "Qatar"])
df2 = process_data(df)
picked_interval = alt.selection_interval(encodings=["x"])

points = scatter_plot()
shapes = shape_plot()

concat = alt.vconcat(
     alt.Chart(df2).mark_bar(
        opacity=0.9
     ).encode(
        alt.X("mean(CO2 emissions from different consumptions (%))"),
        alt.Y('Country Name', title=""),
        alt.Color('type', scale=alt.Scale(scheme="tableau10"), title='type'),
    ).properties(
        width=300,
        height=150,
        title='CO2 emissions from different consumptions'
    ).transform_filter(picked_interval),shapes.transform_filter(picked_interval)
).resolve_scale(
    color='independent'
)

vconcat = alt.hconcat(
    points.add_selection(picked_interval), concat
).resolve_scale(
    color='independent'
    , size='independent'
)

st.write(vconcat)
next_block()

st.header("Factors that may affect CO2 emissions")
slider = alt.binding_range(min=1991, max=2011, step=1)
select_year = alt.selection_single(name="Year", fields=['Year'],
                                       bind=slider, init={'Year': 2011})
highlight = alt.selection_single(on='mouseover', fields=['Country Name'], empty='all') #init={"Country Name": "United States"})

dataset2 = st.multiselect("Choose factors to compare!",
                             ["CO2 emissions per GDP", "CO2 emissions (kt)", "CO2 emissions per capita",
                              "Urban population (% of total)",
                              "Renewable energy consumption (% of total final energy consumption)",
                              "Forest area (% of land area)","Marine protected areas (% of territorial waters)","Population growth (annual %)","Renewable electricity output % of total"],
                             ["CO2 emissions (kt)","CO2 emissions per GDP","Renewable electricity output % of total"])


st.write(alt.hconcat(world_map_for_factors(highlight, dataset2, select_year), alt.Chart(df).mark_point().encode(
        alt.X(alt.repeat("column"), type='quantitative'),
        alt.Y(alt.repeat("row"), type='quantitative'),
        color='Country Name:N',
    ).properties(
        width=160,
        height=160,
    ).repeat(
        row=dataset2,
        column=dataset2,
    ).transform_filter(select_year).interactive()))
