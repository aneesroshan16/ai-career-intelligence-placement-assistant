import { apiClient, unwrap } from "@/lib/api/client";
import { setStoredDevToken } from "@/lib/supabaseClient";

export interface DevLoginPayload {
  user_id: string;
  email: string;
  role?: "student" | "admin" | "placement_officer";
  full_name?: string;
}

interface DevTokenResponse {
  access_token: string;
  token_type: string;
}

/**
 * Exchanges a locally-generated user id for a dev-mode JWT via
 * POST /api/v1/auth/dev-token (backend/app/modules/auth/router.py).
 * Only works when the backend has AUTH_MODE=dev — returns 403 otherwise.
 */
export async function devLogin(payload: DevLoginPayload): Promise<void> {
  const { access_token } = await unwrap<DevTokenResponse>(
    apiClient.post("/auth/dev-token", payload)
  );
  setStoredDevToken(access_token);
}
