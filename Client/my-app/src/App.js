import React, { Component , useState} from "react";
import {BrowserRouter, Routes, Route, useParams, useNavigate} from "react-router-dom"

const axios = require("axios").default;

class App extends Component {
  render() {
    return (
      <div>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={
              <RenderForm/>
              }
            ></Route>
            <Route path="/code/:codename" element={
              <RenderImage/>
            }></Route>
          </Routes>
        </BrowserRouter>
      </div>
    )
  }
}

class RenderTable extends Component {
  constructor(props){
    super(props);
    this.state={
      EnergyCores: '',
      EnergyPkg: '',
      EnergyRAM: '', 
      Instructions: '', 
      LLCLoads: '',
      LLCLoadMisses: '',
      LLCStores: '',
      LLCStoresMisses: '',
      L1DcacheLoads: '',
      L1DcacheLoadMisses: '',
      L1DcacheStores: '',
      CacheMisses: '',
      CacheReferences: '',
      Branches: '',
      BranchMisses: '', 
      CpuCycles: '',
      DurationTime: '',
      PowerCores : '',
      PowerPkg: '',
      PowerRAM: ''}
  }

  componentDidMount(){
    axios({
      url: 'http://keira.inf.udec.cl/'+this.props.code+'/mean',
        method: 'GET'
      })
    .then((response) => {
      this.setState(response.data)
      this.setState({
        BranchMisses: response.data['Branch-Misses']
      })
    });
  }

  render(){
    return(
      <React.Fragment>
        <div>
          <table style={{width: "50%"} }>
            <tr>
              <td className="dataName">Energía de Nucleos (J):</td>
              <td>{this.state.EnergyCores}</td>
              <td className="dataName">Energía de Paquete (J):</td>
              <td>{this.state.EnergyPkg}</td>
              <td className="dataName">Energía de RAM (J):</td>
              <td>{this.state.EnergyRAM}</td>
              <td className="dataName">Instrucciones:</td>
              <td>{this.state.Instructions}</td>
            </tr>
            <tr>
              <td className="dataName">Cargas de caché último nivel:</td>
              <td>{this.state.LLCLoads}</td>
              <td className="dataName">Fallos de caché último nivel:</td>
              <td>{this.state.LLCLoadMisses}</td>
              <td className="dataName">Guardados de caché último nivel:</td>
              <td>{this.state.LLCStores}</td>
              <td className="dataName">Fallos de guardado de caché último nivel:</td>
              <td>{this.state.LLCStoresMisses}</td>
            </tr>
            <tr>
              <td className="dataName">Cargas de caché nivel 1:</td>
              <td>{this.state.L1DcacheLoads}</td>
              <td className="dataName">Fallos de caché nivel 1:</td>
              <td>{this.state.L1DcacheLoadMisses}</td>
              <td className="dataName">Guardados de caché nivel 1:</td>
              <td>{this.state.L1DcacheStores}</td>
              <td className="dataName">Fallos generales de caché:</td>
              <td>{this.state.CacheMisses}</td>
            </tr>
            <tr>
              <td className="dataName">Referencias de caché:</td>
              <td>{this.state.CacheReferences}</td>
              <td className="dataName">Saltos:</td>
              <td>{this.state.Branches}</td>
              <td className="dataName">Fallos de Saltos:</td>
              <td>{this.state.BranchMisses}</td>
              <td className="dataName">Ciclos de CPU:</td>
              <td>{this.state.CpuCycles}</td>
            </tr>
            <tr>
              <td className="dataName">Tiempo de ejecución (ns):</td>
              <td>{this.state.DurationTime}</td>
              <td className="dataName">Potencia de Núcleos (W):</td>
              <td>{this.state.PowerCores}</td>
              <td className="dataName">Potencia de Paquete (W):</td>
              <td>{this.state.PowerPkg}</td>
              <td className="dataName">Potencia de RAM (W):</td>
              <td>{this.state.PowerRAM}</td>
            </tr>
          </table>
        </div>
      </React.Fragment>
    )
  }
}


