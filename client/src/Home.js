import React, { useState, useEffect } from "react";

import { makeStyles } from "@material-ui/core/styles";

import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardActionArea from "@material-ui/core/CardActionArea";
import Container from "@material-ui/core/Container";
import Typography from "@material-ui/core/Typography";

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
}));

export default function Pricing() {
  const classes = useStyles();

  const [users, setUsers] = useState(null);
  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("/api/users");
      setUsers(await res.json());
    };

    fetchData();
  }, []);

  return (
    <Container maxWidth="sm" component="main" className={classes.title}>
      <Typography
        component="h1"
        variant="h2"
        align="center"
        color="textPrimary"
        gutterBottom
      >
        Users
      </Typography>
      {users !== null &&
        users.map((user) => (
          <Card key={user}>
            <CardActionArea
              href={`#/profile?username=${encodeURIComponent(user)}`}
            >
              <CardContent>
                <Typography variant="h5">{user}</Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        ))}
      {Array.isArray(users) && !users.length && (
        <Typography variant="h2">No users now!</Typography>
      )}
    </Container>
  );
}
