import React, { useState } from 'react';

function TaskPage({ onTaskToggle }) {
    const [selectedTaskId, setSelectedTaskId] = useState(null);
    
    const tasks = [
        {
            id: 'lcs',
            title: 'Longest common substring (LCS)',
            description: `
    La tarea LCS se centra en encontrar la subsecuencia común más larga que existe entre dos secuencias. Una subsecuencia es una secuencia que aparece en el mismo orden relativo, pero no necesariamente de forma consecutiva, en ambas secuencias. 
    
    Este problema es un desafío clásico de la informática a menudo encontrado en los dominios de la programación dinámica. Por ejemplo, considera dos secuencias: "ABCDGH" y "AEDFHR". La LCS es "ADH".
    
    Esta tarea te requerirá:
    1. Entender los conceptos básicos de la programación dinámica.
    2. Formular un enfoque recursivo para representar los subproblemas.
    3. Optimizar el enfoque recursivo utilizando memoización o cálculo de abajo hacia arriba para lograr una solución más eficiente.
    
    Las aplicaciones del problema LCS incluyen, pero no se limitan a, utilidades de diferenciación (utilizadas para mostrar diferencias entre archivos), análisis de secuencias de ADN y sistemas de control de versiones.
            `
        },
        {
            id: 'camm',
            title: 'Cache Oblivious Matrix multiplication (COMM)',
            description: `
    La tarea profundiza en el proceso de multiplicación de matrices optimizado para jerarquías de memoria teniendo en cuenta los parámetros específicos de la memoria caché. Los algoritmos conscientes del caché están diseñados para maximizar el uso del caché y minimizar las fallas del caché, lo que mejora el rendimiento general del algoritmo.
    
    Esta tarea te desafiará a:
    1. Captar los fundamentos de las estrategias conscientes del caché y cómo aprovechan las características del caché para mejorar el rendimiento.
    2. Implementar la multiplicación de matrices que logre un rendimiento óptimo al ajustarla para tamaños de caché específicos.
    3. Analizar y comprender el impacto de los patrones de acceso a la memoria y cómo un enfoque consciente del caché busca maximizar el uso eficiente del caché.
    
    La multiplicación de matrices consciente del caché tiene aplicaciones en computación de alto rendimiento, simulaciones científicas y en escenarios donde el rendimiento es crucial.
            `
        }
    ];
    
    

    const handleRadioChange = (taskId, isChecked) => {
        if (isChecked) {
            setSelectedTaskId(taskId);
            onTaskToggle(taskId, isChecked);
        } else {
            setSelectedTaskId(null);
            onTaskToggle(null, isChecked);
        }
    }

    return (
        <div className="container mt-4">
            {tasks.map(task => (
                <div className="card mb-3" key={task.id}>
                    <div className="card-body">
                        <div className="form-check">
                            <input
                                className="form-check-input"
                                type="radio"
                                name="taskToggle"
                                id={task.id}
                                checked={selectedTaskId === task.id}
                                onChange={(e) => handleRadioChange(task.id, e.target.checked)}
                            />
                            <label className="form-check-label" htmlFor={task.id}>
                                {task.title} {selectedTaskId !== task.id && '(Expand for description)'}
                            </label>
                        </div>
                        {selectedTaskId === task.id && (
                            <div className="mt-2">
                                <p>{task.description}</p>
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default TaskPage;
