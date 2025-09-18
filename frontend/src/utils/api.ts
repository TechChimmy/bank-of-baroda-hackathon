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
  
  const API_URL = "http://127.0.0.1:8000/api";
  
  export async function login(req: LoginRequest): Promise<LoginResponse> {
    const res = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    return res.json();
  }
  
  export async function verifyMFA(username: string, token: string): Promise<MFAResponse> {
    const res = await fetch(`${API_URL}/mfa/verify?username=${username}&token=${token}`, {
      method: "POST",
    });
    return res.json();
  }
  
  export async function reportPhish(req: PhishReportRequest): Promise<PhishReportResponse> {
    const res = await fetch(`${API_URL}/report-phish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    return res.json();
  }
  