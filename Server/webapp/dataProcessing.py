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

def plot_box(name, csvobj):
    """Function to plot box graphs for the provided statistics CSV object."""
    for column in csvobj.columns:
        if column != "Increment":
            fig, ax = plt.subplots()
            
            # Extract the relevant statistics for the current column
            stats_data = csvobj[column].values
            
            # Plot a boxplot for the current column
            ax.boxplot(stats_data)
            ax.set_title(f"Box plot for {column}")
            ax.set_ylabel(column)
            ax.set_xticklabels([column])
            
            if ax.lines:
                plt.savefig("static/" + name + "/fig" + str(columni) + ".svg", format='svg')
            plt.close(fig)


def plot_graphs(name, csvobj):
    nameresult = name + "Results" + str(0) + ".csv"
    
    # Check if the first column is "Increment"
    has_increment = csvobj.columns[0] == "Increment"

    for columni in range(17):
        fig, ax = plt.subplots()
        df = csvobj
        test = csvobj.iloc[:, columni]
        
        if has_increment:
            ax.set_title(f"Graph for Increment: {test[0]}")
        else:
            plot_common(columni, csvobj, ax, name)
        plt.close(fig)

    subprocess.run(["/bin/mv", nameresult, "static/" + name])
    print("Done!")

def graph_results(name):
    create_directory(name)
    csvobj = read_csv_data(name)
    csvobj = calculate_normalized_power(csvobj)
    save_normalized_data(name, csvobj)
    plot_graphs(name, csvobj)

