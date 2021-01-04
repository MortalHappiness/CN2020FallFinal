import React, { createContext, useState, useEffect } from "react";
import { hot } from "react-hot-loader";
import {
  HashRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom";

import TopBar from "./TopBar";
import Home from "./Home";
import Stream from "./Stream";
import Login from "./Login";
import Register from "./Register";
import Profile from "./Profile";

export const UsernameContext = createContext();

function App() {
  const [username, setUsername] = useState(null);
  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("/api/username");
      const json = await res.json();
      setUsername(json.username);
    };

    fetchData();
  }, []);

  return (
    <UsernameContext.Provider value={[username, setUsername]}>
      <Router>
        <TopBar />
        <Switch>
          <Route exact path="/">
            <Home />
          </Route>
          <Route exact path="/stream">
            <Stream />
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
    </UsernameContext.Provider>
  );
}

export default hot(module)(App);
