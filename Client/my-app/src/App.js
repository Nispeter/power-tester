import React, { Component } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import RenderForm from "./screens/RenderForm";
import RenderImage from "./screens/RenderImage";
import Navbar from "./common/Navbar";
import TaskPage from "./screens/TaskPage"

class App extends Component {
  state = {
    useLCSTest: false
  }

  handleLCSToggle = (value) => {
    this.setState({ useLCSTest: value });
  }

  componentDidMount() {
    document.title = "Power-tester";
  }

  render() {
    return (
      <div>
        <BrowserRouter>
        <Navbar useLCSTest={this.state.useLCSTest} />
          <Routes>
            <Route path="/taskpage" element={<TaskPage onLCSToggle={this.handleLCSToggle} useLCSTest={this.state.useLCSTest} />} />
            <Route path="/" element={<RenderForm useLCSTest={this.state.useLCSTest} />} />
            <Route path="/code/:codename" element={<RenderImage />} />
          </Routes>
        </BrowserRouter>
      </div>
    );
  }
}

export default App;