import { useMutation, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';

import { useSession } from '@/auth/session';
import { Button, Card, Chip, Choice, ErrorBox, Field, Notice, P, Screen } from '@/ui/components';

export default function LeadScreen() {
  const { id, summary, matches, mine } = useLocalSearchParams<{ id: string; summary: string; matches: string; mine: string }>();
  const { api } = useSession();
  const qc = useQueryClient();
  const [terms, setTerms] = useState('1 month rent');
  const [message, setMessage] = useState(Number(matches) ? `I have ${matches} flats that fit your needs. I can show them today.` : 'I can find flats that fit your needs.');
  const send = useMutation({
    mutationFn: () => api.propose(id, { brokerage_terms: terms, message }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['leads'] });
      router.back();
    },
  });
  return (
    <Screen>
      <Card>
        <P>{summary}</P>
        <Chip label={`${matches} of your flats match`} tone={Number(matches) ? 'ok' : undefined} />
      </Card>
      {mine ? (
        <Notice tone="ok">You already responded ({mine}). You’ll get an alert if the customer accepts.</Notice>
      ) : (
        <>
          <Choice label="Your brokerage" value={terms} onChange={setTerms} options={['15 days rent', '1 month rent', '1% of price', '2% of price'].map((t) => ({ value: t, label: t }))} />
          <Field label="Message to the customer" value={message} onChangeText={setMessage} multiline maxLength={500} />
          <Notice>The customer sees your agency, rating, reviews, response time, terms and match count — not your flat details. Their number is shared only if they accept.</Notice>
          {send.error ? <ErrorBox error={send.error} /> : null}
          <Button title="Send proposal" onPress={() => send.mutate()} busy={send.isPending} testID="send-proposal" />
        </>
      )}
    </Screen>
  );
}
