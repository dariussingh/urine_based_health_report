# utils 
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import datetime as dt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
import statistics



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
    fig.add_trace(go.Scatter(x=time_list, y=[8 for i in range(len(time_list))], mode='lines',
                            line={'dash':'dash', 'color':'blue'},
                            name='Upper healthy pH limit (Alkaline)'))
    fig.add_trace(go.Scatter(x=time_list, y=[4.5 for i in range(len(time_list))], mode='lines',
                            line={'dash':'dash', 'color':'red'},
                            name='Lower healthy pH limit (Acidic)'))


    fig.update_yaxes(title_text='Urine pH level', range=[1,14], 
                     showgrid=True, secondary_y=False)
    fig.update_yaxes(range=[0,5], 
                     showgrid=False, tickvals=[],
                     secondary_y=True)
    fig.update_xaxes(title_text='Time')

    return fig




def ph_info(water_dict, urine_ph_dict):
    time_list = []
    ph_list = []
    water_list = []
    time_ = dt.time(0,0)

    for i in range(24):
        time_list.append(time_)
        time_ = datetime(100, 1, 1, time_.hour, time_.minute, time_.second)
        time_ += timedelta(hours=1)
        time_ = time_.time()
    
    time_list = time_list + list(water_dict.keys()) + list(urine_ph_dict.keys())
    time_list = list(set(time_list))
    time_list = sorted(time_list)

    
    ph = 7
    
    for key in time_list:
        # check urine_ph_dict
        if key in urine_ph_dict:
            ph = urine_ph_dict[key]
        else:
            if 1.5<=ph<=13.5:
                ph -= 0.25
        # check water_dict
        if key in water_dict.keys():
            water = water_dict[key]
            if ph+water<=7.25:
                ph += water
            else:
                ph = 7
        else:
            water = 0
        
        ph_list.append(ph)
        water_list.append(water)
        
    
    return time_list, ph_list, water_list




def color_based_recommendation(urine_color):
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


def ph_based_recommendation(urine_ph):
    if 0<=urine_ph<4.5:
        rec = "Something is severely wrong. Your body is dangerously acidic, please see a doctor right away."
    elif 4.5<=urine_ph<5:
        rec = "This is a danger zone, your body is too acidic, drastic dietary and lifestyle changes are advised. Please see a doctor."
    elif 5<=urine_ph<6:
        rec = 'Consider dietary and lifestyle changes to improve the pH of your body.'
    elif 6<=urine_ph<6.5:
        rec = "Consider slight dietary adjustments to bring your pH back up to where it should be."
    elif 6.5<=urine_ph<7.25:
        rec = 'Congratulations! Keep up the good work by maintaining an alkalising lifestyle.'
    elif 7.25<=urine_ph<8:
        rec = "WHile not uncommon, this is not healthy."
    else:
        rec = 'Something is severely wrong. Your body is dangerously alkaline, please see a doctor right away.'
        
    return rec


def drink_water_recommendation(time_list, ph_list, water_list):
    rehydrate_time = []
    for i in range(len(time_list)):
        ph = ph_list[i]
        time = time_list[i]
        water = water_list[i]

        if water!=0:
            rehydrate_time = []
            last_water = time
            
        if ph<=4.5 or ph>=8:
            rehydrate_time.append(time)
        else:
            pass
        
    if rehydrate_time == []:
        last_water = datetime(100, 1, 1, last_water.hour, last_water.minute, last_water.second)
        last_water += timedelta(hours=3)
        last_water = last_water.time()
        rehydrate_time = [last_water]
        rec_time = rehydrate_time[0].strftime('%I:%M %p')
        rec =f"It is advised that you drink water and rehydrate before {rec_time}."
    elif rehydrate_time[0]==last_water:
        rec_time = last_water.strftime('%I:%M %p')
        rec = f"You did not drink enough water the last time you drank water (at {rec_time}), it is advised you drink more water immediately."
    else:
        rec_time = rehydrate_time[0].strftime('%I:%M %p')
        rec =f"It is advised that you drink water and rehydrate before {rec_time}."

    return rec


def extreme_case_based_recommendation(time_list, ph_list):
    rec_time_list = []
    
    for i in range(len(time_list)):
        time = time_list[i]
        ph = ph_list[i]
        
        if ph<=4.6 or ph>=7.9:
            rec_time_list.append(time)
    
    rec = []
    for time in rec_time_list:
        if dt.time(6,0)<=time<dt.time(8,0):
            rec.append('early-morning')
        elif dt.time(8,0)<=time<dt.time(10,0):
            rec.append('mid-morning')
        elif dt.time(10,0)<=time<dt.time(12,0):
            rec.append('late-morning')
        elif dt.time(12,0)<=time<dt.time(14,0):
            rec.append('early-afternoon')
        elif dt.time(14,0)<=time<dt.time(16,0):
            rec.append('mid-afternoon')
        elif dt.time(16,0)<=time<dt.time(18,0):
            rec.append('late-afternoon')
        elif dt.time(18,0)<=time<dt.time(21,0):
            rec.append('evening')
        elif dt.time(21,0)<=time<=dt.time(23,59):
            rec.append('night')
        elif dt.time(0,0)<=time<dt.time(3,0):
            rec.append('late-night')
        elif dt.time(3,0)<=time<dt.time(6,0):
            rec.append('toward-morning')
        else:
            pass
    
    rec = list(set(rec))

    if len(rec)==0:
        return 'Good job drinking water throughout the day!'
    elif len(rec)==1:
        return f"""Your urine pH dropped below healthy levels during {rec[0]}, make sure to consciously drink water during {rec[0]}."""
    else:
        return f"""Your urine pH dropped below healthy levels during {", ".join(rec[:-1]) + ' and ' + rec[-1]}, make sure to consciously drink water during {", ".join(rec[:-1]) + ' and ' + rec[-1]}."""


def ph_chart(urine_ph):
    fig, ax = plt.subplots(figsize=(1, 6))
    fig.suptitle('Urine pH Scale')

    cmap = mpl.colors.ListedColormap(['#fe1321', '#fe531a', '#ffa400', 
                                      '#ffcc01', '#dbe000', '#6ed700', 
                                      '#00b601', '#038503', '#00a654', 
                                      '#00c1b9', '#008bca', '#014bca', 
                                      '#3421b9', '#480da7', '#3e0890'])

    bounds = [i for i in range(15)]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    cbar = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
                                    boundaries=bounds,
                                    norm=norm,
                                    ticks=bounds,
                                    orientation='vertical')
    
    ax.annotate("Your average urine pH", xy=(0, urine_ph), xytext=(-3, urine_ph),
            arrowprops=dict(arrowstyle="->"))
    ax.annotate("Upper healthy pH limit", xy=(0, 8), xytext=(-3, 8),
            arrowprops=dict(arrowstyle="->"), c='b')
    ax.annotate("Lower healthy pH limit", xy=(0, 4.5), xytext=(-3, 4.5),
            arrowprops=dict(arrowstyle="->"), c='r')

    cbar.ax.set_yticklabels(['acidic']+[str(i) for i in range(1,14)]+['alkaline'])
    
    
    return fig


def avg_ph(ph_list):
    n = len(ph_list)
    avg = sum(ph_list) / n
    return avg


def avg_color(color_list):
    avg = statistics.mode(color_list)
    return avg