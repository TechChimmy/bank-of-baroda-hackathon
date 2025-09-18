// Utility functions for WebAuthn base64url conversion
export function b64urlToArrayBuffer(b64url: string): ArrayBuffer {
  const pad = '='.repeat((4 - (b64url.length % 4)) % 4);
  const b64 = (b64url + pad).replace(/-/g, '+').replace(/_/g, '/');
  const str = atob(b64);
  const bytes = new Uint8Array(str.length);
  for (let i = 0; i < str.length; i++) bytes[i] = str.charCodeAt(i);
  return bytes.buffer;
}

export function arrayBufferToB64url(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  const b64 = btoa(binary).replace(/=+$/g, '');
  return b64.replace(/\+/g, '-').replace(/\//g, '_');
}

const API_URL = "http://127.0.0.1:8000/api";

export async function beginRegistration(username: string) {
  const res = await fetch(`${API_URL}/webauthn/register/begin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });
  if (!res.ok) throw new Error('Failed to begin registration');
  const options = await res.json();
  // Convert base64url fields to ArrayBuffers
  options.challenge = b64urlToArrayBuffer(options.challenge);
  if (options.user && typeof options.user.id === 'string') {
    options.user.id = b64urlToArrayBuffer(options.user.id);
  }
  if (Array.isArray(options.excludeCredentials)) {
    options.excludeCredentials = options.excludeCredentials.map((c: any) => ({
      ...c,
      id: b64urlToArrayBuffer(c.id),
    }));
  }
  return options as PublicKeyCredentialCreationOptions;
}

export async function finishRegistration(username: string, credential: PublicKeyCredential) {
  const att = credential.response as AuthenticatorAttestationResponse;
  const payload = {
    username,
    clientDataJSON: arrayBufferToB64url(att.clientDataJSON),
    attestationObject: arrayBufferToB64url(att.attestationObject),
  };
  const res = await fetch(`${API_URL}/webauthn/register/finish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to finish registration');
  return res.json();
}

export async function beginAuthentication(username: string) {
  const res = await fetch(`${API_URL}/webauthn/authenticate/begin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  });
  if (!res.ok) throw new Error('Failed to begin authentication');
  const request = await res.json();
  request.challenge = b64urlToArrayBuffer(request.challenge);
  if (Array.isArray(request.allowCredentials)) {
    request.allowCredentials = request.allowCredentials.map((c: any) => ({
      ...c,
      id: b64urlToArrayBuffer(c.id),
    }));
  }
  return request as PublicKeyCredentialRequestOptions;
}

export async function finishAuthentication(username: string, assertion: PublicKeyCredential) {
  const auth = assertion.response as AuthenticatorAssertionResponse;
  const payload = {
    username,
    id: arrayBufferToB64url(assertion.rawId),
    clientDataJSON: arrayBufferToB64url(auth.clientDataJSON),
    authenticatorData: arrayBufferToB64url(auth.authenticatorData),
    signature: arrayBufferToB64url(auth.signature),
  };
  const res = await fetch(`${API_URL}/webauthn/authenticate/finish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to finish authentication');
  return res.json();
}
