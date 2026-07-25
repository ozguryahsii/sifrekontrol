import type { CheckResult, DatasetStatus } from "./types";

/**
 * Tüm istekler aynı origin'e gider; Next.js rewrite kuralı bunları
 * 127.0.0.1:3002'deki Python API'sine iletir. Şifre makine dışına çıkmaz.
 */

export class ApiError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(path, { cache: "no-store", ...init });
  } catch {
    throw new ApiError(
      "API'ye ulaşılamadı. Backend'in çalıştığından emin olun: sifrekontrol serve --port 3002"
    );
  }
  if (!resp.ok) {
    throw new ApiError(`API hatası (HTTP ${resp.status})`, resp.status);
  }
  return resp.json() as Promise<T>;
}

export function checkPassword(password: string): Promise<CheckResult> {
  return request<CheckResult>("/api/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
}

export function getStatus(): Promise<DatasetStatus> {
  return request<DatasetStatus>("/api/status");
}
