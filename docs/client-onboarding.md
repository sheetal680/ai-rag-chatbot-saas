# Client Onboarding Guide

Step-by-step checklist for handing off the AI chatbot to a new client.

---

## Pre-Delivery Checklist

Before the handoff call, complete these steps yourself:

- [ ] Backend deployed on Railway (or Render) with all env vars set
- [ ] Frontend deployed on Vercel and connected to the backend
- [ ] CORS configured: `ALLOWED_ORIGINS` includes the Vercel URL
- [ ] Supabase project active — `GET /health/ready` confirms DB is reachable
- [ ] `GET /health/ready` returns `{"status": "ok", "db": "ok"}`
- [ ] Admin account created for the client via `/signup`
- [ ] Initial knowledge base uploaded (at least one PDF or FAQ page)
- [ ] Test chat: ask 3–5 questions that should be answerable from the docs
- [ ] Widget embed code generated in Settings with the client's branding
- [ ] WhatsApp webhook configured (if client has requested it)

---

## Information to Collect from the Client

| Item | Example |
|---|---|
| Company name | Luminary Homes |
| Brand colour (hex) | `#10b981` |
| Greeting message | "Hi! How can I help you with your property search?" |
| Initial documents | Company FAQ PDF, pricing sheet, service list |
| WhatsApp number | `whatsapp:+447911123456` (if needed) |
| Website domain for CORS | `https://luminaryhomes.co.uk` |
| Preferred admin email | owner@luminaryhomes.co.uk |

---

## Handoff Session Agenda (60 min)

### 1. Dashboard tour (15 min)

Walk the client through:
- Overview stats
- Documents page — upload and delete
- Conversations — how to read chat logs
- Leads — status management (New → Contacted → Qualified → Closed)
- Analytics — 14-day volume chart
- Settings — embed code and WhatsApp webhook

### 2. Upload their first documents (15 min)

- Upload the PDF(s) they provided during pre-delivery
- Demonstrate the URL ingest with one of their web pages
- Show the chunk count confirmation

### 3. Live widget demo (10 min)

- Open the embed page at `/embed/chat?clientId=...&companyName=...`
- Ask 3 questions live — show the AI answering from their documents
- Demonstrate the lead capture form appearing

### 4. Embed code walkthrough (10 min)

- Show the Settings page embed snippet
- Walk through what each `ChatbotConfig` field does
- Explain: paste before `</body>`, publish, done
- If they use WordPress: offer the plugin helper at `scripts/wordpress-snippet.txt` (or paste into footer script)

### 5. Q&A and next steps (10 min)

Common client questions and answers:

**Q: Will it answer questions about things not in the documents?**
> No — it's designed to only answer from your uploaded content. If asked something it doesn't know, it politely says so and directs the user to contact support.

**Q: How do I add new content later?**
> Log into the dashboard → Documents → upload the new file or paste a URL. The AI is ready in seconds.

**Q: What if it gives a wrong answer?**
> Check the document it was trained on first. If the document says something outdated, update it or delete and re-upload. The AI is only as good as the content you give it.

**Q: Can I change the colour/greeting later?**
> Yes — update `ChatbotConfig` in the embed code on your website. No backend changes needed.

---

## Post-Handoff Support

For the first 30 days, offer:
- Email support for dashboard questions
- One free document update/upload session
- WhatsApp setup assistance if not done at handoff

After 30 days: include a support retainer in the project price, or direct the client to this documentation.

---

## Pricing Your Service

Suggested project structure:

| Package | Deliverables | Price guide |
|---|---|---|
| **Starter** | Setup + 1 document set + 1 widget | £500–£800 |
| **Business** | Setup + 3 document sets + widget + WhatsApp | £1,200–£2,000 |
| **Agency** | White-label + custom branding + 6 months support | £3,000+ |

Ongoing hosting costs are ~£5–55/month (see `docs/deployment.md`). Pass these through at cost or include in a monthly retainer.
