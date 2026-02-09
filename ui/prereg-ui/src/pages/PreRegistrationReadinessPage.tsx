// src/pages/PreRegistrationReadinessPage.tsx
import { useEffect, useState } from "react";
import {
  fetchPreregistrationSnapshot,
  completeObligation,
  fetchRegistrarPack,
} from "../api/preregistration";
import type { PreregistrationSnapshot } from "../types/preregistration";

import { StatusBanner } from "../components/StatusBanner";
import { ChecklistTable } from "../components/ChecklistTable";
import { BlockersPanel } from "../components/BlockersPanel";
import { useSociety } from "../context/SocietyContext";
import { SocietySelector } from "../components/SocietySelector";
import { deletePreregistrationDocument } from "../api/preregistration";


export function PreRegistrationReadinessPage() {
  const [snapshot, setSnapshot] =
    useState<PreregistrationSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const { society } = useSociety();

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

  const handleGeneratePack = async () => {
    if (!society) return;

    try {
      const data = await fetchRegistrarPack(society.id);
      console.log("Registrar pack:", data);
      alert("Registrar pack generated — check console for now.");
    } catch (err) {
      console.error(err);
      setError("Failed to generate registrar pack");
    }
  };

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

  return (
    <div style={{ padding: "24px" }}>
      <SocietySelector />

      <h1>{snapshot.title}</h1>

      <StatusBanner
        summary={snapshot.summary}
        registrarReady={snapshot.registrar_ready}
      />

      <ChecklistTable
        items={snapshot.items}
        onToggle={toggleItem}
        onDelete={handleDelete}
      />

      <BlockersPanel blockers={snapshot.blockers} />
    </div>
  );
}
