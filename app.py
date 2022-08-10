import utils
import streamlit as st
from datetime import datetime


# Set config
st.set_page_config(layout='wide') 

st.title("Tann Mann Gaadi")
st.header('Register User')

# ---------------------------------------------------------------
name = st.text_input('Name')
dob = st.date_input('Date of birth', min_value=datetime(1930, 1, 1).date())
sex = st.selectbox('Sex', ['Male', 'Female', 'Other'])
height = st.number_input('Height (in meters)', min_value=0.3, max_value=3.0, value=1.6)
weight = st.number_input('Weight (in Kilogram)', min_value=10, max_value=300, value=60)
last_time_water = st.time_input('Last time you drank water')
number_of_glasses = st.slider('Number of glasses of water you drank last', min_value=1, max_value=7, value=2)
urine_color = st.selectbox('Urine Colour', ['Clear', 'Pale Yellow', 'Yellow', 'Dark Yellow', 'Honey', 'Brown'])
urine_ph = st.slider('Urine pH', min_value=1, max_value=14, value=7)
# ---------------------------------------------------------------

if st.button('Submit'):
    st.markdown('---')
    st.header(f'Wellness Report for {name}')
    age = utils.find_age(dob)
    risk = utils.risk_score(age, height, weight, urine_color, urine_ph)
    segment_risk = utils.segment_risk_score(age)

    st.markdown(f'Date: {datetime.now().date()}')

    col1, col2 = st.columns((1,1))

    col1.plotly_chart(utils.risk_gauge(risk), use_container_width=True)
    col2.plotly_chart(utils.risk_gauge(segment_risk, segment=True), use_container_width=True)

    st.markdown('---')

    col1, col2 = st.columns((1,1))
    time_list, ph_list, water_list = utils.ph_info(last_time_water, number_of_glasses)
    col1.markdown('## Urine pH Chart')
    col1.plotly_chart(utils.water_ph_plot(time_list, ph_list, water_list), use_container_width=True)
    col2.markdown(f"""
    ## Recommendation:
    The colour of your urine is {urine_color} and its pH is {urine_ph}.
    {utils.recommendation(urine_color)}
    """)

    st.markdown('---')
    