import React, { useCallback, useContext } from "react";
import { useHistory } from "react-router-dom";

import { makeStyles } from "@material-ui/core/styles";

import AppBar from "@material-ui/core/AppBar";
import Button from "@material-ui/core/Button";
import Link from "@material-ui/core/Link";
import Toolbar from "@material-ui/core/Toolbar";

import { UsernameContext } from "./App";

const useStyles = makeStyles((theme) => ({
  "@global": {
    ul: {
      margin: 0,
      padding: 0,
      listStyle: "none",
    },
  },
  appBar: {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
  toolbar: {
    flexWrap: "wrap",
  },
  toolbarTitle: {
    flexGrow: 1,
  },
  link: {
    margin: theme.spacing(1, 1.5),
  },
}));

export default function TopBar() {
  const classes = useStyles();

  const [username, setUsername] = useContext(UsernameContext);

  const history = useHistory();

  const logoutRequest = useCallback(async () => {
    const res = await fetch("/api/logout", {
      method: "POST",
      mode: "same-origin",
      cache: "no-cache",
      credentials: "same-origin",
      redirect: "manual",
      referrerPolicy: "no-referrer",
    });
    if (res.ok) {
      setUsername("");
      history.push("/");
    }
  }, [history, setUsername]);

  return (
    <AppBar
      position="static"
      color="default"
      elevation={0}
      className={classes.appBar}
    >
      <Toolbar className={classes.toolbar}>
        <Link
          href="#"
          color="inherit"
          variant="h4"
          noWrap
          underline="none"
          className={classes.toolbarTitle}
        >
          CN2020 Final
        </Link>
        <Link
          href="#/stream"
          color="textPrimary"
          variant="button"
          underline="none"
          className={classes.link}
        >
          Streaming
        </Link>
        {username !== null &&
          (username ? (
            <>
              <Link
                variant="button"
                color="textPrimary"
                href={`#/profile?username=${encodeURIComponent(username)}`}
                className={classes.link}
              >
                {`Hello, ${username}!`}
              </Link>
              <Button
                color="primary"
                variant="outlined"
                className={classes.link}
                onClick={logoutRequest}
              >
                Logout
              </Button>
            </>
          ) : (
            <>
              <Button
                href="#/login"
                color="primary"
                variant="outlined"
                className={classes.link}
              >
                Login
              </Button>
              <Button
                href="#/register"
                color="primary"
                variant="outlined"
                className={classes.link}
              >
                Sign Up
              </Button>
            </>
          ))}
      </Toolbar>
    </AppBar>
  );
}
