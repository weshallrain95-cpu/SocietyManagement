// Bring a list in at once: an Excel/CSV file, a phone contacts export (.vcf), or lines pasted from WhatsApp/notes.
import { useMutation } from '@tanstack/react-query';
import React, { useState } from 'react';

import type { ImportResult, ImportSource } from '@/api';
import { pickListFile } from '@/lib/pickFile';
import { Button, Card, ErrorBox, Field, Notice, P } from './components';

export function ImportPanel({ what, columns, run, onDone }: {
  what: string;
  columns: string;
  run: (src: ImportSource) => Promise<ImportResult>;
  onDone?: (r: ImportResult) => void;
}) {
  const [text, setText] = useState('');
  const m = useMutation({ mutationFn: run, onSuccess: (r) => { setText(''); onDone?.(r); } });
  const fromFile = async () => {
    const file = await pickListFile();
    if (file) m.mutate({ file });
  };
  const r = m.data;
  return (
    <Card>
      <P style={{ fontWeight: '700' }}>Import {what}</P>
      <P small muted>Excel or CSV with columns like {columns}. Or your phone’s contacts export (.vcf). Or paste one per line: “Name 98200 12345”.</P>
      <Button kind="secondary" title="Choose a file" onPress={fromFile} busy={m.isPending} testID="import-file" />
      <Field label="…or paste a list" value={text} onChangeText={setText} multiline placeholder={'Ramesh Patil 98203 00001\nSunil 98203 00004'} testID="import-text" />
      <Button title="Import pasted list" onPress={() => m.mutate({ text })} disabled={!text.trim()} busy={m.isPending} testID="import-paste" />
      {m.error ? <ErrorBox error={m.error} /> : null}
      {r ? (
        <Notice tone={r.skipped_count ? 'warn' : 'ok'}>
          {r.added} added{r.already_in_book ? `, ${r.already_in_book} already in your book` : ''}{r.updated ? `, ${r.updated} updated` : ''}
          {r.skipped_count ? `, ${r.skipped_count} skipped (${r.skipped.slice(0, 3).map((s) => `row ${s.row}: ${s.reason}`).join('; ')})` : ''}.
        </Notice>
      ) : null}
    </Card>
  );
}
