import React, { useState, useEffect, useCallback, useRef } from "react";
import PropTypes from "prop-types";
import { useLocation } from "react-router-dom";

import { makeStyles } from "@material-ui/core/styles";

import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Container from "@material-ui/core/Container";
import FormHelperText from "@material-ui/core/FormHelperText";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";

const useStyles = makeStyles((theme) => ({
  "@global": {
    ul: {
      margin: 0,
      padding: 0,
      listStyle: "none",
    },
  },
  title: {
    padding: theme.spacing(8, 0, 6),
  },
  form: {
    width: "100%",
    marginTop: theme.spacing(1),
  },
}));

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function MessageForm({ userTo, messageAdded }) {
  const classes = useStyles();

  const [message, setMessage] = useState("");
  const handleChange = (e) => {
    setMessage(e.target.value);
  };

  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(false);
  const isMounted = useRef(true);

  // set isMounted to false when we unmount the component
  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      if (isSending) return;
      setIsSending(true);
      const res = await fetch("/api/send-message", {
        method: "POST",
        mode: "same-origin",
        cache: "no-cache",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        redirect: "manual",
        referrerPolicy: "no-referrer",
        body: `user-to=${encodeURIComponent(
          userTo
        )}&message=${encodeURIComponent(message)}`,
      });
      if (isMounted.current) setIsSending(false);
      if (res.ok) {
        const json = await res.json();
        messageAdded(json);
        setError(null);
      } else {
        const json = await res.json();
        setError(json.msg);
      }
    },
    [isSending, message, userTo, messageAdded]
  );

  return (
    <form className={classes.form} onSubmit={handleSubmit}>
      <FormHelperText error={Boolean(error)} className={classes.errorMsg}>
        {error}
      </FormHelperText>
      <TextField
        name="message"
        value={message}
        placeholder="Message"
        variant="outlined"
        multiline={true}
        rows={4}
        required={true}
        size="medium"
        margin="normal"
        fullWidth
        onChange={handleChange}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        color="primary"
        className={classes.submit}
      >
        Send
      </Button>
    </form>
  );
}

MessageForm.propTypes = {
  userTo: PropTypes.string,
  messageAdded: PropTypes.func,
};

export default function Profile() {
  const classes = useStyles();

  const query = useQuery();
  const username = query.get("username");

  const [messages, setMessages] = useState();
  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(
        `/api/messages?username=${encodeURIComponent(username)}`
      );
      setMessages(await res.json());
    };

    fetchData();
  }, [username]);

  const messageAdded = useCallback(
    (message) => {
      setMessages([message, ...messages]);
    },
    [messages]
  );

  return (
    <Container maxWidth="sm" component="main" className={classes.title}>
      {username ? (
        <>
          <Typography
            component="h1"
            variant="h2"
            align="center"
            color="textPrimary"
            gutterBottom
          >
            {`Profile for ${username}`}
          </Typography>
          <Typography variant="h4">{`Send messages to ${username}`}</Typography>
          <MessageForm userTo={username} messageAdded={messageAdded} />
          <Typography variant="h4">Messages</Typography>
          {messages &&
            messages.map(({ id, user_from, message }) => (
              <Card key={id}>
                <CardContent>
                  <Typography variant="h5">
                    {`${user_from} ▶ ${username}`}
                  </Typography>
                  {message}
                </CardContent>
              </Card>
            ))}
        </>
      ) : (
        <>
          <Typography
            component="h1"
            variant="h2"
            align="center"
            color="textPrimary"
            gutterBottom
          >
            Demo Profile
          </Typography>
          <Card>
            <CardContent>
              <Typography variant="h5">{`admin ▶ demo`}</Typography>
              {"Welcome!"}
            </CardContent>
            <CardContent>
              <Typography variant="h5">{`hacker ▶ demo`}</Typography>
              {"<script>alert()</script>"}
            </CardContent>
          </Card>
        </>
      )}
    </Container>
  );
}
