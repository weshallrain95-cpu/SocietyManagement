export interface PreregistrationChecklistItem {
  id: number;
  code: string;
  title: string;
  mandatory: boolean;
  status: string;

  evidence_required: boolean;

  // NEW — evidence layer
  document_uploaded?: boolean;

  document?: {
    template_id: number;
    file: string;
    uploaded_at: string;
  };
}


export interface PreregistrationBlocker {
  type: string;
  message: string;
  obligation_id?: number;
  obligation_title?: string;
}

export interface PreregistrationSummary {
  total_mandatory: number;
  completed_mandatory: number;
}

export interface PreregistrationSnapshot {
  title: string;
  registrar_ready: boolean;
  completed: boolean;
  summary: PreregistrationSummary;
  items: PreregistrationChecklistItem[];
  blockers: PreregistrationBlocker[];
}
