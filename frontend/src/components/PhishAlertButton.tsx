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
    <div className="space-y-3">
      <div className="space-y-1.5">
        <label className="text-sm text-neutral-300">Suspicious URL</label>
        <input
          className="w-full rounded-lg border border-neutral-800/60 bg-neutral-950/60 px-3 py-2 outline-none focus:border-rose-500/60"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/login"
        />
      </div>
      <button
        className="inline-flex items-center justify-center rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium hover:bg-rose-500 disabled:opacity-50"
        onClick={handleReport}
        disabled={!url}
      >
        Report URL
      </button>
      {result && <p className="text-sm text-neutral-300">{result}</p>}
    </div>
  );
}
