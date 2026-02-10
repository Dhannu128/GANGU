/* GANGU Static Frontend
 * - Chat UI
 * - Voice input via Web Speech API
 * - Live agent workflow via WebSocket (/ws/{session_id})
 * - Purchase confirmation via /api/order/confirm
 */

const API_BASE = ""; // same-origin (FastAPI)

/* ── Step definitions ──
 * The pipeline branches after Task Planning:
 *   Purchase path: Search → Comparison → Decision → Purchase → Notification
 *   Info/RAG path: Knowledge (RAG)
 * We track which path is active so grayed-out steps give a clear signal.
 */
const STEPS_COMMON = [
  { id: "init", label: "Init" },
  { id: "intent_extraction", label: "Intent Extraction", icon: "🧠" },
  { id: "task_planning", label: "Task Planning", icon: "📋" },
];

const STEPS_PURCHASE = [
  { id: "search", label: "Search", icon: "🔍" },
  { id: "comparison", label: "Comparison", icon: "⚖️" },
  { id: "decision", label: "Decision", icon: "🎯" },
  { id: "purchase", label: "Purchase", icon: "🛒" },
  { id: "notification", label: "Notification", icon: "🔔" },
];

const STEPS_INFO = [
  { id: "query_info", label: "Knowledge (RAG)", icon: "📚" },
];

// Flat list for state management (all possible steps)
const STEPS = [...STEPS_COMMON, ...STEPS_PURCHASE, ...STEPS_INFO];

// Active pipeline path: "unknown" | "purchase" | "info"
let activePath = "unknown";

const els = {
  workflow: document.getElementById("workflow"),
  chat: document.getElementById("chat"),
  message: document.getElementById("message"),
  btnSend: document.getElementById("btnSend"),
  btnMic: document.getElementById("btnMic"),
  btnClear: document.getElementById("btnClear"),
  btnCancel: document.getElementById("btnCancel"),
  btnNewSession: document.getElementById("btnNewSession"),
  sessionId: document.getElementById("sessionId"),
  connBadge: document.getElementById("connBadge"),
  btnTheme: document.getElementById("btnTheme"),
  btnToggleDebug: document.getElementById("btnToggleDebug"),
  debugPanel: document.getElementById("debugPanel"),
  debugFeed: document.getElementById("debugFeed"),
  recommendations: document.getElementById("recommendations"),
  products: document.getElementById("products"),
  btnSpeak: document.getElementById("btnSpeak"),
  typing: document.getElementById("typing"),
  inspectorStep: document.getElementById("inspectorStep"),
  inspectorStatus: document.getElementById("inspectorStatus"),
  inspectorMsg: document.getElementById("inspectorMsg"),
  inspectorData: document.getElementById("inspectorData"),
  chips: document.getElementById("chips"),
};

function nowIso() {
  return new Date().toISOString();
}

function newSessionId() {
  const n = Math.random().toString(16).slice(2);
  return `web_${Date.now()}_${n}`;
}

let sessionId = localStorage.getItem("gangu.sessionId") || newSessionId();
localStorage.setItem("gangu.sessionId", sessionId);
els.sessionId.textContent = sessionId;

let ws = null;
let stepStatus = Object.fromEntries(STEPS.map((s) => [s.id, "idle"]));
let stepLast = Object.fromEntries(STEPS.map((s) => [s.id, null]));
let selectedStep = "intent_extraction";

let ttsEnabled = localStorage.getItem("gangu.tts") === "true";
setSpeakButton();

let compactEnabled = localStorage.getItem("gangu.compact") === "true";
document.body.classList.toggle("compact", compactEnabled);
setCompactButton();

function setSpeakButton() {
  els.btnSpeak.classList.toggle("btn-primary", ttsEnabled);
  els.btnSpeak.classList.toggle("btn-ghost", !ttsEnabled);
  els.btnSpeak.textContent = ttsEnabled ? "TTS: On" : "TTS: Off";
}

function setCompactButton() {
  if (!els.btnTheme) return;
  els.btnTheme.classList.toggle("btn-primary", compactEnabled);
  els.btnTheme.classList.toggle("btn-ghost", !compactEnabled);
  els.btnTheme.textContent = compactEnabled ? "Compact: On" : "Compact: Off";
}

function setConnBadge(state) {
  els.connBadge.classList.remove("badge-ok", "badge-warn", "badge-err");
  if (state === "connected") {
    els.connBadge.classList.add("badge-ok");
    els.connBadge.textContent = "Connected";
  } else if (state === "connecting") {
    els.connBadge.classList.add("badge-warn");
    els.connBadge.textContent = "Connecting";
  } else {
    els.connBadge.classList.add("badge-warn");
    els.connBadge.textContent = "Disconnected";
  }
}

