import pandas as pd
import numpy as np
import altair as alt
import re
import os
from django.conf import settings

def read_file(workflow_folder_name):
    parent_dir = os.path.join(settings.MEDIA_ROOT, 'PerformanceResults')

    for f in os.scandir(parent_dir):
        if f.name == workflow_folder_name:
            result_dir = os.path.join(parent_dir, workflow_folder_name)
            fname = ""
            
            for file in os.listdir(result_dir):
                if file.endswith(".txt"):
                    fname = os.path.join(result_dir, file)
            
            return fname
        else:
            return None


def create_raw_list(fname):
    f = open(fname)
    lines = f.readlines()
    rng = len(lines)
    my_lt = []
    for i in range(2, rng, 4):
        if i < rng:
            x = lines[i]
            my_lt.append(re.split(r'\t+', x))
        
    f.close()

    return my_lt


def hms_to_sec(val):
    l = val.split(':')
    sec = int(l[1])*60 + int(l[2])
    return sec


def create_df_list(my_lt):
    result = []

    for i in my_lt:
        trust_with_task_list = i[0].split(',')
        task_trust_dict = {val.strip().split('-')[1].strip():val.strip().split('-')[0].strip()  for val in trust_with_task_list}

        task_with_timestamp = i[1].split(',')
        task_timestamp_dict = {val.strip().split('-')[1].strip():val.strip().split('-')[0].strip()  for val in task_with_timestamp}

        df1 = pd.DataFrame(task_trust_dict.values(), index=task_trust_dict.keys())
        df1.rename(columns={0:"TrustID"}, inplace=True)

        df2 = pd.DataFrame(task_timestamp_dict.values(), index=task_timestamp_dict.keys())
        df2.rename(columns={0:"Time Taken (h:m:s)"}, inplace=True)

        final_df = df1.join(df2)

        final_df["Time(in sec)"] = final_df["Time Taken (h:m:s)"].apply(hms_to_sec)
        
        result.append(final_df)

    return result


def make_chart(df):
    selection = alt.selection_interval(encodings=['x'])

    colorCondition = alt.condition(selection, alt.value('lightgreen'), alt.value('gray'))

    x = alt.Chart(df).mark_bar().encode(
        x=alt.X('TrustID', sort='-x'),
        y=alt.Y('Time(in sec)', scale=alt.Scale(domain=[0, 300])),
        tooltip = ['TrustID', 'Time Taken (h:m:s)'],
        color=colorCondition
    ).interactive().add_selection(selection).properties(
        width=500,
        height=400
    )
    
    return x


def trust_frame(result_frames, trust_id):
    #trust_id = "ODART20181"
    trust_dframe = None
    for dframe in result_frames:
        trust_row = dframe[dframe['TrustID'] == trust_id]
        if trust_dframe is None:
            trust_dframe = trust_row
        else:
            trust_dframe = pd.concat([trust_dframe, trust_row], axis=0)
        
    return trust_dframe


def trust_chart(trust_frame, trust_id):
    x = alt.Chart(trust_frame.reset_index()).mark_bar().encode(
        x=alt.X('index', axis=None),
        y=alt.Y('Time(in sec)', scale=alt.Scale(domain=[0, 300])),
        tooltip=['Time(in sec)'],
        color=alt.value('lightgreen'),
    ).properties(title=trust_id, width=200, height=200)
    
    return x


def max_trust_time_chart(trust_frame, title, type="max"):
    if type == "avg":
        x = alt.Chart(trust_frame.reset_index()).mark_bar().encode(
                x=alt.X('TrustID'),
                y=alt.Y('AvgTime', scale=alt.Scale(domain=[0, 350])),
                tooltip = ['AvgTime'],
                color=alt.Color('AvgTime' ,scale=alt.Scale(scheme="blues"), legend=None)
            ).properties(
                    width=700,
                    height=300,
                    title=title
            )

    elif type == "min":
        x = alt.Chart(trust_frame.reset_index()).mark_bar().encode(
                x=alt.X('TrustID'),
                y=alt.Y('MinTime', scale=alt.Scale(domain=[0, 350])),
                tooltip = ['MinTime'],
                color=alt.Color('MinTime' ,scale=alt.Scale(scheme="blues"), legend=None)
            ).properties(
                    width=700,
                    height=300,
                    title=title
            )

    else:
        x = alt.Chart(trust_frame.reset_index()).mark_bar().encode(
                x=alt.X('TrustID'),
                y=alt.Y('Time(in sec)', scale=alt.Scale(domain=[0, 350])),
                tooltip = ['Time(in sec)'],
                color=alt.Color('Time(in sec)' ,scale=alt.Scale(scheme="blues"), legend=None)
            ).properties(
                    width=700,
                    height=300,
                    title=title
            )

    return x


