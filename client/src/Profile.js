import React from "react";
import { useLocation } from "react-router-dom";

import Button from "@material-ui/core/Button";

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

export default function Profile() {
  const query = useQuery();
  const id = query.get("id") || "guest";
  return (
    <>
      <h1>{`profile for ${id}`}</h1>
      <Button variant="contained" color="primary">
        Hello World
      </Button>
    </>
  );
}
