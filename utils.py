import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl



def find_age(dob):
    now = datetime.now().date()
    delta = now - dob
    seconds_in_year = 365.25*24*60*60
    age = delta.total_seconds() // seconds_in_year
    return age


def BMI(height, weight):
    bmi = weight/(height*height)
    return bmi


def diabetes_score(age, height, weight):
    model = pickle.load(open('./models/model.sav', 'rb'))
    
    bmi = BMI(height, weight)
    inp = np.array([age, bmi]).reshape(1, -1)
    
    out = model.predict_proba(inp)
    out = out[0][1]    
    return out


urine_color_dict = {
    'Clear':0,
    'Pale Yellow':1,
    'Yellow':2,
    'Dark Yellow':3,
    'Honey':4,
    'Brown':5
}

def color_score(color):
    score = urine_color_dict[color]
    return score/5


def ph_score(ph):
    if 4.5<ph<8:
        score = abs(ph-7)
        score = score/2.5
    else:
        score = 1
    return score


def risk_score(age, height, weight, urine_color, urine_ph):
    diabetes =  diabetes_score(age, height, weight)
    color = color_score(urine_color)
    ph = ph_score(urine_ph)
    
    score = (diabetes + color + ph) / 3
    return score


def segment_risk_score(age):
    if 0<=age<40:
        score = 0.0976
    elif 40<age<60:
        score = 0.3847
    else:
        score = 0.725
    return score


def risk_gauge(risk, segment=False):
    fig = go.Figure()

    if segment:
        title = 'Segment Lifestyle Risk'
    else:
        title = 'Lifestyle Risk'

    fig.add_trace(go.Indicator(
        mode = 'gauge+number',
        value = risk*100,
        title = {'text':title},
        gauge={'axis': {'range':[0,100]},
               'bar':{'color':'#4D96FF', 'thickness':0.17},
               'steps':[
                    {'range':[0,33.33], 'color':'#6BCB77'},
                    {'range':[33.33,66.66], 'color':'#FFD93D'},
                    {'range':[66.66,100], 'color':'#FF6B6B'}
              ]
              }
    ))
    
    return fig


def water_ph_plot(time_list, ph_list, water_list):
    fig = make_subplots(specs=[[{'secondary_y':True}]])
    fig.update_layout(title='Water intake vs. Urine pH')


    fig.add_trace(go.Bar(x=time_list, y=water_list, name='Glasses of water',
                         marker={'color':'#1b95e0'}, text=water_list), secondary_y=True)
    fig.add_trace(go.Scatter(x=time_list, y=ph_list, 
                             mode='lines+markers', name='Urine pH level',
                             marker={'color':'#FFA500'}), secondary_y=False)
    fig.add_trace(go.Scatter(x=time_list, y=[8 for i in range(24)], mode='lines',
                            line={'dash':'dash', 'color':'blue'},
                            name='Upper healthy pH limit (Alkaline)'))
    fig.add_trace(go.Scatter(x=time_list, y=[4.5 for i in range(24)], mode='lines',
                            line={'dash':'dash', 'color':'red'},
                            name='Lower healthy pH limit (Acidic)'))


    fig.update_yaxes(title_text='Urine pH level', range=[1,14], 
                     showgrid=True, secondary_y=False)
    fig.update_yaxes(range=[0,5], 
                     showgrid=False, tickvals=[],
                     secondary_y=True)
    fig.update_xaxes(title_text='Time')

    return fig


def ph_info(water_dict):
    time_list = []
    ph_list = [7 for i in range(24)]
    water_list = [0 for i in range(24)]
    
    time = min(water_dict.keys())
    time = datetime(100, 1, 1, time.hour, time.minute, time.second)
    time -= timedelta(hours=1)
    time = time.time()
    
    for i in range(24):
        time_list.append(time)
        last_time = time
        time = datetime(100, 1, 1, time.hour, time.minute, time.second)
        time += timedelta(hours=1)
        time = time.time()
        
        ph_list = ph_list[:i] + [j-0.25 for j in ph_list[i:]]
        
        for key in water_dict.keys():
            if last_time<=key<time:
                last_time = key
                time_list[i] = key
                water_list[i] = water_dict[key]
                ph_list[i:] = [7 for k in range(len(ph_list[i:]))]
        
    return time_list, ph_list, water_list


def recommendation(urine_color):
    if urine_color == 'Clear':
        rec = "Doing Great! You are well hydrated."
    elif urine_color == 'Pale Yellow':
        rec = "Doing ok. You're probably well hydrated. Drink water as normal."
    elif urine_color == 'Yellow':
        rec = "You're just fine. You could stand to drink a little water now, maybe a small glass of water."
    elif urine_color == 'Dark Yellow':
        rec = "Drink about 1/2 bottle of water (250 ml) within the hour, or drink a whole bottle (500 ml) of water if you're outside and/or sweating."
    elif urine_color == 'Honey':
        rec = "Drink about 1/2 bottle of water (250 ml) right now, or drink a whole bottle (500 ml) of water if you're outside and/or sweating."
    elif urine_color == 'Brown':
        rec = 'Drink 2 bottles of water right now (1000 ml).If your urine is darker than this and/or red, then dehydration may not be your problem.See a doctor.'
    else:
        rec = 'Please consult a docter.'
        
    return rec
