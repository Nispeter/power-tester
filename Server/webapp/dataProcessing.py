from flask import Flask, request, render_template, abort, url_for, redirect, make_response, jsonify
from flask_cors import CORS
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import random
import socket
import json
import threading as th
import time
from statistics import mean
import plotly.graph_objects as go
import plotly.offline as pyo
import sys
import numpy as np


# Define colors, units of measurement, and titles for graphs
color = ['red', 'green', 'blue', 'orange', 'purple']
unidadesdemedida = ['Joules', 'Joules', 'Joules', 'Instrucciones', 'Lecturas', 'Fallos', 'Escrituras', 'Fallos', 'Lecturas', 'Fallos', 'Escrituras', 'Fallos', 'Referencias', 'Saltos', 'Fallos', 'Ciclos', 'Nanosegundos']
titulos = ['Energía de Nucleos', 'Energía de Paquete', 'Energía de RAM', 'Instrucciones', 'Lecturas de LLC', 'Fallos de lectura de LLC', 'Escrituras de LLC', 'Fallas de escritura de LLC', 'Lecturas de L1D', 'Fallas de lectura de L1D', 'Escrituras de L1D', 'Fallos de caché', 'Referencias de caché', 'Saltos', 'Fallas en saltos', 'Ciclos de CPU', 'Tiempo de ejecución']


# Function to plot and save graphs from measurement results
def create_directory(names):
    for name in names:
        print("Creating directory for " + name + "!")
        subprocess.run(["/bin/mkdir", "static/" + name], universal_newlines=True)

def read_csv_data(name):
    nameresult = name + "Results" + str(0) + ".csv"
    return pd.read_csv(nameresult)


def calculate_normalized_power(csvobj):
    for i in range(3):
        aux2 = []
        for j in range(30):
            print(j)
            temp = csvobj.iloc[j, 16] / float(10**9)
            temp2 = csvobj.iloc[j, i] / temp
            temp2 = round(temp2, 3)
            aux2.append(temp2)
        if i == 0:
            csvobj['PowerCores'] = aux2
        if i == 1:
            csvobj['PowerPkg'] = aux2
        if i == 2:
            csvobj['PowerRAM'] = aux2
    return csvobj

def save_normalized_data(name, csvobj):
    with open("static/"+name+"/"+name+"ResultsFinal.csv", 'x') as w:
        csvobj.to_csv(w, index=False)


def plot_common_plotly(columni, csvobjs, ax, names):
    # Create the base figure
    fig = go.Figure()

    for name, csvobj in zip(names, csvobjs):
        df = csvobj.copy()
        test = df.iloc[:, columni]

        # Handle non-numeric data
        test.replace('<not-counted>', np.nan, inplace=True)
        test = pd.to_numeric(test, errors='coerce')

        if columni < 3:
            test2 = df.iloc[:, columni + 17]
            
            # Handle non-numeric data for test2
            test2.replace('<not-counted>', np.nan, inplace=True)
            test2 = pd.to_numeric(test2, errors='coerce')

            # Bar trace
            fig.add_trace(go.Bar(x=df.index, y=test, name=f'{titulos[columni]} - {name}', marker_color='lightblue', yaxis='y1'))

            # Line trace for the twin axes
            fig.add_trace(go.Scatter(x=df.index, y=test2, mode='lines+markers', name=f'Potencia promedio - {name}', line=dict(color='red', dash='dash'), yaxis='y2'))

        else:
            fig.add_trace(go.Scatter(x=df.index, y=test, mode='lines+markers', name=f'{titulos[columni]} - {name}', line=dict(color=color[0], dash='dash')))

    # Configurations for twin axes, if applicable
    if columni < 3:
        fig.update_layout(
            yaxis=dict(title=unidadesdemedida[columni]),
            yaxis2=dict(title='Watts', overlaying='y', side='right')
        )

    # Adjust layout for all cases
    fig.update_layout(
        title=titulos[columni],
        xaxis_title='Iteraciones',
        xaxis=dict(tickvals=list(range(0, 30, 5)))
    )

    # Save the figure as an HTML file
    fig.write_html(f"static/{name}/fig{columni}.html")



def plot_box_plotly(data, name):
    # Replace non-numeric entries
    data.replace('<not-counted>', np.nan, inplace=True)

    # Convert columns to float type
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    data_columns = [col for col in data.columns if col != 'Increment']

    # Sort the data by 'Increment' to ensure the order on the x-axis
    data.sort_values(by='Increment', inplace=True)

    for columni, col in enumerate(data_columns, 1):
        # Create a new figure
        fig = go.Figure()

        # Extract the box data for each increment
        box_data = [data[data['Increment'] == increment][col].dropna().values for increment in data['Increment'].unique()]

        # Create the box traces
        for i, increment in enumerate(data['Increment'].unique(), 1):
            fig.add_trace(go.Box(y=box_data[i-1], name=str(increment), marker_color='lightblue', line_color='black'))

        # Median trace
        medians = [np.median(b_data) for b_data in box_data if len(b_data) > 0]
        fig.add_trace(go.Scatter(x=list(data['Increment'].unique()), y=medians, mode='lines', name='Medians', line=dict(color='red')))

        # Adjust layout
        fig.update_layout(
            title=f"Box plot for {col}",
            xaxis_title='Increment',
            yaxis_title='Value',
        )

        # Save the plot as HTML
        fig.write_html(f"static/{name}/fig{columni}.html")  



def plot_graphs(names, csvobjs):
        nameresult = names[0] + "Results" + str(0) + ".csv"
        for columni in range(17):
            fig, ax = plt.subplots()
            # df = csvobj
            # test = csvobj.iloc[:, columni]
            
            plot_common_plotly(columni, csvobjs,ax,  names)
            plt.close(fig)

        subprocess.run(["/bin/mv", nameresult, "static/" + names[0]])
        print("Done!")

def graph_results(names):
    create_directory(names)
    all_csvobjs = []
    csvobj = read_csv_data(names[0])                    #Identify the task 
    has_increment = csvobj.columns[0] == "Increment"    #Identify the task 
    
    if has_increment:
        for name in names:
            all_csvobjs.append(read_csv_data(name))
        plot_box_plotly(all_csvobjs, names)
    else: 
        for name in names:
            csvobj = read_csv_data(name)
            csvobj = calculate_normalized_power(csvobj)
            save_normalized_data(name, csvobj)
            all_csvobjs.append(pd.read_csv("static/"+name+"/"+name+"ResultsFinal.csv",))
        print(all_csvobjs)
        plot_graphs(names, all_csvobjs)
