import React, { Component } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import RenderForm from "./common/RenderForm";
import RenderImage from "./common/RenderImage";
import Navbar from "./common/Navbar";

class App extends Component {
  componentDidMount() {
    document.title = "Power-tester";
  }

  render() {
    return (
      <div>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<RenderForm />} />
            <Route path="/code/:codename" element={<RenderImage />} />
          </Routes>
        </BrowserRouter>
      </div>
    );
  }
}

export default App;
