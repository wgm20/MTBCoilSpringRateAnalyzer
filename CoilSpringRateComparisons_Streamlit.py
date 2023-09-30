import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
from time import time
from datetime import timedelta
import warnings
import altair as alt

import streamlit as st

#functions
def motion_ratio(travel, stroke):
    return travel/stroke

def spring_rate_at_wheel(spring, motion_ratio):
    return spring/(motion_ratio**2)

def spring_rate_at_wheel_normalised_75kg(spring_rate_at_wheel, weight):
    return spring_rate_at_wheel*75/weight

def energy_at_max_travel(spring_rate, shock_stroke):
    return 0.5*(spring_rate*175.126835)*((shock_stroke/1000)**2)

def huck_height(energy_at_max_travel, weight):
    return energy_at_max_travel/(0.6*weight*9.81)

def add_label(name, spring):
    return name + " " + str(spring) + "lbs/in"
    
def add_calucated_quantitles(df):
    df['Motion_ratio'] = motion_ratio(df['Travel'], df['Stroke'])
    df['Spring_rate_at_wheel'] = spring_rate_at_wheel(df['Spring_rate'],df['Motion_ratio'])
    df['Spring_rate_at_wheel_normalised_75kg'] = spring_rate_at_wheel_normalised_75kg(df['Spring_rate_at_wheel'],df['Weight'])
    df['Energy_at_max_travel'] = energy_at_max_travel(df['Spring_rate'], df['Stroke'])
    df['Huck_height_(m)'] = huck_height(df['Energy_at_max_travel'], df['Weight'])
    df['LabelX'] = np.vectorize(add_label)(df['Name'], df['Spring_rate'])
    


# Title
st.markdown("<h1 style='font-size: 54px;'>Setup analyzer</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='font-size: 40px;'>Uncover your ideal configuration</h1>", unsafe_allow_html=True)
# Description
st.markdown("""
<sub style='font-size: 16px;'>
Enter your details on the left and change the spring rate until you find an appropriate spring for your mountain bike, travel and weight.
</sub>
""", unsafe_allow_html=True)
# Credit
st.write("\n")
st.markdown("""
<sub style='font-size: 16px;'>
Credit: Rowland Jowett for the original very useful prototype.
</sub>
""", unsafe_allow_html=True)

st.write("\n")
st.write("\n")
st.write("\n")

# User Inputs
st.title("Coil Spring Rate Comparisons")
st.write("\n")
st.sidebar.markdown("### Setup Analyzer")
st.sidebar.markdown("Enter your details...")

user_discipline = st.sidebar.selectbox("Discipline", ['Enduro', 'DH'])
user_stroke = st.sidebar.slider("Rear shock stroke (mm)", 20.0, 100.0, 63.0, 0.5)  # All values are floats
user_travel = st.sidebar.slider("Rear wheel vertical travel (mm)", 100.0, 250.0, 160.0, 5.0)  # All values are floats
user_weight = st.sidebar.slider("Rider weight (Kg)", 20.0, 200.0, 80.0, 1.0)  # All values are floats
user_spring_rate = st.sidebar.slider("Spring_rate lbs/in", 200.0, 800.0, 434.0, 5.0)  # All values are floats
user_speed_rating = st.sidebar.slider("Rider speed, Mens WCDH = 10", 1.0, 10.0, 5.0, 1.0)  # All values are floats
user_name = st.sidebar.text_input("Name", "Jane Doe")

# Data Preparation and Calculation
df = pd.read_csv("Data.csv", index_col=1)
df = df.reset_index()


data = {
    'Discipline': ['Entered data'],
    'Name': [user_name],
    'Stroke': [user_stroke],
    'Travel': [user_travel],
    'Spring_rate': [user_spring_rate],
    'Weight': [user_weight],
    'Speed_rating': [user_speed_rating],
}

df_user = pd.DataFrame(data)
add_calucated_quantitles(df)
add_calucated_quantitles(df_user)
df_user['plot_point_size'] = 3
df['plot_point_size'] = 2
df_combined = pd.concat([df, df_user])


# Make the chart
points = alt.Chart(df, title='Normalised Rider Weight Spring Rate vs Bike Max Travel').mark_circle().encode(
    alt.X('Travel:Q',axis=alt.Axis(title ='Travel_')).scale(zero=False),
    alt.Y('Spring_rate_at_wheel_normalised_75kg:Q', axis=alt.Axis(title ='Spring_rate_at_wheel_normalised_75kg_')).scale(zero=False),
    color='Discipline:N',
    tooltip=['Name', 'Weight', 'Spring_rate', 'Speed_rating', 'Discipline'],
)
points_user = alt.Chart(df_user, title='Normalised Rider Weight Spring Rate vs Bike Max Travel').mark_circle().encode(
    alt.X('Travel:Q',axis=alt.Axis(title ='Travel_')).scale(zero=False),
    alt.Y('Spring_rate_at_wheel_normalised_75kg:Q', axis=alt.Axis(title ='Spring_rate_at_wheel_normalised_75kg_')).scale(zero=False),
    color='Discipline:N',
    tooltip=['Name', 'Weight', 'Spring_rate', 'Speed_rating', 'Discipline'],
    size=alt.value(200)
)

