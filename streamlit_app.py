import streamlit as st
import pandas as pd
import altair as alt

st.title("Let's analyze some Penguin Data hahahha ：） 🐧📊.")

@st.cache  # add caching so we load the data only once
def load_data():
    # Load the penguin data from https://github.com/allisonhorst/palmerpenguins.
    penguins_url = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/v0.1.0/inst/extdata/penguins.csv"
    return pd.read_csv(penguins_url)

df = load_data()

st.write("Let's look at raw data in the Pandas Data Frame.")

if st.checkbox("show raw data"):
    st.write(df)

#selections
# picked = alt.selection_single(on="mouseover")
picked = alt.selection_single(fields=["Species","Island"])
picked_multi = alt.selection_multi()
picked_interval = alt.selection_interval(encodings=["x"])

input_dropdown = alt.binding_select(options = ["Adelie","Chinstrap","Gentoo"],name = "Species of ")
picked_bind = alt.selection_single(encodings = ["color"], bind = input_dropdown)

st.write("Hmm 🤔, is there some correlation between body mass and flipper length? Let's make a scatterplot with [Altair](https://altair-viz.github.io/) to find.")

chart = alt.Chart(df).mark_point().encode(
    x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
    y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
    color=alt.Y("species")
).properties(
    width=600, height=400
)\
    # .interactive()

st.write(chart.encode(color = alt.condition(picked_bind,"species:N",alt.value("lightgray")))
         .add_selection(picked_bind))


brush = alt.selection_interval(encodings=["x"])
st.write(chart.add_selection(brush) & chart.encode(color = alt.condition(brush,"species:N",alt.value("lightgray"))).transform_filter(brush))

st.write(chart.add_selection(brush) & alt.Chart(df).mark_bar().encode(
    alt.X("body_mass_g",bin =True)
    ,alt.Y("count()")
    ,alt.Color("species")
).transform_filter(brush))