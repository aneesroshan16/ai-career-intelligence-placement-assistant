import axios, { AxiosError, type AxiosInstance } from "axios";
import { getAccessToken } from "@/lib/supabaseClient";

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  meta: { request_id: string; timestamp: string };
  error: { code: string; message: string; details: Record<string, unknown> } | null;
}

export class ApiError extends Error {
  code: string;
  details: Record<string, unknown>;
  status?: number;

  constructor(code: string, message: string, details: Record<string, unknown>, status?: number) {
    super(message);
    this.code = code;
    this.details = details;
    this.status = status;
  }
}

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const apiClient: AxiosInstance = axios.create({ baseURL, timeout: 30000 });

apiClient.interceptors.request.use(async (config) => {
  const token = await getAccessToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiEnvelope<unknown>>) => {
    const envelope = error.response?.data;
    if (envelope?.error) {
      throw new ApiError(envelope.error.code, envelope.error.message, envelope.error.details, error.response?.status);
    }
    throw error;
  }
);

/** Unwraps the standard `{ success, data, error }` envelope into just `data`. */
export async function unwrap<T>(promise: Promise<{ data: ApiEnvelope<T> }>): Promise<T> {
  const response = await promise;
  if (!response.data.success || response.data.data === null) {
    throw new ApiError(
      response.data.error?.code ?? "UNKNOWN_ERROR",
      response.data.error?.message ?? "Unknown error",
      response.data.error?.details ?? {}
    );
  }
  return response.data.data;
}