function RenderImage(props){
  let asd2 = useNavigate();
  var asd = useParams().codename;
  const link = "http://keira.inf.udec.cl/static/"+asd+"/";
  return (
    <div>
      <div class="row">
        <button type="button" className="buttonv" onClick={()=>asd2(-1)}> Volver</button>
        <button type="button" className="buttonv" onClick={handleDownload} style={{float: "right"}}> Descargar CSV </button>
      </div>
      <div class="cat">
        <h2>Tabla de Promedios</h2>
        <RenderTable code={asd}/>
      </div>
      <div class="cat">
        <h2>Energía y rendimiento de CPU</h2>
        <div class="row">
          <img src={link+"fig0.svg"} alt="img0"></img>
          <img src={link+"fig1.svg"} alt="img1"></img>
        </div>
        <div class="row">
          <img src={link+"fig2.svg"} alt="img2"></img>
          <img src={link+"fig3.svg"} alt="img3"></img>
        </div>
        <div>
          <img src={link+"fig16.svg"} alt="img16"></img>
          <img src={link+"fig15.svg"} alt="img15"></img>
        </div>
        <div>
          <img src={link+"fig14.svg"} alt="img14"></img>
          <img src={link+"fig13.svg"} alt="img13"></img>
        </div>
      </div>
      <div class="cat">
        <h2>Estatisticas generales de Caché</h2>
        <div class="row">
          <img src={link+"fig12.svg"} alt="img12"></img>
          <img src={link+"fig11.svg"} alt="img11"></img>
        </div>
      </div>
      <div class="cat">
        <h2>Estadisticas de Ultimo nivel de Caché</h2>
        <div class="row">
          <img src={link+"fig4.svg"} alt="img4"></img>
          <img src={link+"fig5.svg"} alt="img5"></img>
        </div>
        <div class="row">
          <img src={link+"fig6.svg"} alt="img6"></img>
          <img src={link+"fig7.svg"} alt="img7"></img>
        </div>
      </div>
      <div class="cat">
        <h2>Estadisticas de Caché nivel 1</h2>
        <div class="row">
          <img src={link+"fig8.svg"} alt="img8"></img>
          <img src={link+"fig9.svg"} alt="img9"></img>
        </div>
        <div class="row">
          <img src={link+"fig10.svg"} alt="img10"></img>
        </div>
      </div>
    </div>
    );

  function handleDownload(event){
    axios({
      url: 'http://keira.inf.udec.cl/static/'+asd+'/'+asd+'ResultsFinal.csv',
        method: 'GET',
        responseType: 'blob', // important
      })
    .then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'results.csv');
      document.body.appendChild(link);
      link.click();
    });
  }
}


function RenderForm(){
  const [code, setCode] = useState('');
  const [codename, setCodename] = useState();
  const [status, setStatus] = useState('Esperando entrada');
  const [check, setCheck] = useState(true)
  var flag = '';
  var intervalID = 0;
  let navigate = useNavigate();

  function handleSubmit(event){
    alert('Sent!');
    event.preventDefault();
    var bodyFormData = new FormData();
    bodyFormData.append('code', code);
    axios({
        method: 'post',
        url: 'http://keira.inf.udec.cl/sendcode',
        data: bodyFormData,
        headers: {'Content-Type': 'multipart/form-data'}
      })
      .then((response) =>{
        console.log(response.data, codename);
        setCodename(response.data);
        intervalID = setInterval(getStatusfromServer, 5000, response.data)
      })
      .catch((response) =>{
        console.log(response);
      });
  }

  function handleChange(event){
    setCode(event.target.value);
    setCheck(true);
  }

  function getStatusfromServer(match){
    axios.get('http://keira.inf.udec.cl/checkstatus/'+match)
        .then((response) =>{
          if(response.data === 'IN QUEUE')
            setStatus('En cola')
          else 
            if(response.data === 'DONE')
            setStatus('Listo')
          else
            setStatus(response.data);
          flag = response.data;
        })
        .catch((response)=>{
        })
    var tmp = flag.split(':');
    console.log(tmp, flag)
    if(flag === 'DONE' || tmp[0] === 'ERROR'){
      clearInterval(intervalID)
      if(flag === 'DONE')
        setCheck(false)
    }
}

  return (<React.Fragment>
            <div><h1>Power Tester</h1></div>
            <form onSubmit={handleSubmit}>
            <div><label htmlFor="code">Inserte codigo </label></div>
            <textarea type="text" id="code" name="code" rows="20" cols="100" value={code} onChange={handleChange}></textarea>
            <aside>
              <h2> Estado del Código </h2>
              <div>
                <textarea type="text" id="status" value={status} disabled rows="10" cols="50"></textarea>
              </div>
              <button type="button" className="buttonv" onClick={()=>navigate('/code/'+codename, {replace: false})} disabled={check}> Check Code</button>
            </aside>
            <div>
            <input type="submit" className="buttonv" value="Subir"/>
            </div>
            </form>
          </React.Fragment>)

function RenderImage(){
  var asd = useParams().codename;
  return (
    <div>
      <img src={"http://127.0.0.1:5000/static/"+asd+"/fig0.svg"}></img>
      <img src={"http://127.0.0.1:5000/static/"+asd+"/fig1.svg"}></img>
    </div>
    );
}
export default App;