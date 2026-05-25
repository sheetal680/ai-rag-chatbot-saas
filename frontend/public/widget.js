/*!
 * AI RAG Chatbot Widget v0.1.0
 * Drop-in embed script — no build step required.
 *
 * Usage:
 *   <script>
 *     window.ChatbotConfig = {
 *       clientId:     "acme",                         // your tenant ID
 *       widgetUrl:    "https://your-app.vercel.app",  // where this Next.js app lives
 *       apiUrl:       "https://your-api.railway.app", // optional — falls back to widgetUrl's backend
 *       primaryColor: "#2563eb",
 *       companyName:  "ACME Support",
 *       greeting:     "Hi! How can I help?",
 *       position:     "bottom-right",   // "bottom-right" | "bottom-left"
 *       autoOpen:     false,
 *     };
 *   </script>
 *   <script src="https://your-app.vercel.app/widget.js" async></script>
 */
(function () {
  "use strict";

  /* Capture currentScript immediately — async scripts can't rely on it later */
  var _script = document.currentScript;

  /* ── Config ──────────────────────────────────────────────────────────────── */
  var cfg = window.ChatbotConfig || {};
  var clientId    = cfg.clientId     || "default";
  var apiUrl      = cfg.apiUrl       || "";
  var primaryColor= cfg.primaryColor || "#2563eb";
  var companyName = cfg.companyName  || "AI Assistant";
  var greeting    = cfg.greeting     || "Hi! How can I help you today?";
  var position    = cfg.position     || "bottom-right";
  var autoOpen    = cfg.autoOpen     === true;

  /* Derive where the Next.js app is hosted (script src origin) */
  function getWidgetBase() {
    if (cfg.widgetUrl) return cfg.widgetUrl.replace(/\/$/, "");
    if (_script && _script.src) {
      try { return new URL(_script.src).origin; } catch (_) {}
    }
    return window.location.origin;
  }
  var widgetBase = getWidgetBase();

  /* ── State ───────────────────────────────────────────────────────────────── */
  var isOpen = false;
  var launcher, container;

  /* ── SVG icons ───────────────────────────────────────────────────────────── */
  var ICON_CHAT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24"' +
    ' fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>' +
    "</svg>"
  );
  var ICON_CLOSE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"' +
    ' fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<line x1="18" y1="6" x2="6" y2="18"/>' +
    '<line x1="6" y1="6" x2="18" y2="18"/>' +
    "</svg>"
  );

  /* ── CSS injection ───────────────────────────────────────────────────────── */
  function injectStyles() {
    var isLeft = position === "bottom-left";
    var sideRule = isLeft ? "left:24px;" : "right:24px;";
    var origin   = isLeft ? "bottom left" : "bottom right";

    var css = [
      /* Launcher button */
      "#cb-launcher{",
        "position:fixed;bottom:24px;", sideRule,
        "z-index:2147483647;",
        "width:60px;height:60px;border-radius:50%;",
        "background:", primaryColor, ";",
        "border:none;cursor:pointer;",
        "display:flex;align-items:center;justify-content:center;",
        "color:#fff;",
        "box-shadow:0 4px 20px rgba(0,0,0,.28);",
        "transition:transform .2s ease,box-shadow .2s ease;",
        "outline:none;",
      "}",
      "#cb-launcher:hover{transform:scale(1.08);box-shadow:0 6px 30px rgba(0,0,0,.38);}",

      /* Iframe container — hidden by default, slides up on open */
      "#cb-frame-wrap{",
        "position:fixed;bottom:96px;", sideRule,
        "z-index:2147483646;",
        "opacity:0;pointer-events:none;",
        "transform:translateY(14px) scale(.97);",
        "transform-origin:", origin, ";",
        "transition:opacity .25s ease,transform .25s ease;",
      "}",
      "#cb-frame-wrap.cb-open{",
        "opacity:1;pointer-events:auto;",
        "transform:translateY(0) scale(1);",
      "}",
      "#cb-frame-wrap iframe{",
        "width:380px;height:600px;",
        "border:none;border-radius:16px;display:block;",
        "box-shadow:0 20px 60px rgba(0,0,0,.35),0 0 0 1px rgba(255,255,255,.06);",
      "}",

      /* Full-screen on small phones */
      "@media(max-width:440px){",
        "#cb-frame-wrap{",
          "top:0!important;bottom:0!important;",
          "left:0!important;right:0!important;",
          "width:100%!important;",
        "}",
        "#cb-frame-wrap iframe{",
          "width:100%!important;height:100%!important;",
          "border-radius:0!important;",
        "}",
      "}",
    ].join("");

    var tag = document.createElement("style");
    tag.textContent = css;
    document.head.appendChild(tag);
  }

  /* ── Build iframe src ────────────────────────────────────────────────────── */
  function buildSrc() {
    var pairs = [
      "clientId="     + encodeURIComponent(clientId),
      "primaryColor=" + encodeURIComponent(primaryColor),
      "companyName="  + encodeURIComponent(companyName),
      "greeting="     + encodeURIComponent(greeting),
    ];
    if (apiUrl) pairs.push("apiUrl=" + encodeURIComponent(apiUrl));
    return widgetBase + "/embed/chat?" + pairs.join("&");
  }

  /* ── Open / Close / Toggle ───────────────────────────────────────────────── */
  function open() {
    if (isOpen) return;
    isOpen = true;
    container.classList.add("cb-open");
    launcher.innerHTML = ICON_CLOSE;
    launcher.setAttribute("aria-label", "Close chat");
    launcher.setAttribute("aria-expanded", "true");
  }

  function close() {
    if (!isOpen) return;
    isOpen = false;
    container.classList.remove("cb-open");
    launcher.innerHTML = ICON_CHAT;
    launcher.setAttribute("aria-label", "Open chat");
    launcher.setAttribute("aria-expanded", "false");
  }

  function toggle() { isOpen ? close() : open(); }

  /* ── Init ────────────────────────────────────────────────────────────────── */
  function init() {
    if (document.getElementById("cb-launcher")) return; /* idempotent */

    injectStyles();

    /* Floating button */
    launcher = document.createElement("button");
    launcher.id = "cb-launcher";
    launcher.setAttribute("aria-label", "Open chat");
    launcher.setAttribute("aria-expanded", "false");
    launcher.setAttribute("aria-haspopup", "dialog");
    launcher.innerHTML = ICON_CHAT;
    launcher.addEventListener("click", toggle);

    /* Iframe wrapper */
    container = document.createElement("div");
    container.id = "cb-frame-wrap";
    container.setAttribute("role", "dialog");
    container.setAttribute("aria-label", companyName + " chat");

    var iframe = document.createElement("iframe");
    iframe.src     = buildSrc();
    iframe.title   = companyName + " Chat";
    iframe.loading = "lazy";
    iframe.setAttribute("allow", "microphone");

    container.appendChild(iframe);
    document.body.appendChild(container);
    document.body.appendChild(launcher);

    /* PostMessage bridge: embed page can ask us to open or close */
    window.addEventListener("message", function (e) {
      if (!e.data || typeof e.data !== "object") return;
      if (e.data.type === "chatbot:close") close();
      if (e.data.type === "chatbot:open")  open();
    });

    /* ESC key closes the widget */
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen) close();
    });

    if (autoOpen) open();

    /* Public JavaScript API */
    window.ChatbotWidget = { open: open, close: close, toggle: toggle };
  }

  /* Run after DOM is ready */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