function appendDebug(obj) {
  const line = `[${nowIso()}] ${JSON.stringify(obj)}\n`;
  els.debugFeed.textContent = (els.debugFeed.textContent + line).slice(-12000);
  els.debugFeed.scrollTop = els.debugFeed.scrollHeight;
}

function badgeForStatus(status) {
  if (!status) return "badge-warn";
  if (status === "complete") return "badge-ok";
  if (status === "error") return "badge-err";
  if (status === "processing") return "badge-warn";
  return "badge-warn";
}

function setInspector(stepId) {
  selectedStep = stepId;
  const s = STEPS.find((x) => x.id === stepId);
  const last = stepLast[stepId];
  const status = stepStatus[stepId];

  els.inspectorStep.textContent = s ? s.label : stepId;
  els.inspectorStatus.className = `badge ${badgeForStatus(status)}`;
  els.inspectorStatus.textContent = status === "idle" ? "waiting" : (status || "—");
  els.inspectorMsg.textContent = last?.message || "";

  const data = last?.data ?? null;
  els.inspectorData.textContent = data ? JSON.stringify(data, null, 2) : "(no data yet)";

  // highlight selected item
  for (const el of els.workflow.querySelectorAll(".workflow-item")) {
    el.classList.toggle("selected", el.dataset.stepId === stepId);
  }
}

function renderWorkflow() {
  els.workflow.innerHTML = "";

  // Determine which steps belong to the active vs inactive path
  const purchaseIds = new Set(STEPS_PURCHASE.map(s => s.id));
  const infoIds = new Set(STEPS_INFO.map(s => s.id));

  // Ordered list for display: common → branch
  let displaySteps;
  if (activePath === "purchase") {
    displaySteps = [...STEPS_COMMON.filter(s => s.id !== "init"), ...STEPS_PURCHASE];
  } else if (activePath === "info") {
    displaySteps = [...STEPS_COMMON.filter(s => s.id !== "init"), ...STEPS_INFO];
  } else {
    // Unknown yet — show all, info path at bottom
    displaySteps = [...STEPS_COMMON.filter(s => s.id !== "init"), ...STEPS_PURCHASE, ...STEPS_INFO];
  }

  // Insert branch divider after task_planning
  let branchInserted = false;

  for (const step of displaySteps) {
    // Insert branch label right before the first post-planning step
    if (!branchInserted && (purchaseIds.has(step.id) || infoIds.has(step.id))) {
      branchInserted = true;
      const divider = document.createElement("li");
      divider.className = "workflow-branch-label";
      if (activePath === "purchase") {
        divider.innerHTML = '<span class="branch-icon">🛒</span> Purchase Path';
      } else if (activePath === "info") {
        divider.innerHTML = '<span class="branch-icon">📚</span> Info / RAG Path';
      } else {
        divider.innerHTML = '<span class="branch-icon">⑂</span> Awaiting routing…';
      }
      els.workflow.appendChild(divider);
    }

    // Is this step on the inactive path?
    const isInactivePurchase = activePath === "info" && purchaseIds.has(step.id);
    const isInactiveInfo = activePath === "purchase" && infoIds.has(step.id);
    const dimmed = isInactivePurchase || isInactiveInfo;

    const li = document.createElement("li");
    li.className = "workflow-item" + (dimmed ? " workflow-dimmed" : "");
    li.dataset.stepId = step.id;
    li.onclick = () => setInspector(step.id);

    const dot = document.createElement("div");
    const st = stepStatus[step.id];
    dot.className = "workflow-dot " + (
      dimmed ? "dot-skip" :
        st === "processing" ? "dot-run" :
          st === "complete" ? "dot-ok" :
            st === "error" ? "dot-err" :
              "dot-idle"
    );

    const wrap = document.createElement("div");
    wrap.style.minWidth = "0";

    const title = document.createElement("div");
    title.className = "text-sm font-semibold flex items-center gap-1.5";
    if (step.icon) {
      const iconSpan = document.createElement("span");
      iconSpan.className = "workflow-icon";
      iconSpan.textContent = step.icon;
      title.appendChild(iconSpan);
    }
    const labelSpan = document.createElement("span");
    labelSpan.textContent = step.label;
    title.appendChild(labelSpan);

    const meta = document.createElement("div");
    meta.className = "text-xs text-slate-400";
    const last = stepLast[step.id];
    const status = stepStatus[step.id];
    if (dimmed) {
      meta.textContent = "Skipped";
    } else {
      const statusLabel = status === "idle" ? "Waiting" : status;
      meta.textContent = last?.message ? `${statusLabel} • ${last.message}` : statusLabel;
    }

    wrap.appendChild(title);
    wrap.appendChild(meta);
    li.appendChild(dot);
    li.appendChild(wrap);
    els.workflow.appendChild(li);
  }

  // keep selection styling
  setInspector(selectedStep);
}

