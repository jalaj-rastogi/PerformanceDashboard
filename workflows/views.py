from django.shortcuts import render
from django.http import JsonResponse
from django.urls import resolve
from django.conf import settings
from .models import Workflow
from . import utils

import altair as alt
import json
import os
import pandas as pd

# Create your views here.
def workflows(request):

    workflow_objects = Workflow.objects.all()
    workflow_testlist = [w.name.lower().replace(" ", '-') for w in workflow_objects]

    workflow_filepath_list = []
    for dir_name in workflow_testlist:
        workflow_filepath_list.append(utils.read_file(dir_name))

    workflow_filepath_list_dropnone = [i for i in workflow_filepath_list if i]
    chart_list = [None for i in workflow_filepath_list]
    
    count = 0
    for fname in workflow_filepath_list_dropnone:
        raw_list = utils.create_raw_list(fname)
        df_list = utils.create_df_list(raw_list)
        iteration_list = ['Run-' + str(i) for i in range(1, len(df_list)+1)]
        x = utils.max_iteration_time(iteration_list, df_list)
        chart = x.to_json(indent=None)
        chart_list[count] = chart
        count += 1

    # raw_list = utils.read_file()
    # print(raw_list)
    # df_list = utils.create_df_list(raw_list)
    # iteration_list = ['Iteration-' + str(i) for i in range(1, len(df_list)+1)]
    # trust_iteration_list = df_list[0].TrustID.tolist()
    context = {
        'workflow_objects': workflow_objects,
        'chart_list' : chart_list
    }
    # context = {'iteration_list': iteration_list, 'trust_iteration_list': trust_iteration_list}
    # settings.result_df = df_list

    return render(request, 'workflows/workflows.html', context=context)


def dailyworkflow(request):
    workflow_objects = Workflow.objects.all()
    workflow_names = [w.name for w in workflow_objects]
    workflow_url = [ w.slug for w in workflow_objects]
    current_url = resolve(request.path_info).url_name
    workflow_filepath = ""
    for i in workflow_url:
        if i == current_url:
            workflow_filepath = utils.read_file(i)

    fname = os.path.basename(workflow_filepath)
    client = os.path.splitext(fname)[0].split('_')[0]
    # print(workflow_filepath)

    raw_list = utils.create_raw_list(workflow_filepath)
    df_list = utils.create_df_list(raw_list)
    settings.result_df = df_list

    # Iteration list df for tables
    iteration_df = utils.max_iteration_df(df_list)
    iteration_list = iteration_df['Iterations'].tolist()
    iteration_time = iteration_df['Time (in sec)'].tolist()
    min_iteration_time = iteration_df['MinTime'].tolist()
    iteration_chart = utils.max_iteration_time_axis(iteration_df, "Max Time For Iteration")
    iterations_json = iteration_chart.to_json(indent=None)


    # Trust List and max time list for tables
    max_trusttime_df = utils.max_trust_df(df_list)
    trust_list = max_trusttime_df.index.tolist()
    max_time_list = max_trusttime_df['Time(in sec)'].tolist()
    min_time_list = max_trusttime_df['MinTime'].tolist()
    trust_time_chart = utils.max_trust_time_chart(max_trusttime_df, "Trust vs Maximum Time")
    trust_time_json = trust_time_chart.to_json(indent=None)

    # Count for Top cards
    iteration_count = len(df_list)
    trust_count = len(df_list[0])
    
    workflow_zip = zip(workflow_names, workflow_url)
    context = {
        'workflow_objects': workflow_zip,
        'client': client,
        'trust_count': trust_count,
        'iteration_count': iteration_count,
        'max_trusttime': zip(trust_list, max_time_list, min_time_list),
        'trust_time_chart': trust_time_json,
        'max_runtime': zip(iteration_list, iteration_time, min_iteration_time),
        'iterations_chart': iterations_json
    }
    return render(request, 'workflows/daily-workflow.html', context=context)


def alltrusts(request):
    workflow_objects = Workflow.objects.all()
    workflow_names = [w.name for w in workflow_objects]
    workflow_url = [ w.slug for w in workflow_objects]

    result = settings.result_df
    x = utils.all_trust_chart(result)
    chart = x.to_json(indent=None)

    context = {
        'workflow_objects': zip(workflow_names, workflow_url),
        'chart': chart
    }

    return render(request, 'workflows/all-trusts.html', context=context)


def alliterations(request):
    workflow_objects = Workflow.objects.all()
    workflow_names = [w.name for w in workflow_objects]
    workflow_url = [ w.slug for w in workflow_objects]

    result = settings.result_df
    x = utils.all_iteration_chart(result)
    chart = x.to_json(indent=None)

    context = {
        'workflow_objects': zip(workflow_names, workflow_url),
        'chart': chart
    }

    return render(request, 'workflows/all-trusts.html', context=context)


def trustypechart(request):
    trust_type = request.GET.get('trust_type', None)
    df_list = settings.result_df
    max_trusttime_df = utils.max_trust_df(df_list)
    title = ""
    if trust_type == "max":
        title = "Trust vs Maximum Time"
    elif trust_type == "min":
        title = "Trust vs Minimum Time"
    elif trust_type == "avg":
        title = "Trust vs Average Time"
    
    trust_time_chart = utils.max_trust_time_chart(max_trusttime_df, title, trust_type)
    trust_time_json = trust_time_chart.to_json(indent=None)
    data = {
        'trust_type_chart': trust_time_json
    }
    return JsonResponse(data)


def trust_all_type_chart(request):
    switchstatus = request.GET.get('switchstatus', None)
    df_list = settings.result_df
    max_trusttime_df = utils.max_trust_df(df_list)
    chart1 = utils.max_trust_time_chart(max_trusttime_df, "Trust vs Maximum Time", "max")
    chart2 = utils.max_trust_time_chart(max_trusttime_df, "Trust vs Minimum Time", "min")
    chart3 = utils.max_trust_time_chart(max_trusttime_df, "Trust vs Average Time", "avg")
    z = alt.ConcatChart(concat=[chart1,chart2,chart3], columns=1)
    
    trust_alltype = z.to_json(indent=None)
    data = {
        'trust_alltype': trust_alltype
    }
    return JsonResponse(data)
