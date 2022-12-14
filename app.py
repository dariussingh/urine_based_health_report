import utils
import streamlit as st
import datetime as dt
from datetime import datetime



# Set config
st.set_page_config(page_title='The Tann Mann Gaadi',
            layout='wide') 

st.title("The Tann Mann Gaadi")
st.image('./assets/ttmg.jpg')
st.markdown('---')
# ---------------------------------------------------------------

st.header('Register User')
name = st.text_input('Name')
dob = st.date_input('Date of birth', min_value=datetime(1930, 1, 1).date())
sex = st.selectbox('Sex', ['Male', 'Female', 'Other'])
height = st.number_input('Height (in meters)', min_value=0.3, max_value=3.0, value=1.6)
weight = st.number_input('Weight (in Kilogram)', min_value=10, max_value=300, value=60)
st.markdown('---')
# ---------------------------------------------------------------

st.header("How much water did your drink today")
water_drinking_ocassions = st.slider('Number of water drinking ocassions today', 1, 10, value=5)
    
water_dict = dict()

for i in range(water_drinking_ocassions):
    col1, col2 = st.columns((1,1))
    time_ = col1.time_input('Time', key=str(i), value=dt.time(i+2,0))
    num_glasses = col2.slider('Number of glasses of water you drank last', min_value=1, max_value=5, value=2, key=str(10+i))
    water_dict[time_] = num_glasses
    st.markdown("")
st.markdown('---')  
# ---------------------------------------------------------------

st.header('Urine Details')
urine_passing_ocassions = st.slider('Number of urine passing ocassions today', 1, 10, value=5)

urine_ph_dict = dict()
urine_color_dict = dict()

for i in range(urine_passing_ocassions):
    col1, col2, col3 = st.columns((1,1,1))
    time_ = col1.time_input('Time', key='9'+str(i), value=dt.time(i+2,0))
    urine_color = col2.selectbox('Urine Colour', ['Clear', 'Pale Yellow', 'Yellow', 'Dark Yellow', 'Honey', 'Brown'], key='8'+str(i))
    urine_ph = col3.slider('Urine pH', min_value=1.0, max_value=14.0, value=7.0, step=0.25, key='7'+str(i))
    urine_ph_dict[time_] = urine_ph
    urine_color_dict[time_] = urine_color
    st.markdown("")

urine_ph = utils.avg_ph(list(urine_ph_dict.values()))
urine_color = utils.avg_color(list(urine_color_dict.values()))
st.markdown('---')
# ---------------------------------------------------------------

if st.button('Submit'):
    st.header(f'Wellness Report for {name}')
    age = utils.find_age(dob)
    risk = utils.risk_score(age, height, weight, urine_color, urine_ph)
    segment_risk = utils.segment_risk_score(age)

    st.markdown(f'Date: {datetime.now().date()}')

    col1, col2 = st.columns((1,1))

    col1.plotly_chart(utils.risk_gauge(risk), use_container_width=True)

    col2.plotly_chart(utils.risk_gauge(segment_risk, segment=True), use_container_width=True)

    st.markdown('---')
    # ---------------------------------------------------------------

    col1, col2 = st.columns((2,1))
    
    time_list, ph_list, water_list = utils.ph_info(water_dict, urine_ph_dict)
    col1.markdown('## Urine pH Chart')
    col1.plotly_chart(utils.water_ph_plot(time_list, ph_list, water_list), use_container_width=True)
    
    col2.markdown(f"""
    ## Recommendation
    The general colour of your urine is {urine_color} and its average pH is {urine_ph}.
    {utils.color_based_recommendation(urine_color)}
    """)
    col2.markdown(f"__{utils.drink_water_recommendation(time_list, ph_list, water_list)}__")

    st.markdown('---')
    # ---------------------------------------------------------------

    col1, col2 = st.columns((2,1))
    
    col1.markdown(f"""
    ## Lifestyle Improvement Tips
    {utils.ph_based_recommendation(urine_ph)}
    """)
    col1.markdown(f"""
    {utils.extreme_case_based_recommendation(time_list, ph_list)}
    """)
    col1.markdown("""
    ## More Information
    For more information and to learn how you can adopt a healthier life style visit [The Tann Mann Gaadi](https://www.thetannmanngaadi.org/).
    """)
    
    col2.markdown('## Urine pH Scale')
    col2.pyplot(utils.ph_chart(urine_ph))
    if 4.5<urine_ph<8:
        col2.markdown("""Your urine pH is within normal ranges. 
                    Keep in mind to hydrate yourself on a regular basis.""")
    else:
        col2.markdown('__Please consult a doctor immediately.__')

    st.markdown('---')
    # ---------------------------------------------------------------


    