"use client";

import { useState } from "react";
import PageHeader from "@/components/dashboard/PageHeader";
import { CLIENT_ID, API_BASE } from "@/lib/constants";

// ─── Sub-components ───────────────────────────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button
      onClick={copy}
      className="shrink-0 text-xs text-zinc-400 transition-colors hover:text-zinc-100"
    >
      {copied ? "✓ Copied" : "Copy"}
    </button>
  );
}

function CodeBlock({ code }: { code: string }) {
  return (
    <div className="relative rounded-lg border border-zinc-700 bg-zinc-950">
      <div className="absolute right-3 top-3">
        <CopyButton text={code} />
      </div>
      <pre className="overflow-x-auto p-4 pr-16 text-xs leading-relaxed text-zinc-300">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function InlineUrl({ url }: { url: string }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2">
      <code className="flex-1 truncate font-mono text-xs text-zinc-300">{url}</code>
      <CopyButton text={url} />
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function SettingsPage() {
  const [companyName, setCompanyName]   = useState("My Company");
  const [primaryColor, setPrimaryColor] = useState("#2563eb");
  const [greeting, setGreeting]         = useState("Hi! How can I help you today?");

  const widgetUrl  = typeof window !== "undefined" ? window.location.origin : "https://your-app.vercel.app";
  const webhookUrl = `${API_BASE}/api/v1/whatsapp/webhook`;

  const embedCode = `<!-- Paste before </body> on your website -->
<script>
  window.ChatbotConfig = {
    clientId:     "${CLIENT_ID}",
    widgetUrl:    "${widgetUrl}",
    companyName:  "${companyName}",
    primaryColor: "${primaryColor}",
    greeting:     "${greeting}",
  };
</script>
<script src="${widgetUrl}/widget.js" async></script>`;

  return (
    <div>
      <PageHeader title="Settings" description="Widget configuration and integration setup." />

      <div className="space-y-6 p-8">

        {/* ── Embed Widget ─────────────────────────────────────────────── */}
        <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div className="mb-4">
            <h2 className="text-sm font-semibold text-zinc-200">Embed Widget</h2>
            <p className="text-xs text-zinc-500">
              Paste this snippet on any website to add the floating chat widget.
            </p>
          </div>

          {/* Customization controls */}
          <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <label className="block">
              <span className="mb-1 block text-xs text-zinc-400">Company name</span>
              <input
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-zinc-500 transition-colors"
              />
            </label>

            <label className="block">
              <span className="mb-1 block text-xs text-zinc-400">Brand color</span>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="h-9 w-12 cursor-pointer rounded border border-zinc-700 bg-zinc-800 p-1"
                />
                <span className="font-mono text-xs text-zinc-400">{primaryColor}</span>
              </div>
            </label>

            <label className="block">
              <span className="mb-1 block text-xs text-zinc-400">Greeting message</span>
              <input
                value={greeting}
                onChange={(e) => setGreeting(e.target.value)}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-zinc-500 transition-colors"
              />
            </label>
          </div>

          <CodeBlock code={embedCode} />

          <p className="mt-2 text-xs text-zinc-600">
            Widget page:&nbsp;
            <span className="font-mono text-zinc-500">{widgetUrl}/embed/chat</span>
          </p>
        </section>

        {/* ── WhatsApp Integration ─────────────────────────────────────── */}
        <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div className="mb-4 flex items-start justify-between gap-4">
            <div>
              <h2 className="text-sm font-semibold text-zinc-200">WhatsApp Integration</h2>
              <p className="text-xs text-zinc-500">
                Connect a WhatsApp Business number via Meta Cloud API — free for the first 1,000 conversations/month.
              </p>
            </div>
            <span className="shrink-0 rounded-full border border-yellow-800/50 bg-yellow-950/40 px-2.5 py-0.5 text-xs text-yellow-400">
              Setup required
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <p className="mb-1.5 text-xs text-zinc-400">
                Webhook URL — paste this in the Meta App dashboard
              </p>
              <InlineUrl url={webhookUrl} />
            </div>

            <ol className="space-y-1.5 text-xs text-zinc-500">
              {[
                "Go to developers.facebook.com → create a Business app → add WhatsApp product",
                "API Setup page → copy Phone Number ID → generate a System User access token",
                "Webhooks tab → set Callback URL to the webhook URL above, set Verify Token (any string you choose)",
                "Subscribe to the 'messages' field under whatsapp_business_account",
                "Add META_WHATSAPP_TOKEN, META_PHONE_NUMBER_ID, META_WEBHOOK_VERIFY_TOKEN, META_APP_SECRET to backend env vars",
                "Redeploy the backend — messages will arrive as JSON and replies go out via the Graph API",
              ].map((step, i) => (
                <li key={i} className="flex gap-2">
                  <span className="shrink-0 font-mono text-zinc-600">{i + 1}.</span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
        </section>

        {/* ── Environment info ─────────────────────────────────────────── */}
        <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <h2 className="mb-4 text-sm font-medium text-zinc-300">Environment</h2>
          <dl className="space-y-3">
            {[
              { label: "Client ID",  value: CLIENT_ID },
              { label: "API Base",   value: API_BASE },
              { label: "Widget URL", value: widgetUrl },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center gap-4">
                <dt className="w-28 shrink-0 text-xs text-zinc-500">{label}</dt>
                <dd className="font-mono text-xs text-zinc-300">{value}</dd>
              </div>
            ))}
          </dl>
        </section>

      </div>
    </div>
  );
}
