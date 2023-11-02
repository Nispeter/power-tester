function getUrl(taskState) {
    const baseURL = "http://127.0.0.1:5000/";
    
    if (taskState.lcs) {
        return baseURL + "submit/lcs";
    } else if (taskState.camm) {
        return baseURL + "submit/camm";
    }
    return baseURL + "sendcode";
}