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


def plot_common_plotly(columni, csvobjs, ax, names, nameFiles):
    # Create the base figure
    fig = go.Figure()
    file_count = 0
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
            fig.add_trace(go.Bar(x=df.index, y=test, name=f'{titulos[columni]} - {nameFiles[file_count]}', marker_color='lightblue', yaxis='y1'))

            # Line trace for the twin axes
            fig.add_trace(go.Scatter(x=df.index, y=test2, mode='lines+markers', name=f'Potencia promedio - {name}', line=dict(color='red', dash='dash'), yaxis='y2'))
            file_count+=1
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

def plot_box_plotly(csvobjs, names, nameFiles, input_size):
    input_size = int(input_size)
    # Assuming all CSV objects have the same column structure
    print("input size: ", input_size)
    if csvobjs:
        nameresult = names[0] + "Results" + str(0) + ".csv"
        data_columns = [col for col in csvobjs[0].columns if col != 'Increment']
        fig_number = 0 
        for col in data_columns:
            # Create a new figure for each column
            fig = go.Figure()
            file_count = 0
            for data, name in zip(csvobjs, names):
                # Replace non-numeric entries
                data.replace('<not-counted>', np.nan, inplace=True)
                # Convert columns to float type
                data[col] = pd.to_numeric(data[col], errors='coerce')

                # Group data by increment and calculate median and interquartile range
                grouped_data = data.groupby('Increment')[col].agg(['median', lambda x: x.quantile(0.75) - x.quantile(0.25)])
                grouped_data = data.groupby('Increment')[col].agg(
                    median=('median'),
                    iqr=(lambda x: x.quantile(0.75) - x.quantile(0.25))
                )
                increments = np.linspace(0, input_size, len(grouped_data))
                # Create the line trace with error bars for this CSV object
                fig.add_trace(go.Scatter(
                    x=increments,
                    y=grouped_data['median'],
                    error_y=dict(type='data', array=grouped_data['iqr'], visible=True),
                    mode='lines+markers',
                    name=f'{col} - {nameFiles[file_count]}'
                ))
                file_count+=1
                # Adjust layout
                fig.update_layout(
                    title=f"{col}",
                    yaxis_title=unidadesdemedida[fig_number],
                    xaxis_title='Input Size'
                )
                
                # Save the plot as HTML
            fig.write_html(f"static/{name}/fig{fig_number}.html")
            fig_number += 1  # Increment the figure number
        subprocess.run(["/bin/mv", nameresult, "static/" + names[0]])



def plot_graphs(names, csvobjs, nameFiles):
        nameresult = names[0] + "Results" + str(0) + ".csv"
        for columni in range(17):
            fig, ax = plt.subplots()
            # df = csvobj
            # test = csvobj.iloc[:, columni]
            
            plot_common_plotly(columni, csvobjs,ax,  names, nameFiles)
            plt.close(fig)

        subprocess.run(["/bin/mv", nameresult, "static/" + names[0]])
        print("Done!")

def graph_results(names, nameFiles, input_size):
    create_directory(names)
    all_csvobjs = []
    csvobj = read_csv_data(names[0])                    #Identify the task 
    has_increment = csvobj.columns[0] == "Increment"    #Identify the task 
    print("names, size : ",nameFiles, input_size)
    if has_increment:
        for name in names:
            csvobj = read_csv_data(name)
            save_normalized_data(name, csvobj)
            all_csvobjs.append(csvobj)
        plot_box_plotly(all_csvobjs, names, nameFiles, input_size)
    else: 
        for name in names:
            csvobj = read_csv_data(name)
            csvobj = calculate_normalized_power(csvobj)
            save_normalized_data(name, csvobj)
            all_csvobjs.append(pd.read_csv("static/"+name+"/"+name+"ResultsFinal.csv",))
        plot_graphs(names, all_csvobjs, nameFiles)
