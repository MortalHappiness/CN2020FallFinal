import React from "react";

import { Player } from "video-react";
import { makeStyles } from "@material-ui/core/styles";

import Container from "@material-ui/core/Container";
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";

import "./video-react.css";

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

export default function Stream() {
  const classes = useStyles();

  return (
    <Container maxWidth="lg" component="main" className={classes.title}>
      <Typography
        component="h1"
        variant="h2"
        align="center"
        color="textPrimary"
        gutterBottom
      >
        Audio
      </Typography>
      <Link variant="h3" href="https://www.bensound.com/">
        Royalty Free Music from Bensound
      </Link>
      <Player>
        <source src="/static/music.mp3" />
      </Player>
      <Typography
        component="h1"
        variant="h2"
        align="center"
        color="textPrimary"
        gutterBottom
      >
        Video
      </Typography>
      <Player>
        <source src="/static/video.mp4" />
      </Player>
    </Container>
  );
}