function setStep(step, status) {
  if (!step) return;
  // normalize API step names to our STEPS ids
  const map = {
    task_planning: "task_planning",
    task_planner: "task_planning",
    intent_extraction: "intent_extraction",
    query_info_only: "query_info",
  };
  const id = map[step] || step;
  if (!(id in stepStatus)) return;
  stepStatus[id] = status;
  renderWorkflow();
}

function showTyping(isOn) {
  if (!els.typing) return;
  els.typing.hidden = !isOn;
}

function safeMarkdownToHtml(text) {
  try {
    if (!text) return "";
    if (!window.marked || !window.DOMPurify) {
      return `<div class=\"md\">${escapeHtml(text)}</div>`;
    }
    const raw = window.marked.parse(text, { breaks: true, gfm: true });
    const clean = window.DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } });
    return `<div class=\"md\">${clean}</div>`;
  } catch {
    return `<div class=\"md\">${escapeHtml(text)}</div>`;
  }
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function addMsg(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role}`;
  avatar.textContent = role === "user" ? "You" : "G";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (role === "assistant") {
    bubble.innerHTML = safeMarkdownToHtml(text);
  } else {
    bubble.textContent = text;
  }

  if (role === "assistant") {
    wrap.appendChild(avatar);
    wrap.appendChild(bubble);
  } else {
    wrap.appendChild(bubble);
    wrap.appendChild(avatar);
  }
  els.chat.appendChild(wrap);
  els.chat.scrollTop = els.chat.scrollHeight;

  if (role === "assistant" && ttsEnabled) {
    speak(text);
  }
}

function speak(text) {
  try {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "hi-IN";
    u.rate = 1.0;
    window.speechSynthesis.speak(u);
  } catch {
    // ignore
  }
}

function resetWorkflow() {
  stepStatus = Object.fromEntries(STEPS.map((s) => [s.id, "idle"]));
  stepLast = Object.fromEntries(STEPS.map((s) => [s.id, null]));
  activePath = "unknown";
  renderWorkflow();
}

function showRecommendations(products) {
  els.products.innerHTML = "";
  if (!products || products.length === 0) {
    els.recommendations.hidden = true;
    return;
  }
  els.recommendations.hidden = false;

  products.slice(0, 6).forEach((p, idx) => {
    const card = document.createElement("div");
    card.className = "product-card";

    const title = document.createElement("div");
    title.className = "product-title";
    title.textContent = p.item_name || p.name || "Product";

    const meta = document.createElement("div");
    meta.className = "product-meta mt-1";
    const platform = p.platform || "Unknown";
    const price = p.unit_price_label || p.price || p.normalized_attributes?.unit_price_label || "N/A";
    const delivery = p.delivery_time_label || p.delivery_time || p.normalized_attributes?.delivery_time_label || "";
    const score = p.scores?.final_score ?? p.score;
    meta.textContent = `${platform} • ${price}${delivery ? " • " + delivery : ""}${(score !== undefined && score !== null) ? " • score " + score : ""}`;

    const actions = document.createElement("div");
    actions.className = "product-actions";

    const btn = document.createElement("button");
    btn.className = "btn btn-primary w-full";
    btn.textContent = "Confirm";
    btn.onclick = () => confirmOrder(idx);

    actions.appendChild(btn);
    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(actions);
    els.products.appendChild(card);
  });
}

async function confirmOrder(index) {
  addMsg("assistant", `Placing order for option #${index + 1}…`);
  try {
    const res = await fetch(`${API_BASE}/api/order/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, selected_product_index: index }),
    });
    const data = await res.json();
    appendDebug({ type: "confirm_response", data });

    if (!res.ok || !data.success) {
      addMsg("assistant", `Order failed: ${data.detail || data.message || "Unknown error"}`);
      return;
    }

    addMsg("assistant", `✅ Order placed! Order ID: ${data.order_id || "(unknown)"}`);
    els.recommendations.hidden = true;
  } catch (e) {
    addMsg("assistant", `Order failed: ${e?.message || String(e)}`);
  }
}

function connectWs() {
  if (ws) {
    try { ws.close(); } catch { }
    ws = null;
  }

  setConnBadge("connecting");
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/${sessionId}`);

  ws.onopen = () => setConnBadge("connected");
  ws.onclose = () => setConnBadge("disconnected");
  ws.onerror = () => setConnBadge("disconnected");

  ws.onmessage = (ev) => {
    let msg;
    try { msg = JSON.parse(ev.data); } catch { return; }
    appendDebug(msg);

    if (msg.type === "agent_update") {
      setStep(msg.step, msg.status);

      // ── Detect pipeline branch ──
      // When search starts processing → purchase path
      if (msg.step === "search" && (msg.status === "processing" || msg.status === "complete")) {
        if (activePath !== "purchase") {
          activePath = "purchase";
          renderWorkflow();
        }
      }
      // When query_info completes → info/RAG path
      if (msg.step === "query_info" && (msg.status === "processing" || msg.status === "complete")) {
        if (activePath !== "info") {
          activePath = "info";
          renderWorkflow();
        }
      }

      // store the last update for inspector
      const map = {
        task_planner: "task_planning",
      };
      const sid = map[msg.step] || msg.step;
      if (sid in stepLast) {
        stepLast[sid] = { message: msg.message, data: msg.data, status: msg.status, ts: msg.timestamp };
      }

      // keep inspector fresh
      setInspector(selectedStep);

      if (msg.message) {
        // Narrate key step transitions into chat
        const narrateSteps = ["intent_extraction", "task_planning", "search", "comparison", "decision", "query_info"];
        if (narrateSteps.includes(msg.step) && msg.status === "complete") {
          const icon = STEPS.find(s => s.id === msg.step)?.icon || "•";
          addMsg("assistant", `${icon} ${msg.step.replace(/_/g, " ")}: ${msg.message}`);
        }
      }
    }
  };

  // heartbeat every 25s so server loop stays happy
  setInterval(() => {
    try {
      if (ws && ws.readyState === WebSocket.OPEN) ws.send("ping");
    } catch { }
  }, 25000);
}

