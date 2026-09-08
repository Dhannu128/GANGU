# Swiggy readiness review — 8 September 2026

## Outcome

The callback URL requested in the email is:

`https://gangu-api.onrender.com/api/auth/callback/swiggy`

It matches the existing deployment configuration. External GET checks returned a healthy GANGU API (200) and a callback validation response (422, missing code and state). This establishes public reachability and route existence, not successful OAuth or ownership verification. An earlier request timed out; investigate hosting cold starts before a demo. Send the exact URI without query parameters or a trailing slash.

The email says the integration agreement is signed and asks for a URI to update the whitelist. It does not establish that production access is enabled or that the complete project has passed a technical review. No new form is requested.

## Failures found and repairs

1. Only the frontend was listening locally; port 8000 had no backend. Started `python api/main.py`. Health returned 200; unauthenticated chat returned 401; localhost frontend CORS preflight returned 200. Authentication remains enabled.
2. Gemini rejected `gemini-2.5-flash` for this account with 404 and suggested `gemini-3.6-flash`. Updated the shared default, example configuration and Render model configuration. The replacement returned OK; actual intent extraction preserved both wheat flour and 2 kg from “2 kg atta”. Explicit deployed LLM_MODEL environment settings must also be updated.
3. The frontend collapsed all failures into one error. Added distinct connection, timeout, sign-in, conflict, busy and unavailable messages. Confirmation failures no longer assert that no order exists when the result cannot be verified.
4. WebSocket configuration now derives from the API URL when no separate URL is set, preventing a public HTTP API from silently pairing with a localhost WebSocket.
5. OAuth token exchange now uses the JSON request body documented by Swiggy. Added a mocked exchange test covering PKCE verifier, exact redirect, token storage and replay rejection.
6. Render configuration now requires the actual callback and registered client ID instead of silently assuming a service hostname. Changes are local; the deployed server has not been updated by this review.

## Architecture and readiness

| Area | Evidence and remaining work |
| --- | --- |
| Frontend | Next.js, Firebase sign-in, Zustand state, Axios HTTP and authenticated WebSocket tickets. Local UI calls localhost:8000 unless configured otherwise. |
| Backend | FastAPI with LangGraph: intent, planning, search, comparison, decision and confirmation. Local startup and basic connectivity verified. |
| AI | Shared Gemini client repaired and intent extraction tested. Complete multi-agent latency and failure behavior still need an end-to-end run. |
| OAuth | Start and public callback routes exist; S256 PKCE and single-use state implemented. Local SWIGGY_CLIENT_ID and SWIGGY_REDIRECT_URI are absent. No real phone/OTP authorization or token exchange was completed. Obtain/register the client identity through the appropriate Swiggy onboarding flow. |
| Swiggy search | The active adapter targets localhost:8001/sse and labels results mock_swiggy_mcp. It is not the official authenticated Streamable HTTP Instamart integration. |
| User tokens | OAuth tokens can be stored per user, but access_token_for is not wired into the active search client. Public users must never share one developer token. |
| Product data | Mock adapter supplies fallback prices, ratings and synthetic IDs. These cannot be presented as live Swiggy facts or used for real checkout. |
| Checkout | Existing mock client uses food cart tool names. Real groceries require the official Instamart schema, provider product/address/cart IDs and provider-authoritative totals. |
| Safety | Owner-isolated sessions, expiring single-use quotes and confirmation guards are covered by tests. Keep real purchasing disabled until verified. |
| Persistence | Default memory state disappears on restart. Existing MongoDB storage encrypts OAuth tokens; provision and test it before multi-worker production use. |

GANGU's household/elderly grocery use case fits the program's stated categories. It is ready to provide its callback for the whitelist update, but is not yet demonstrated ready for live production shopping.

## What Swiggy evaluates

Their current access documentation lists a concrete use case, user confirmation, working OAuth, 401/429 handling, safe retries, expected traffic and HTTPS/security basics. Their production checklist additionally calls for staging verification, correct tool/server selection, authoritative items and totals at confirmation, observability and appropriate data handling. These are published criteria; the email itself asks only for the callback URL.

Before a live demonstration: deploy these repairs, configure the exact callback and registered client ID, complete per-user OAuth, connect the official Instamart client with each user's token, test address → search → cart → displayed total → explicit confirmation → order status in staging, and exercise expired authentication, unavailable stock and ambiguous checkout outcomes. Never blindly retry checkout after a timeout. Record a short working-flow video and label simulated data clearly. Do not claim staging or production tests that have not been performed.

## Email reply

Hi Swiggy Builders Club Team,

Thank you for the update. Please whitelist the following exact non-local redirect URI for GANGU – Geriatric Assistant for Networked Guidance and Utility:

https://gangu-api.onrender.com/api/auth/callback/swiggy

This is our backend OAuth callback endpoint. Please confirm once the whitelist update is complete and let us know the next integration/testing steps.

Best regards,
DHANNU

## Verification and limits

- 13 backend safety/OAuth tests passed.
- Frontend ESLint and TypeScript checks passed.
- Real Gemini smoke test and intent extraction passed after the model change.
- Local API health, auth protection and frontend CORS checked.
- Public GANGU health, OpenAPI OAuth routes and callback validation checked.
- Full signed-in UI flow, Swiggy authorization, official live search/checkout and public deployment of the new changes remain unverified. No orders were placed and no email was sent.

## Sources

- https://mcp.swiggy.com/builders/docs/start/authenticate/
- https://mcp.swiggy.com/builders/docs/operate/access/
- https://mcp.swiggy.com/builders/docs/build/ship-to-production/
- https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash
