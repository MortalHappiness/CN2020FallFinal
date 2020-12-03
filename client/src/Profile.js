import React from "react";
import { useLocation } from "react-router-dom";

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

export default function Profile() {
  const query = useQuery();
  const id = query.get("id") || "guest";
  return <h1>{`profile for ${id}`}</h1>;
}
