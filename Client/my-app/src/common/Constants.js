
export const serverURL = "http://127.0.0.1:5000/";
export const baseURL = serverURL + "sendcode";
export const statusURL = serverURL + "checkstatus/";
export default function getTask(taskState){
    console.log("taskstate", taskState);
    if(taskState === 'lcs')
        return "LCS";
    else if (taskState === 'camm'){
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
    }
  ];
