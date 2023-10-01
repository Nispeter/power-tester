import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import RenderTable from './RenderTable'

function RenderImage() {
  const asd2 = useNavigate();
  const asd = useParams().codename;
  const name = useLocation().state.name;
  const link = `http://127.0.0.1:5000/static/${asd}/`;

  useEffect(() => {
    document.title = `Power-tester: ${name}`;
  }, [name]);

  return (
    <div>
      <div class="row">
        <button type="button" className="buttonv" onClick={()=>asd2(-1)}> Volver</button>
        <button type="button" className="buttonv" onClick={handleDownload} style={{float: "right"}}> Descargar CSV </button>
        <h1>{name}</h1>
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
        <h2>Estadísticas generales de Caché</h2>
        <div class="row">
          <img src={link+"fig12.svg"} alt="img12"></img>
          <img src={link+"fig11.svg"} alt="img11"></img>
        </div>
      </div>
      <div class="cat">
        <h2>Estadísticas de Último nivel de Caché (LLC)</h2>
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
        <h2>Estadísticas de Caché nivel 1 (L1D)</h2>
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
      url: 'http://127.0.0.1/static/'+asd+'/'+asd+'ResultsFinal.csv',
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

export default RenderImage;
