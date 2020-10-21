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
    country_url ="https://raw.githubusercontent.com/ZeningQu/World-Bank-Data-by-Indicators/master/climate-change/Metadata_Country_API_19_DS2_en_csv_v2_10137883.csv"
    climate_df = pd.read_csv(climate_url)
    climate_df.set_index("Country Code")
    country_df = pd.read_csv(country_url)
    country_df.set_index("Country Code")
    climate = climate_df.merge(country_df, on='Country Code', how='inner')

    country_loc = "https://gist.githubusercontent.com/tadast/8827699/raw/3cd639fa34eec5067080a61c69e3ae25e3076abb/countries_codes_and_coordinates.csv"
    country_loc_df = pd.read_csv(country_loc)
    country_loc_df.replace('"', '', regex=True, inplace=True)
    climate = climate.merge(country_loc_df,left_on="Country Name",right_on = "Country", how = "inner")
    return climate
df = load_data()

countries = alt.topo_feature(data.world_110m.url, 'countries')

if st.checkbox("Show Raw Data"):
    st.write(df)

alt.data_transformers.disable_max_rows()
# #selections
# # picked = alt.selection_single(on="mouseover")
# picked = alt.selection_single(fields=["Species","Island"])
# picked_multi = alt.selection_multi()
# picked_interval = alt.selection_interval(encodings=["x"])
#
# input_dropdown = alt.binding_select(options = ["Adelie","Chinstrap","Gentoo"],name = "Species of ")
# picked_bind = alt.selection_single(encodings = ["color"], bind = input_dropdown)
#
# st.write("Hmm 🤔, is there some correlation between body mass and flipper length? Let's make a scatterplot with [Altair](https://altair-viz.github.io/) to find.")
#
# chart = alt.Chart(df).mark_point().encode(
#     x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
#     y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
#     color=alt.Y("species")
# ).properties(
#     width=600, height=400
# )\
#     # .interactive()
#
# st.write(chart.encode(color = alt.condition(picked_bind,"species:N",alt.value("lightgray")))
#          .add_selection(picked_bind))
#
#
# brush = alt.selection_interval(encodings=["x"])
# st.write(chart.add_selection(brush) & chart.encode(color = alt.condition(brush,"species:N",alt.value("lightgray"))).transform_filter(brush))
#
# st.write(chart.add_selection(brush) & alt.Chart(df).mark_bar().encode(
#     alt.X("body_mass_g",bin =True)
#     ,alt.Y("count()")
#     ,alt.Color("species")
# ).transform_filter(brush))
#
# min_weight = st.sidebar.slider("min weight",2500,6500)
#
# # min_weight = st.sidebar.slider("min weight",2500,6500)
# # scatter = alt.Chart(df).mark_point().transform_filter(alt.detaum["xxx"] >= min_weight).encode(
# # 	alt.X(),
# # 	alt.Y(),
# # 	alt.Color()
# # 	)

st.header("Explore the worldwide total CO2 emission and emission per capita trend!")
slider = alt.binding_range(min=1990, max=2011, step=1)
select_year = alt.selection_single(name = "Year",fields=['Year'],
                                   bind=slider, init={'Year': 1990})

c = alt.Chart(df).mark_geoshape(
    stroke='#aaa', strokeWidth=0.25
).encode(
    color=alt.Color('CO2 emissions (kt):Q',title = "total CO2 emissions"),
    tooltip = ["Country Name", "CO2 emissions (kt)", "CO2 emissions (metric tons per capita)"]
).transform_lookup(
    lookup='Country Name',
    from_=alt.LookupData("https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv", 'name', ['id',"name"])
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(countries, 'id', fields=["id","type", "properties", "geometry"])
).project(
    type="equirectangular"
).properties(
    width=900,
    height=500,
    title='Country Name'
)

