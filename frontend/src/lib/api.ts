import type { DataEnvelope } from "./types";

const baseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, { cache: "no-store", ...init });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new ApiError(0, "无法连接后端服务，请确认 API 已启动。");
  }
  if (!response.ok) {
    const messages: Record<number, string> = {
      404: "没有找到对应数据。",
      422: "输入格式不正确，请检查后重试。",
      503: "行情数据源暂不可用，请稍后重试。",
      502: "模型请求失败，请稍后重试。",
      504: "行情数据源响应超时，请稍后重试。",
    };
    throw new ApiError(response.status, messages[response.status] || `请求失败（HTTP ${response.status}）。`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function getData<T>(path: string, signal?: AbortSignal): Promise<DataEnvelope<T>> {
  return apiRequest<DataEnvelope<T>>(path, { signal });
}

export function errorText(error: unknown): string {
  return error instanceof Error ? error.message : "请求失败，请稍后重试。";
}
