
export const serverURL = "http://127.0.0.1:5000/";
export const baseURL = serverURL + "sendcode";
export const statusURL = serverURL + "checkstatus/";
export default function getTask(taskState){
    console.log("taskstate", taskState);
    if(taskState === 'lcs')
        return "LCS";
    if(taskState === 'size'){
        return "SIZE";
    }
    if (taskState.includes('camm')){
        if(taskState === 'cammr')
            return "CAMMR";
        if(taskState === 'cammso')
            return "CAMMSO";
        if(taskState === 'camms')
            return "CAMMS";
        return "CAMM";
    }
    return "";
}

export const tasks = [
    {
        id: 'none',
        title: 'None',
        description: ``
    },
    {
        id: 'lcs',
        title: 'Text input',
        description: ``
    },
    {
        id: 'camm',
        title: 'Numerical input',
        description: ``
    },
    {
        id: 'size',
        title: 'Input size',
        description: ``
    }
  ];

  export const numericalInputOptions = [
    { value: 'cammr', label: 'Numeros aleatoreos' },
    { value: 'cammso', label: 'Numeros semi-ordenados' },
    { value: 'camms', label: 'Numeros iguales' },
  ];