percapita = alt.Chart(df).mark_circle().encode(
    size=alt.Size('CO2 emissions (metric tons per capita):Q', title='CO2 emissions per capita'),
    color = alt.value("red"),
    longitude='Longitude (average):Q',
    latitude='Latitude (average):Q'
).transform_lookup(
    lookup='Country Name',
    from_=alt.LookupData("https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv", 'name', ['id',"name"])
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(countries, 'id', fields=["id","type", "properties", "geometry"])
).project(
    type="equirectangular"
).properties(
    width=900,
    height=500,
    title='Country Name'
)

# input_dropdown = alt.binding_select(options = ["Europe & Central Asia","Sub-Saharan Africa"],name = "Region of ")
# picked_bind = alt.selection_single(encodings = ["color"], bind = input_dropdown)
# picked = alt.selection_single(empty='all', fields=['Country Name'])
# brush = alt.selection_interval(encodings=["x"])

all = alt.layer(c,percapita)\
    .add_selection(select_year)\
    .transform_filter(select_year )
st.write(all)


st.header("Try to compare the countries you're interested!")
dataset = st.multiselect("Choose countries you want to explore!", ["China","United States","United Kingdom","India","Russian Federation","Australia","Qatar"], ["China","United States"])

df1 = df
df1 = df1[df1["Country Name"].isin(dataset)]
df1 = df1[df1['Year'] <2011]
df1 = df1[df1['Year'] >1990]
df1 = df1[df1['CO2 emissions (kt)'] >0]

line = alt.Chart(df1).mark_trail().encode(
    x=alt.X('Year'),
    y=alt.Y('CO2 emissions (kt)'),
    color = alt.Color('Country Name:N',scale=alt.Scale(domain=dataset,type='ordinal'))
    ,size = alt.Size('CO2 emissions (metric tons per capita):Q',title="CO2 emission per capita")
    ,tooltip=["Country Name","CO2 emissions (kt)","CO2 emissions (metric tons per capita)","Year"]
).properties(
    width=900,
    height=500,
    title='Country Name'
)

labels = alt.Chart(df1).mark_text(align='left', dx=3).encode(
    alt.X('Year', aggregate='max'),
    alt.Y('CO2 emissions (kt)', aggregate={'argmax': 'Year'}),
    alt.Text('Country Name'),
    alt.Color('Country Name:N', legend=None, scale=alt.Scale(domain=dataset,type='ordinal')),
).properties(title='CO2 total emission and emission per capita', width=600)


st.write(line+labels)

# brush = alt.selection_interval
# st.write

# bar chart


st.header("Explore different types of CO2 emission")
dataset2 = st.multiselect("Choose countries you want to explore!", ["China","United States","United Kingdom","India","Russian Federation","Australia","Qatar"], ["China","United States"], key="bar")
# tfilter = st.slider("Year", 1990, 2011, 1990)

slider2 = alt.binding_range(min=1990, max=2011, step=1)
select_year2 = alt.selection_single(name = "Year",fields=['Year'],
                                   bind=slider, init={'Year': 1990})

df2 = df[["Country Name", "Year", "CO2 emissions (kt)", "CO2 emissions from gaseous fuel consumption (kt)", "CO2 emissions from liquid fuel consumption (kt)", "CO2 emissions from solid fuel consumption (kt)"]]
df2 = df2.rename(columns={"CO2 emissions from gaseous fuel consumption (kt)": "gaseous fuel", "CO2 emissions from liquid fuel consumption (kt)": "liquid fuel", "CO2 emissions from solid fuel consumption (kt)": "solid fuel"})

df2 = df2[df2["Country Name"].isin(dataset2)]
df2 = df2[df2['Year'] <= 2011]
df2 = df2[df2['Year'] >= 1990]
df2 = df2[df2['CO2 emissions (kt)'] >0]

df2 = df2.melt(id_vars=["Country Name", "Year"],
               value_vars=["solid fuel", "liquid fuel", "gaseous fuel"],
               var_name="type",
               value_name="CO2 emissions (kt)")


bar = alt.Chart(df2).mark_bar().encode(
    # alt.Column('Year'),
    alt.X("CO2 emissions (kt)"),
    alt.Y('Country Name'),
    alt.Color('type'),
).properties(width=800).add_selection(select_year2)\
    .transform_filter(select_year2)

st.write(bar)
