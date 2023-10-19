import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import "./RenderForm.css";

function RenderForm({ tasksState}) {
  const [code, setCode] = useState("");
  const [codename, setCodename] = useState();
  const [status, setStatus] = useState("Esperando entrada");
  const [check, setCheck] = useState(true);
  const [name, setName] = useState("test");
  var flag = "";
  var intervalID = 0;
  let navigate = useNavigate();

  useEffect(() => {
    document.title = "Power Tester";
  }, []);
  
  function handleSubmit(event) {
    alert("¡Enviado! Espere por el estado del código");
    event.preventDefault();
    setStatus("Esperando respuesta");
    var bodyFormData = new FormData();
    if (code) {
      bodyFormData.append("code", code);
    }

    let url = "http://127.0.0.1:5000/sendcode"; 
    if (tasksState.lcs) {
      url = "http://127.0.0.1:5000/submit/lcs";
    } else if (tasksState.camm) {
      url = "http://127.0.0.1:5000/submit/camm"; 
    }

    axios({
      method: "post",
      url: url,
      data: bodyFormData,
      headers: { "Content-Type": "multipart/form-data" },
    })
      .then((response) => {
        console.log(response.data, codename);
        setCodename(response.data);
        intervalID = setInterval(getStatusfromServer, 5000, response.data);
      })
      .catch((response) => {
        console.log(response);
      });
  }

  function handleChange(event) {
    setCode(event.target.value);
    setCheck(true);
  }
  function handleChange2(event) {
    setName(event.target.value);
  }

  const fileInput = React.useRef(null);
  function handleFileChange(event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => setCode(e.target.result);
      reader.readAsText(file);
    }
  }

  function getStatusfromServer(match) {
    axios
      .get("http://127.0.0.1:5000/checkstatus/" + match)
      .then((response) => {
        if (response.data === "IN QUEUE") setStatus("En cola");
        else if (response.data === "DONE") setStatus("Listo");
        else setStatus(response.data);
        flag = response.data;
      })
      .catch((response) => {});
    var tmp = flag.split(":");
    console.log(tmp, flag);
    if (flag === "DONE" || tmp[0] === "ERROR") {
      clearInterval(intervalID);
      if (flag === "DONE") setCheck(false);
    }
  }

  return (
    <React.Fragment>
      <form onSubmit={handleSubmit}>
      <div className="container">
        <div className="row">
          <div className="col-6">
            <div className="card border-0 shadow ">
              <div className="card-body">
                <div>
                  <label htmlFor="title">
                    Ingrese un nombre al código (para identificarlo en ventanas
                    o pestañas)
                  </label>
                  <br />
                  <input type="text" value={name} onChange={handleChange2} />
                </div>
                <div>
                  <label htmlFor="code">Inserte código </label>
                </div>
                <textarea
                  type="text"
                  id="code"
                  name="code"
                  rows="15" // Adjusted rows to fit content
                  cols="78"
                  value={code}
                  onChange={handleChange}
                ></textarea>
                <label for="formFileDisabled" class="form-label">
                  Disabled file input example
                </label>
                <input ref={fileInput} class="form-control" type="file" id="formFile" onChange={handleFileChange}/>
                <input type="submit" className="buttonv" value="Subir" />
              </div>
            </div>
          </div>

          <div className="col-6">
            <div className="card border-0 shadow ">
              <div className="card-body">
                <h2> Estado del Código </h2>
                <div>
                  <textarea
                    type="text"
                    id="status"
                    value={status}
                    disabled
                    rows="15" // Adjusted rows to fit content
                    cols="78"
                  ></textarea>
                </div>
                <button
                  type="button"
                  className="buttonv"
                  onClick={() =>
                    navigate("/code/" + codename, {
                      replace: false,
                      state: { name: name },
                    })
                  }
                  disabled={check}
                >
                  Ver estadísticas
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      </form>
    </React.Fragment>
  );
}

export default RenderForm;
