"use client";
import { useEffect, useState } from "react";
import { graphUrlsAdd } from "../api-codegen/client";
export default function Home() {
  const [result, setResult] = useState("");
  useEffect(() => {
    async function getResult() {
      const response = await graphUrlsAdd({ query: { a: 1, b: 2 } });
      setResult(response.data?.toString() ?? "");
    }
    getResult();
  }, []);
  return <div>{result}</div>;
}
