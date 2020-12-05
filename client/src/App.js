import React from "react";
import { hot } from "react-hot-loader";
import {
  HashRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom";

import Login from "./Login";
import Register from "./Register";
import Profile from "./Profile";

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/">
          <h1>hi</h1>
        </Route>
        <Route exact path="/login">
          <Login />
        </Route>
        <Route exact path="/register">
          <Register />
        </Route>
        <Route exact path="/profile">
          <Profile />
        </Route>
        <Redirect to="/" />
      </Switch>
    </Router>
  );
}

export default hot(module)(App);
