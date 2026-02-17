// src/pages/PreRegistrationReadinessPage.tsx
import { useEffect, useState } from "react";
import {
  fetchPreregistrationSnapshot,
  completeObligation,
  downloadRegistrarPack,
  deletePreregistrationDocument,
} from "../api/preregistration";

import type { PreregistrationSnapshot } from "../types/preregistration";

import { StatusBanner } from "../components/StatusBanner";
import { ChecklistTable } from "../components/ChecklistTable";
import { BlockersPanel } from "../components/BlockersPanel";
import { useSociety } from "../context/SocietyContext";
import { SocietySelector } from "../components/SocietySelector";

export function PreRegistrationReadinessPage() {
  const [snapshot, setSnapshot] =
    useState<PreregistrationSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const { society } = useSociety();

  // -----------------------------
  // Load snapshot
  // -----------------------------
  const load = () => {
    setLoading(true);
    setError(null);

    const societyId = society?.id ?? 1;

    fetchPreregistrationSnapshot(societyId)
      .then(setSnapshot)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [society]);

  // -----------------------------
  // Toggle obligation status
  // -----------------------------
  const toggleItem = async (obligationId: number, currentStatus: string) => {
    if (!society) return;

    const nextStatus =
      currentStatus === "COMPLETED" ? "PENDING" : "COMPLETED";

    try {
      await completeObligation(obligationId, society.id, nextStatus);
      load();
    } catch (err) {
      console.error(err);
      setError("Failed to update obligation status");
    }
  };

  // -----------------------------
  // Delete uploaded document
  // -----------------------------
  const handleDelete = async (templateId: number) => {
    if (!society) return;

    try {
      await deletePreregistrationDocument(society.id, templateId);
      load();
    } catch (err) {
      console.error(err);
      setError("Failed to delete document");
    }
  };

  // -----------------------------
  // Download Registrar Pack (ZIP)
  // -----------------------------
  const handleDownloadPack = () => {
    if (!society) return;
    downloadRegistrarPack(society.id);
  };

  // -----------------------------
  // UI STATES
  // -----------------------------
  if (loading) {
    return (
      <div style={{ padding: "24px" }}>
        Loading pre-registration readiness…
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "24px", color: "red" }}>
        <h2>Unable to load pre-registration status</h2>
        <pre>{error}</pre>
        <button onClick={load}>Retry</button>
      </div>
    );
  }

  if (!snapshot) {
    return (
      <div style={{ padding: "24px" }}>
        No data available.
      </div>
    );
  }

  // -----------------------------
  // MAIN UI
  // -----------------------------
  return (
    <div style={{ padding: "24px" }}>
      <SocietySelector />

      <h1>{snapshot.title}</h1>

      <StatusBanner
        summary={snapshot.summary}
        registrarReady={snapshot.registrar_ready}
      />

      {/* Registrar Pack download appears ONLY when ready */}
      {snapshot.registrar_ready && (
        <div style={{ marginTop: "16px" }}>
          <button onClick={handleDownloadPack}>
            Download Registrar Pack
          </button>
        </div>
      )}

      <ChecklistTable
        items={snapshot.items}
        onToggle={toggleItem}
        onDelete={handleDelete}
      />

      <BlockersPanel blockers={snapshot.blockers} />
    </div>
  );
}
