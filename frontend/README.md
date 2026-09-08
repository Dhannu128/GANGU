# GANGU frontend

Accessible, voice-first grocery assistance built with Next.js, TypeScript, Firebase Authentication, Zustand and Tailwind CSS.

The interface deliberately separates live provider data from estimates and safe demonstrations. A request never skips the final review screen, and real purchasing remains controlled by backend safety flags.

## Local setup

Requirements: Node.js 20 or newer and the GANGU FastAPI backend.

```powershell
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`.

Configure `.env.local` with the local API and Firebase web app values:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_web_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_web_app_id
```

Use the equivalent HTTPS/WSS API origins in Vercel. `NEXT_PUBLIC_*` Firebase web values are public application metadata. Never put an Admin SDK private key or service-account JSON in the frontend.

## Firebase setup

In Firebase Console:

1. Enable Google and Phone under Authentication > Sign-in method.
2. Add `localhost` under Authentication > Settings > Authorized domains.
3. Add the exact Vercel production hostname to Authorized domains.
4. Ensure the backend `FIREBASE_PROJECT_ID` is the same project used by the frontend.
5. Test with a real Google account and a real SMS OTP. There is no dummy OTP or mock login.

The global auth session listener follows Firebase token changes. API calls read the current Firebase ID token, retry once after a forced refresh on `401`, and sign the user out if the refreshed token is rejected. WebSockets use a short-lived ticket issued by the authenticated backend.

## Routes and data boundaries

| Route | Behaviour |
|---|---|
| `/` | Public product explanation and sign-in entry point |
| `/signin` | Redirects to the shared real authentication screen |
| `/signup` | Google or Indian mobile-number Firebase sign-in |
| `/app` | Voice/text request, progress, comparison and final review |
| `/app/orders` | Browser-local order records; provider history is not synchronized |
| `/app/lists` | Browser-local reusable request lists |
| `/app/family` | Browser-local household contacts; no invitation is sent |
| `/app/settings` | Browser-local address and accessibility preferences |

Authenticated routes redirect to `/signin` after Firebase reports that no session exists. Persisted browser data is cleared on sign-out and when a different Firebase user replaces the current session.

## Checks

```powershell
npm run lint
npm run build
```

Voice input depends on the Web Speech API and microphone permission. It may be unavailable in some browsers; text input remains available. Production microphone access requires HTTPS.

## Known gaps

- Firebase providers and production authorized domains must be configured and verified externally.
- Orders, lists, contacts and preferences need authenticated server-side persistence.
- Swiggy live access depends on approval and credentials.
- Estimated catalog results are not evidence that provider checkout is available.
- Real purchases must remain disabled until live provider integration and end-to-end safety tests pass.
