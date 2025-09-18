// src/utils/api.ts
export interface ReportPhishPayload {
    url: string;
    description?: string;
  }
  
  export const reportPhish = async (payload: ReportPhishPayload) => {
    const res = await fetch("/api/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return res.json();
  };
  