def max_iteration_df(result):
    iteration_list = ['Iteration-' + str(i) for i in range(1, len(result)+1)]
    max_time = []
    min_time = []
    for dframe in result:
        max_time.append(dframe['Time(in sec)'].max())
        min_time.append(dframe['Time(in sec)'].min())

    max_df = pd.DataFrame({"Iterations":iteration_list, "Time (in sec)": max_time, "MinTime":min_time})
    return max_df


def max_iteration_time(iteration_list, result):
    max_time = []

    for dframe in result:
        max_time.append(dframe['Time(in sec)'].max())

    max_df = pd.DataFrame({"Iterations":iteration_list, "Time (in sec)": max_time})

    x = alt.Chart(max_df).mark_bar().encode(
                x=alt.X('Iterations', axis=None),
                y=alt.Y('Time (in sec)', axis=None),
                tooltip = ['Time (in sec)'],
                color = alt.Color('Time (in sec)' ,scale=alt.Scale(scheme="lighttealblue"), legend=None)
        ).properties(
                width=300,
                height=250
        ).configure_axis(grid=False, domain=False).configure(background='#fcfcfa')

    return x


def max_iteration_time_axis(max_df, title):
    x = alt.Chart(max_df).mark_bar().encode(
                x=alt.X('Iterations'),
                y=alt.Y('Time (in sec)', scale=alt.Scale(domain=[0, 300])),
                tooltip = ['Time (in sec)'],
                color = alt.Color('Time (in sec)' ,scale=alt.Scale(scheme="lighttealblue"), legend=None)
        ).properties(
                width=325,
                height=300,
                title=title
        )

    y = alt.Chart(max_df).mark_bar().encode(
                x=alt.X('Iterations'),
                y=alt.Y('MinTime', scale=alt.Scale(domain=[0, 300])),
                tooltip = ['MinTime'],
                color = alt.Color('MinTime' ,scale=alt.Scale(scheme="greens"), legend=None)
        ).properties(
                width=325,
                height=300,
                title="Min Time for Iteration"
        )

    z = alt.ConcatChart(concat=[x,y])

    return z

def max_trust_df(result):
    trust_list = result[0].TrustID.tolist()
    new_res = [df.reset_index().drop('index', axis=1) for df in result]
    new_concat = pd.concat(new_res, axis=0)
    ultimate = new_concat[['TrustID', 'Time(in sec)']].groupby('TrustID').max('Time(in sec)')
    ultimate_min = new_concat[['TrustID', 'Time(in sec)']].groupby('TrustID').min('Time(in sec)')
    ultimate_avg = new_concat[['TrustID', 'Time(in sec)']].groupby('TrustID').mean('Time(in sec)')
    ultimate['MinTime'] = ultimate_min['Time(in sec)']
    ultimate['AvgTime'] = ultimate_avg['Time(in sec)']
    return ultimate


def all_trust_chart(result):
    trust_iteration_list = result[0].TrustID.tolist()
    chart_list = []
    for i in trust_iteration_list:
        get_trust = i
        trust_df = trust_frame(result, get_trust)
        chart = trust_chart(trust_df, get_trust)
        chart_list.append(chart)

    x = alt.ConcatChart(concat=chart_list, columns=4)

    return x


def all_iteration_chart(result):
    iteration_list = ['Iteration-' + str(i) for i in range(1, len(result)+1)]
    iter_chart_list = []
    for i in iteration_list:
        get_index = str(i).split('-')[1]
        my_index=int(get_index)-1
        chart = make_chart(result[my_index])
        iter_chart_list.append(chart)

    x = alt.ConcatChart(concat=iter_chart_list, columns=2)
    return x