"use client";

import { useState } from "react";
import { login } from "../utils/api";
import MFAPrompt from "../components/MFAPrompt";
import PhishAlertButton from "../components/PhishAlertButton";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [challenge, setChallenge] = useState<string | null>(null);

  const handleLogin = async () => {
    const res = await login({ username, password });
    setChallenge(res.mfa_challenge);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Bank of Baroda Hackathon Login</h1>

      {!challenge ? (
        <div>
          <input
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={handleLogin}>Login</button>
        </div>
      ) : (
        <MFAPrompt username={username} challenge={challenge} />
      )}

      <PhishAlertButton />
    </div>
  );
}
