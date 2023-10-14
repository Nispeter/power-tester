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
import sys
import numpy as np


# Define colors, units of measurement, and titles for graphs
color = ['red', 'green', 'blue', 'orange', 'purple']
unidadesdemedida = ['Joules', 'Joules', 'Joules', 'Instrucciones', 'Lecturas', 'Fallos', 'Escrituras', 'Fallos', 'Lecturas', 'Fallos', 'Escrituras', 'Fallos', 'Referencias', 'Saltos', 'Fallos', 'Ciclos', 'Nanosegundos']
titulos = ['Energía de Nucleos', 'Energía de Paquete', 'Energía de RAM', 'Instrucciones', 'Lecturas de LLC', 'Fallos de lectura de LLC', 'Escrituras de LLC', 'Fallas de escritura de LLC', 'Lecturas de L1D', 'Fallas de lectura de L1D', 'Escrituras de L1D', 'Fallos de caché', 'Referencias de caché', 'Saltos', 'Fallas en saltos', 'Ciclos de CPU', 'Tiempo de ejecución']


# Function to plot and save graphs from measurement results
def create_directory(name):
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

def plot_common(columni, csvobj, ax, name):
    df = csvobj
    test = csvobj.iloc[:, columni]
    
    if columni < 3:
        ax2 = ax.twinx()
        test2 = csvobj.iloc[:, columni+17]
        ax.axhline(mean(test), label='Energia promedio', color='orange')
        ax2.axhline(mean(test2), label='Potencia promedio', color='purple')
        df.plot(y=columni, use_index=True, kind='bar', ax=ax, color='lightblue',
                ylabel=unidadesdemedida[columni], legend=None, xlabel='Iteraciones', title=titulos[columni])
        ax.set_ylim(top=max(test)+0.1, bottom=max(min(test)-0.1,0))
        df.plot(y=columni+17, use_index=True, kind='line', ax=ax2, color='red', ylabel='Watts', style='--', marker='.')
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper right')
        plt.xticks(np.arange(0,30, step=5))
    else:
        try:
            df.plot(
                y=columni, use_index=True, color=color[0], title=titulos[columni],
                legend=None, xlabel='Iteraciones',
                ylabel=unidadesdemedida[columni], style='--', marker='.', ax=ax, label="")
            ax.axhline(mean(test), label='Promedio', color='orange')
        except TypeError:
            print("err: ", TypeError)
    
    if columni > 3:
        plt.ticklabel_format(scilimits=[-5,5])
    plt.minorticks_on()
    plt.grid()
    if ax.lines:
        plt.savefig("static/" + name + "/fig" + str(columni) + ".svg", format='svg')

def plot_box(data, name):
    data.replace('<not-counted>', np.nan, inplace=True)
    
    # Use non-interactive backend
    plt.switch_backend('Agg')

    # Convert to float type
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    data_columns = [col for col in data.columns if col != 'Increment']

    for columni, col in enumerate(data_columns, 1):
        medians = []
        fig, ax = plt.subplots(figsize=(12, 8))

        # Extract the box data for each increment
        box_data = [data[data['Increment'] == increment][col].dropna().values for increment in data['Increment'].unique()]
        
        # Create the box and whisker plot
        boxes = ax.boxplot(box_data, whis=1.5, vert=True, patch_artist=True, medianprops=dict(color="black"))
        
        # Coloring the boxes
        for patch in boxes['boxes']:
            patch.set_facecolor('lightblue')
        
        # Median values
        for median in boxes['medians']:
            medians.append(median.get_ydata()[0])

        # Line connecting medians
        ax.plot(np.arange(1, len(data['Increment'].unique()) + 1), medians, color="red", label="Medians")
        
        # Grid
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        # Title and labels
        ax.set_title(f"Box plot for {col}")
        ax.set_xlabel('Increment')
        ax.set_ylabel('Value')
        
        # Setting x ticks labels as Increment values
        ax.set_xticks(np.arange(1, len(data['Increment'].unique()) + 1))
        ax.set_xticklabels(data['Increment'].unique())

        # Save the plot
        plt.tight_layout()
        plt.savefig(f"static/{name}/fig{columni}.svg", format='svg')
        plt.close()  # close the figure to free up memory


def plot_graphs(name, csvobj):
    nameresult = name + "Results" + str(0) + ".csv"

    for columni in range(17):
        fig, ax = plt.subplots()
        df = csvobj
        test = csvobj.iloc[:, columni]

        plot_common(columni, csvobj, ax, name)
        plt.close(fig)

    subprocess.run(["/bin/mv", nameresult, "static/" + name])
    print("Done!")

def graph_results(name):
    create_directory(name)
    csvobj = read_csv_data(name)
    has_increment = csvobj.columns[0] == "Increment"
    
    if has_increment:
        plot_box(csvobj, name)
    else: 
        csvobj = calculate_normalized_power(csvobj)
        save_normalized_data(name, csvobj)
        plot_graphs(name, csvobj)
