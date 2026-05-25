# Admin Dashboard Guide

How to use the dashboard to manage your AI chatbot day-to-day.

---

## Accessing the Dashboard

URL: `https://your-app.vercel.app/login`

Sign in with the email and password created during setup. If you've forgotten your password, contact your administrator.

---

## Overview Page

The first page you see after logging in. Shows four key metrics:

| Metric | What it means |
|---|---|
| **Sessions** | Unique conversations started with your chatbot |
| **Messages** | Total messages sent (user + AI combined) |
| **Leads** | Contacts captured through the lead form |
| **Documents** | Files indexed in your knowledge base |

If you see "—" or zeroes, the backend may be starting up — refresh after 30 seconds.

---

## Documents

> **Path:** Dashboard → Documents

This is where you train the AI. Two ways to add content:

### Upload a file
1. Click the **Upload file** tab
2. Select a PDF, DOCX, TXT, or Markdown file
3. Click **Upload & Index**
4. A toast notification confirms the number of chunks indexed

Supported formats: `.pdf` `.docx` `.txt` `.md`

### Ingest a URL
1. Click the **Ingest URL** tab
2. Paste a full URL (e.g. your FAQ page, about page, pricing page)
3. Click **Ingest URL**
4. The page content is fetched, chunked, and indexed automatically

### Deleting a document
Click the trash icon next to any document in the table. This removes it from both the database and the AI's knowledge base immediately.

> **Tip:** After deleting outdated content, always test the chatbot to confirm it no longer references that information.

---

## Conversations

> **Path:** Dashboard → Conversations

Browse the full history of all chatbot sessions.

- **Left panel**: list of sessions, sorted newest first. Click any session to open it.
- **Right panel**: the full message exchange, formatted the same way the user saw it.

Use this to:
- Quality-check AI responses
- Spot gaps in your knowledge base (unanswered questions)
- Find patterns in what customers are asking

> **Tip:** If you notice the AI frequently saying "I don't have that information," add a document that covers that topic.

---

## Leads

> **Path:** Dashboard → Leads

Shows all contacts who filled out the lead capture form during a chat session.

### Lead statuses

| Status | Meaning |
|---|---|
| **New** | Just captured — not yet contacted |
| **Contacted** | You've reached out to them |
| **Qualified** | They're a genuine prospect |
| **Closed** | Deal done or lead no longer relevant |

To update a status, click the dropdown in the Status column. The change saves immediately.

### Exporting leads

At present, leads are viewed in the dashboard only. To export, you can:
- Ask your developer to add a CSV export endpoint
- Use the Supabase dashboard → **Table Editor** → leads table → **Export CSV**
- Access the API directly: `GET /api/v1/leads/` with your auth token

---

## Analytics

> **Path:** Dashboard → Analytics

Shows the same four summary stats as the overview, plus a **14-day message volume bar chart**.

Hover over any bar to see the date and message count for that day.

Use this to:
- See whether activity spikes after marketing campaigns
- Report usage to stakeholders
- Monitor if the chatbot is being actively used

---

## Settings

> **Path:** Dashboard → Settings

### Widget embed code

Three fields control the widget appearance:
- **Company name** — shown in the widget header
- **Brand color** — the button and user bubble color
- **Greeting message** — the first message the bot shows

Adjust these, then copy the generated code snippet and paste it into your website before `</body>`.

### WhatsApp integration

Copy the webhook URL from the Settings page and configure it in your Meta App dashboard (Webhooks tab). See the step-by-step instructions on the Settings page. Replies are sent back to users via the Meta Graph API — no Twilio account required.

---

## Tips for Getting the Best AI Performance

1. **Upload structured content** — FAQs, service lists, and numbered guides work better than long narrative prose.
2. **Keep documents updated** — Old pricing or policy in a document will cause the AI to give outdated answers.
3. **Be specific in documents** — The more specific the content, the more specific the AI's answers.
4. **Test after every upload** — Ask 3–5 questions you expect customers to ask. Check the answers.
5. **Use the Conversations log** — It's your best source of insight into what's working and what isn't.