labels =  alt.Chart(df_combined).mark_text(align='left', baseline='middle', dx=4, fontSize=14).encode(alt.X('Travel:Q').scale(zero=False),
    alt.Y('Spring_rate_at_wheel_normalised_75kg:Q').scale(zero=False),
    text='LabelX:N')

reg = alt.Chart(df).mark_circle().encode(
    alt.X('Travel:Q',axis=alt.Axis(title ='Travel_')).scale(zero=False),
    alt.Y('Spring_rate_at_wheel_normalised_75kg:Q', axis=alt.Axis(title ='Spring_rate_at_wheel_normalised_75kg_')).scale(zero=False),
    color='Discipline:N',
    tooltip=['Name', 'Weight', 'Spring_rate', 'Speed_rating', 'Discipline']
).transform_regression('Travel', 'Spring_rate_at_wheel_normalised_75kg').mark_line(
     opacity=0.50, 
     shape='mark'
).transform_fold(
     ["best fit line"], 
     as_=["Regression", "y"]
).encode(alt.Color("Regression:N"))


charts = (points + points_user + reg + labels).properties(width="container").interactive().properties(
    width=1000,
    height=600
)


# Make the chart
huck_height_chart = alt.Chart(df, title='Huck_height_(m) ').mark_circle().encode(
    alt.X('Travel:Q').scale(zero=False),
    alt.Y('Huck_height_(m):Q').scale(zero=False),
    color='Discipline:N',
    tooltip=['Name', 'Weight', 'Spring_rate', 'Speed_rating', 'Discipline']
).properties(
    width="container"
)

huck_height_chart_user = alt.Chart(df_user, title='Huck_height_(m) ').mark_circle().encode(
    alt.X('Travel:Q').scale(zero=False),
    alt.Y('Huck_height_(m):Q').scale(zero=False),
    color='Discipline:N',
    tooltip=['Name', 'Weight', 'Spring_rate', 'Speed_rating', 'Discipline'],
    size=alt.value(200)
).properties(
    width="container"
)

labels_h =  alt.Chart(df_combined).mark_text(align='left', baseline='middle', dx=4, fontSize=14).encode(alt.X('Travel:Q').scale(zero=False),
    alt.Y('Huck_height_(m):Q').scale(zero=False),
    text='LabelX:N')

reg_h = alt.Chart(df).mark_circle().encode(
    alt.X('Travel:Q',axis=alt.Axis(title ='Travel_')).scale(zero=False),
    alt.Y('Huck_height_(m):Q', axis=alt.Axis(title ='Huck_height_(m)')).scale(zero=False),
    color='Discipline:N',
    tooltip=['Name', 'Weight', 'Spring_rate', 'Speed_rating', 'Discipline']
).transform_regression('Travel', 'Huck_height_(m)').mark_line(
     opacity=0.50, 
     shape='mark'
).transform_fold(
     ["best fit line"], 
     as_=["Regression", "y"]
).encode(alt.Color("Regression:N"))

charts2 = (huck_height_chart + huck_height_chart_user + reg_h + labels_h).interactive().properties(
    width=1000,
    height=600
)

#display charts
# Display the chart in the Streamlit app
st.altair_chart(charts)
st.altair_chart(charts2)



st.markdown("""
### Definitions:

- **Spring_rate_at_wheel_normalised_75kg:**  
    This metric adjusts the spring rate of different setups to make them comparable as if a 75kg rider were using them. 
    By standardizing the setups to a 75kg rider, you can easily compare the stiffness across different rider weights. 
    For instance, if a 90kg rider uses a 500lbs/in spring, this would feel similar to a 75kg rider using a 416lbs/in spring.

- **Huck_height:**  
    Huck_height is the height you could drop rider and bike from and all energy be contained in the spring without bottoming out (assumes 60% of weight on rear wheel)

Any questions, please email [mulholland.william@gmail.com](mailto:mulholland.william@gmail.com) with the subject: Coil spring rate comparisons.

If this page is of more than fleeting interest, please consider donating to the air ambulance service: [Air Ambulance Donation](https://theairambulanceservice.org.uk)
""")
