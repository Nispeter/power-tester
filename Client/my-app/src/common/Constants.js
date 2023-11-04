
export const serverURL = "http://127.0.0.1:5000/";
export const baseURL = serverURL + "sendcode";
export const statusURL = serverURL + "checkstatus/";
export default function getTask(taskState){
    if(taskState.lcs)
    return "LCS";
    else if (taskState.camm){
        return "CAMM";
    }
    return "";
}


