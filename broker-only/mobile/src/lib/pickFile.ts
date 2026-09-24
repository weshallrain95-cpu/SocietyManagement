// Pick a list to import: Excel, CSV or a phone contacts export (.vcf).
import * as DocumentPicker from 'expo-document-picker';

import type { UploadFile } from '@/api';

const TYPES = [
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/csv',
  'text/comma-separated-values',
  'text/x-vcard',
  'text/vcard',
  'application/octet-stream',
];

export async function pickListFile(): Promise<UploadFile | null> {
  const r = await DocumentPicker.getDocumentAsync({ type: TYPES, copyToCacheDirectory: true, multiple: false });
  if (r.canceled || !r.assets.length) return null;
  const a = r.assets[0];
  return { uri: a.uri, name: a.name, type: a.mimeType ?? 'application/octet-stream', file: a.file };
}
