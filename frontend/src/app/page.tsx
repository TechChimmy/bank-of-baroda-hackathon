"use client";

import { useState } from "react";
import { login } from "../utils/api";
import MFAPrompt from "../components/MFAPrompt";
import PhishAlertButton from "../components/PhishAlertButton";
import {
  beginRegistration,
  finishRegistration,
  beginAuthentication,
  finishAuthentication,
} from "../utils/webauthn";
import Card from "../components/Card";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [challenge, setChallenge] = useState<string | null>(null);
  const [passkeyStatus, setPasskeyStatus] = useState<string | null>(null);
  const [loginError, setLoginError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoginError(null);
    try {
      const res = await login({ username, password });
      setChallenge(res.mfa_challenge);
    } catch (e: any) {
      setLoginError(e?.message ?? String(e));
    }
  };

  const handleRegisterPasskey = async () => {
    try {
      setPasskeyStatus("Starting registration...");
      const options = await beginRegistration(username);
      const credential = (await navigator.credentials.create({ publicKey: options })) as PublicKeyCredential;
      await finishRegistration(username, credential);
      setPasskeyStatus("Passkey registered successfully.");
    } catch (e: any) {
      setPasskeyStatus(`Registration failed: ${e?.message ?? e}`);
    }
  };

  const handleLoginPasskey = async () => {
    try {
      setPasskeyStatus("Starting authentication...");
      const request = await beginAuthentication(username);
      const assertion = (await navigator.credentials.get({ publicKey: request })) as PublicKeyCredential;
      const res = await finishAuthentication(username, assertion);
      setPasskeyStatus(`Authenticated with passkey. Risk score: ${res.risk_score}`);
    } catch (e: any) {
      setPasskeyStatus(`Authentication failed: ${e?.message ?? e}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="mb-2">
        <h1 className="text-2xl font-semibold tracking-tight">Welcome</h1>
        <p className="text-sm text-neutral-400">Sign in securely or use passkeys. Report suspicious URLs below.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card id="login" title="Password Login">
          <div className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-sm text-neutral-300">Username</label>
              <input
                className="w-full rounded-lg border border-neutral-800/60 bg-neutral-950/60 px-3 py-2 outline-none focus:border-indigo-500/60"
                placeholder="e.g., alice"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm text-neutral-300">Password</label>
              <input
                className="w-full rounded-lg border border-neutral-800/60 bg-neutral-950/60 px-3 py-2 outline-none focus:border-indigo-500/60"
                placeholder="••••••••"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button
              className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500 disabled:opacity-50"
              onClick={handleLogin}
              disabled={!username || !password}
            >
              Continue
            </button>
            {loginError && (
              <p className="text-sm text-rose-400">{loginError}</p>
            )}
          </div>
          {challenge && (
            <div className="mt-4">
              <MFAPrompt username={username} challenge={challenge} />
            </div>
          )}
        </Card>

        <Card id="passkeys" title="Passkeys (WebAuthn)">
          <div className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-sm text-neutral-300">Username</label>
              <input
                className="w-full rounded-lg border border-neutral-800/60 bg-neutral-950/60 px-3 py-2 outline-none focus:border-indigo-500/60"
                placeholder="e.g., alice"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-2">
              <button
                className="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium hover:bg-emerald-500 disabled:opacity-50"
                onClick={handleRegisterPasskey}
                disabled={!username}
              >
                Register Passkey
              </button>
              <button
                className="inline-flex items-center justify-center rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium hover:bg-sky-500 disabled:opacity-50"
                onClick={handleLoginPasskey}
                disabled={!username}
              >
                Login with Passkey
              </button>
            </div>
            {passkeyStatus && (
              <p className="text-sm text-neutral-300">{passkeyStatus}</p>
            )}
          </div>
        </Card>
      </div>

      <Card id="report" title="Report Suspicious URL">
        <PhishAlertButton />
      </Card>
    </div>
  );
}
