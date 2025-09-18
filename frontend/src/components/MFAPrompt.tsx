"use client";

import { useState } from "react";
import { verifyMFA } from "../utils/api";

interface MFAPromptProps {
  username: string;
  challenge: string;
}

export default function MFAPrompt({ username, challenge }: MFAPromptProps) {
  const [token, setToken] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  const handleVerify = async () => {
    const res = await verifyMFA(username, token);
    setStatus(res.status + " | Risk score: " + res.risk_score);
  };

  return (
    <div className="rounded-lg border border-neutral-800/60 bg-neutral-950/40 p-4">
      <h3 className="text-sm font-medium mb-1">MFA Verification</h3>
      <p className="text-xs text-neutral-400 mb-3">Challenge: <span className="font-mono text-neutral-300">{challenge}</span></p>
      <div className="flex items-center gap-2">
        <input
          className="flex-1 rounded-lg border border-neutral-800/60 bg-neutral-950/60 px-3 py-2 outline-none focus:border-indigo-500/60"
          type="text"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Enter MFA token"
        />
        <button
          className="inline-flex items-center justify-center rounded-lg bg-amber-600 px-3 py-2 text-sm font-medium hover:bg-amber-500 disabled:opacity-50"
          onClick={handleVerify}
          disabled={!token}
        >
          Verify
        </button>
      </div>
      {status && <p className="mt-2 text-sm text-neutral-300">{status}</p>}
    </div>
  );
}
