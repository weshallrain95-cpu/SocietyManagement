# Only Broker — mobile app (broker + field staff)

Expo SDK 57 · React Native 0.86 · Expo Router · TypeScript. One codebase for Android, iOS and web.

## Run

```bash
npm install
npm run web:demo          # in a browser, demo data kept on the device — no server needed
npx expo start            # on a phone: scan the QR code with Expo Go
```

Live mode talks to the backend (`broker-only/backend`). Set the server address in the app
(Login → Server settings) or at build time: `EXPO_PUBLIC_API_URL=http://<laptop-ip>:8000 npx expo start`.

Demo logins: broker `9820000001`, field staff `9820010000`, OTP `123456`.
Against the dev server, the OTP is shown on screen (development only).

## What's inside

| Path | What |
|------|------|
| `src/app/(broker)/` | Broker tabs: Today, Leads, Customers, Flats, More |
| `src/app/(staff)/` | Field staff: My day (works offline), Account |
| `src/app/listing`, `customer`, `match`, `visit`, `lead` | Detail and flow screens |
| `src/api/http.ts` | Typed client for `/v1` with token refresh |
| `src/api/demo.ts` | In-app demo backend (same contract) for previews and UI work |
| `src/lib/offlineQueue.ts` | Offline action queue with idempotency keys (PRD OFF-10/11) |
| `src/lib/live.ts` | WebSocket live alerts with heartbeat and reconnect |
| `src/lib/format.ts` | India-time dates/times, ₹ lakh/crore, phone formatting |

## Checks

```bash
npm run typecheck && npx expo lint && npm test
```

Timezone rule: dates and times always use India time (`Asia/Kolkata`), whatever the device timezone.
