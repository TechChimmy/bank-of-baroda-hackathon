"use client";

import { useState } from "react";
import { reportPhish } from "../utils/api";

export default function PhishAlertButton() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<string | null>(null);

  const handleReport = async () => {
    const res = await reportPhish({ url });
    setResult(res.detected_as_phish ? "Phishing detected!" : "No phishing detected.");
  };

  return (
    <div>
      <h4>Report Suspicious URL</h4>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL"
      />
      <button onClick={handleReport}>Report</button>
      {result && <p>{result}</p>}
    </div>
  );
}
