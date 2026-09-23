import { router } from 'expo-router';
import React, { useState } from 'react';

import { DEMO_FORCED } from '@/api';
import { useSession } from '@/auth/session';
import { Button, Choice, Field, Notice, P, Screen } from '@/ui/components';

export default function Settings() {
  const { settings, updateSettings, signOut } = useSession();
  const [url, setUrl] = useState(settings.baseUrl);
  const [demo, setDemo] = useState(settings.demo ? 'demo' : 'live');

  return (
    <Screen>
      {DEMO_FORCED ? (
        <Notice tone="warn">This build is the online demo. It always uses sample data.</Notice>
      ) : (
        <>
          <Choice
            label="Data source"
            value={demo}
            onChange={setDemo}
            options={[
              { value: 'live', label: 'Only Broker server' },
              { value: 'demo', label: 'Demo (sample data)' },
            ]}
          />
          <Field
            label="Server address"
            value={url}
            onChangeText={setUrl}
            autoCapitalize="none"
            autoCorrect={false}
            hint="On the same Wi-Fi as the dev laptop: http://<laptop-ip>:8000"
          />
          <Button
            title="Save"
            onPress={async () => {
              await signOut();
              await updateSettings({ baseUrl: url.trim(), demo: demo === 'demo' });
              router.replace('/login');
            }}
          />
          <P small muted>Saving signs you out so you can log in against the chosen server.</P>
        </>
      )}
    </Screen>
  );
}
