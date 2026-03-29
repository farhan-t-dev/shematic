export interface ValidationFlag {
  key: string;
  id: string;
  level: "BLOCKING" | "WARNING";
  message: string;
  question?: string | null;
  metadata?: {
    input_type?: string;
    merge_candidates?: string[];
  };
}

export interface ValidationResponse {
  status: "blocked" | "needs_confirmation" | "ok";
  report: string;
  flags: ValidationFlag[];
  file_name: string;
  upload_id?: string;
}

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  `${window.location.origin}/api`;

const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("auth-token");
  if (!token) {
    return {};
  }
  return { Authorization: `Bearer ${token}` };
};

async function parseError(res: Response): Promise<never> {
  let message = "Request failed.";

  try {
    const data = await res.json();
    if (typeof data.detail === "string") {
      message = data.detail;
    }
  } catch {
    message = res.statusText || message;
  }

  throw new Error(message);
}

export const login = async (username: string, password: string) => {
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    return parseError(res);
  }

  return res.json();
};

export const logout = async () => {
  const res = await fetch(`${API_BASE}/logout`, {
    method: "POST",
    headers: getAuthHeaders(),
  });

  if (!res.ok) {
    return parseError(res);
  }
};

export const validateExcel = async (file: File): Promise<ValidationResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/validate`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!res.ok) {
    return parseError(res);
  }

  return res.json();
};

export const generatePptx = async ({
  uploadId,
  accountNameOverride,
  warningAnswers,
}: {
  uploadId: string;
  accountNameOverride?: string;
  warningAnswers: Record<string, string>;
}): Promise<Blob> => {
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      upload_id: uploadId,
      account_name_override: accountNameOverride || undefined,
      warning_answers: warningAnswers,
    }),
  });

  if (!res.ok) {
    return parseError(res);
  }

  return res.blob();
};