async function sendMessage() {
  const text = (els.message.value || "").trim();
  if (!text) return;
  els.message.value = "";

  resetWorkflow();
  els.recommendations.hidden = true;
  showTyping(true);

  addMsg("user", text);
  setStep("intent_extraction", "processing");

  try {
    const res = await fetch(`${API_BASE}/api/chat/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });

    const data = await res.json();
    appendDebug({ type: "chat_response", data });

    if (!res.ok || !data.success) {
      showTyping(false);
      addMsg("assistant", `Error: ${data.detail || data.message || "Unknown error"}`);
      return;
    }

    showTyping(false);

    if (data.ai_response) addMsg("assistant", data.ai_response);

    // Detect path from response data
    if (data.rag_metadata && data.rag_metadata.sources_used > 0) {
      // Info/RAG path was used
      activePath = "info";
      setStep("query_info", "complete");
      if (!stepLast["query_info"]) {
        stepLast["query_info"] = {
          message: `Answered from ${data.rag_metadata.sources_used} knowledge sources`,
          data: data.rag_metadata,
          status: "complete",
        };
      }
    } else {
      // Purchase path
      if (activePath !== "info") activePath = "purchase";
    }

    // show products for confirmation
    const ranked = data.ranked_products || [];
    if (data.requires_confirmation && ranked.length) {
      showRecommendations(ranked);
    } else {
      els.recommendations.hidden = true;
    }

    // mark final step done
    if (activePath === "info") {
      setStep("query_info", "complete");
    } else {
      setStep("notification", "complete");
    }

  } catch (e) {
    showTyping(false);
    addMsg("assistant", `Network error: ${e?.message || String(e)}`);
  }
}

// Voice input via Web Speech API
let recognizer = null;
let listening = false;

function setupSpeech() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    els.btnMic.textContent = "Mic (N/A)";
    els.btnMic.disabled = true;
    return;
  }

  recognizer = new SR();
  recognizer.lang = "hi-IN";
  recognizer.interimResults = true;
  recognizer.maxAlternatives = 1;

  recognizer.onstart = () => {
    listening = true;
    els.btnMic.textContent = "Listening…";
    els.btnMic.classList.add("btn-primary");
    els.btnMic.classList.remove("btn-secondary");
  };

  recognizer.onend = () => {
    listening = false;
    els.btnMic.textContent = "Mic";
    els.btnMic.classList.remove("btn-primary");
    els.btnMic.classList.add("btn-secondary");
  };

  recognizer.onerror = (e) => {
    appendDebug({ type: "speech_error", error: e.error });
  };

  recognizer.onresult = (event) => {
    let finalText = "";
    let interimText = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const t = event.results[i][0]?.transcript || "";
      if (event.results[i].isFinal) finalText += t;
      else interimText += t;
    }

    if (interimText) {
      els.message.value = interimText;
    }

    if (finalText) {
      els.message.value = finalText.trim();
      // auto-send for voice UX
      sendMessage();
    }
  };
}

// Wire UI
renderWorkflow();
connectWs();
setupSpeech();

// default inspector selection
setInspector(selectedStep);

els.btnSend.addEventListener("click", sendMessage);
els.message.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) sendMessage();
  if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.metaKey) sendMessage();
});

els.btnClear.addEventListener("click", () => {
  els.chat.innerHTML = "";
  els.debugFeed.textContent = "";
  els.recommendations.hidden = true;
  resetWorkflow();
});

if (els.btnToggleDebug && els.debugPanel) {
  els.btnToggleDebug.addEventListener("click", () => {
    const show = els.debugPanel.hidden;
    els.debugPanel.hidden = !show;
  });
}

els.btnCancel.addEventListener("click", async () => {
  try {
    await fetch(`${API_BASE}/api/cancel`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
    addMsg("assistant", "⏹️ Cancel requested.");
  } catch (e) {
    addMsg("assistant", `Cancel failed: ${e?.message || String(e)}`);
  }
});

els.btnNewSession.addEventListener("click", () => {
  sessionId = newSessionId();
  localStorage.setItem("gangu.sessionId", sessionId);
  els.sessionId.textContent = sessionId;
  resetWorkflow();
  els.chat.innerHTML = "";
  els.debugFeed.textContent = "";
  els.recommendations.hidden = true;
  connectWs();
});

if (els.btnTheme) {
  els.btnTheme.addEventListener("click", () => {
    compactEnabled = !compactEnabled;
    localStorage.setItem("gangu.compact", String(compactEnabled));
    document.body.classList.toggle("compact", compactEnabled);
    setCompactButton();
  });
}

els.btnMic.addEventListener("click", () => {
  if (!recognizer) return;
  try {
    if (!listening) recognizer.start();
    else recognizer.stop();
  } catch (e) {
    appendDebug({ type: "speech_start_error", error: e?.message || String(e) });
  }
});

els.btnSpeak.addEventListener("click", () => {
  ttsEnabled = !ttsEnabled;
  localStorage.setItem("gangu.tts", String(ttsEnabled));
  setSpeakButton();
  addMsg("assistant", ttsEnabled ? "Text-to-speech enabled." : "Text-to-speech disabled.");
});

// Welcome message
addMsg(
  "assistant",
  "**Namaste!** Main **GANGU** hoon.\n\n- Aap **bol kar** ya **type** karke order de sakte hain\n- Main **search → compare → decide** karke best options dikhata hoon\n- Aap **Confirm** karoge to order place kar dunga (COD)\n- Koi bhi **sawaal** poocho — 📚 RAG knowledge se jawab dunga"
);

// Suggestion chips
const SUGGESTIONS = [
  { label: "Cadbury urgent", text: "Cadbury Dairy Milk 2 le aao, urgent" },
  { label: "Milk", text: "Doodh 1 litre le aao" },
  { label: "Atta", text: "Aata 5kg order kar do" },
  { label: "Haldi info", text: "Haldi kya hoti hai?" },
  { label: "GANGU help", text: "Gangu par order kaise karte hain?" },
];

function renderChips() {
  if (!els.chips) return;
  els.chips.innerHTML = "";
  SUGGESTIONS.forEach((s, idx) => {
    const btn = document.createElement("button");
    btn.className = "chip";
    btn.type = "button";
    btn.innerHTML = `${escapeHtml(s.label)} <kbd>${idx + 1}</kbd>`;
    btn.onclick = () => {
      els.message.value = s.text;
      els.message.focus();
      sendMessage();
    };
    els.chips.appendChild(btn);
  });
}

renderChips();

// Alt+1..5 triggers chips
window.addEventListener("keydown", (e) => {
  if (!e.altKey) return;
  const n = Number(e.key);
  if (!Number.isFinite(n)) return;
  const s = SUGGESTIONS[n - 1];
  if (!s) return;
  e.preventDefault();
  els.message.value = s.text;
  sendMessage();
});
