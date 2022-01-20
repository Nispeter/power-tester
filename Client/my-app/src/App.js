import React, { Component } from "react";
import {BrowserRouter, Routes, Route, Link, useParams} from "react-router-dom"

const axios = require("axios").default;

class App extends Component {
  constructor(props){
    super(props);
    this.state = {
      value: '',
      codename: ''
    };
    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }

  handleSubmit(event){
    alert('Sent!');
    event.preventDefault();
    var bodyFormData = new FormData();
    bodyFormData.append('code', this.state.value)
    axios({
      method: 'post',
      url: 'http://127.0.0.1:5000/sendcode',
      data: bodyFormData,
      headers: {'Content-Type': 'multipart/form-data'}
    })
    .then(function (response) {
      console.log(response.data)
      this.setState({codename: response.data})
    })
    .catch(function (response) {
      console.log(response)
    })
  }
  handleChange(event){
    this.setState({value: event.target.value});
  }

  render() {
    return (
      <div>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={
              <React.Fragment>
                <div><h1>Power Tester</h1></div>
                <form onSubmit={this.handleSubmit}>
                  <div><label htmlFor="code">Inserte codigo </label></div>
                    <textarea type="text" id="code" name="code" rows="20" cols="100" value={this.state.value} onChange={this.handleChange}></textarea>
                  <div>
                    <input type="submit" value="Subir"/>
                  </div>
                </form>
              </React.Fragment>
              }
            ></Route>
            <Route path="/:codename" element={
              <RenderImage/>
            }></Route>
          </Routes>
        </BrowserRouter>
      </div>
    )
  }
}


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