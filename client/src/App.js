import React from "react";
import { hot } from "react-hot-loader";
import {
  HashRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom";

import Profile from "./Profile";

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/">
          <h1>hi</h1>
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
