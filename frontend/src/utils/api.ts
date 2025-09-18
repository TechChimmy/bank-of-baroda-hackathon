export interface LoginRequest {
    username: string;
    password: string;
  }
  
  export interface LoginResponse {
    message: string;
    mfa_challenge: string;
  }
  
  export interface MFAResponse {
    status: string;
    risk_score: number;
  }
  
  export interface PhishReportRequest {
    url: string;
    description?: string;
  }
  
  export interface PhishReportResponse {
    reported: boolean;
    detected_as_phish: boolean;
  }
  
  const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000") + "/api";
  
  async function handleJson(res: Response) {
    let data: any = null;
    try {
      data = await res.json();
    } catch (_) {
      // ignore parse error
    }
    if (!res.ok) {
      const msg = data?.detail || data?.message || `HTTP ${res.status}`;
      throw new Error(`API error: ${msg}`);
    }
    return data;
  }
  
  export async function login(req: LoginRequest): Promise<LoginResponse> {
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });
      return await handleJson(res);
    } catch (e: any) {
      throw new Error(`Login failed: ${e?.message ?? e}`);
    }
  }
  
  export async function verifyMFA(username: string, token: string): Promise<MFAResponse> {
    try {
      const res = await fetch(`${API_URL}/mfa/verify?username=${encodeURIComponent(username)}&token=${encodeURIComponent(token)}`, {
        method: "POST",
      });
      return await handleJson(res);
    } catch (e: any) {
      throw new Error(`MFA verify failed: ${e?.message ?? e}`);
    }
  }
  
  export async function reportPhish(req: PhishReportRequest): Promise<PhishReportResponse> {
    try {
      const res = await fetch(`${API_URL}/report-phish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });
      return await handleJson(res);
    } catch (e: any) {
      throw new Error(`Report failed: ${e?.message ?? e}`);
    }
  }