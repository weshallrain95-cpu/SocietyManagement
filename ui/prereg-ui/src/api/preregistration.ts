// src/api/preregistration.ts
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

/** read Django csrftoken from document.cookie */
function getCSRFToken(): string {
  const name = "csrftoken=";
  const decoded = decodeURIComponent(document.cookie || "");
  const cookies = decoded.split(";").map((c) => c.trim());
  for (const c of cookies) {
    if (c.startsWith(name)) {
      return c.substring(name.length);
    }
  }
  return "";
}

/** Fetch preregistration snapshot for a society */
export async function fetchPreregistrationSnapshot(societyId: number = 1) {
  const res = await fetch(`${API_BASE}/api/societies/${societyId}/preregistration/snapshot`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to load preregistration snapshot");
  }
  return res.json();
}

/** Mark obligation as completed/pending (POST) */
export async function completeObligation(
  obligationId: number,
  societyId: number,
  nextStatus?: string
) {
  const res = await fetch(`${API_BASE}/api/preregistration/obligations/${obligationId}/status`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    credentials: "include",
    body: JSON.stringify({ society_id: societyId, status: nextStatus }),
  });

  if (res.status === 403) {
    throw new Error("Forbidden (403). CSRF cookie missing or invalid.");
  }
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`Failed to update obligation (${res.status}) ${txt}`);
  }
  return res.json();
}

/** Fetch registrar pack (server-side generation) */
export async function fetchRegistrarPack(societyId: number) {
  const res = await fetch(`${API_BASE}/api/societies/${societyId}/registrar-pack`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to load registrar pack");
  }
  return res.json();
}

export async function deleteDocument(
  societyId: number,
  templateId: number
) {
  const formData = new FormData();
  formData.append("society_id", societyId.toString());
  formData.append("template_id", templateId.toString());

  const res = await fetch(
    `${API_BASE}/api/preregistration/documents/delete`,
    {
      method: "POST",
      credentials: "include",
      body: formData,
    }
  );

  if (!res.ok) {
    throw new Error("Failed to delete document");
  }

  return res.json();
}

export async function deletePreregistrationDocument(
  societyId: number,
  templateId: number
) {
  const formData = new FormData();
  formData.append("society_id", String(societyId));
  formData.append("template_id", String(templateId));

  const res = await fetch(
    `${API_BASE}/api/preregistration/documents/delete`,
    {
      method: "POST",
      credentials: "include",
      body: formData,
    }
  );

  if (!res.ok) {
    throw new Error("Failed to delete document");
  }

  return res.json();
}

export function downloadRegistrarPack(societyId: number) {
  window.open(
    `${API_BASE}/api/societies/${societyId}/registrar-pack/download`,
    "_blank"
  );
}
