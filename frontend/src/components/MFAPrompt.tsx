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
    <div>
      <h3>MFA Verification</h3>
      <p>Challenge: {challenge}</p>
      <input
        type="text"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        placeholder="Enter MFA token"
      />
      <button onClick={handleVerify}>Verify</button>
      {status && <p>{status}</p>}
    </div>
  );
}
