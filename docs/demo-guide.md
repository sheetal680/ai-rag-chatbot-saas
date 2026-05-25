# Demo Guide — How to Pitch the AI Chatbot to Clients

A practical walkthrough for demonstrating the platform to potential clients.

---

## Before the Demo

### Set up the demo environment

1. Run the seed script to populate demo data:
   ```bash
   cd backend
   python ../scripts/seed_demo.py
   ```
   This creates:
   - A "Luminary Homes" knowledge base (property agency FAQ)
   - A sample lead record
   - An admin account: `demo@luminaryhomes.com` / `Demo1234!`

2. Open the chat widget demo:
   ```
   https://your-app.vercel.app/embed/chat?clientId=luminary-homes&companyName=Luminary%20Homes&primaryColor=%2310b981&greeting=Hi!%20How%20can%20I%20help%20with%20your%20property%20search%3F
   ```
   Or open `/chat/new` for the full chat UI.

3. Open the dashboard in a second browser tab:
   ```
   https://your-app.vercel.app/login
   ```
   Log in with `demo@luminaryhomes.com` / `Demo1234!`

---

## Demo Script (30 minutes)

### Part 1 — The Problem (5 min)

Start with the client's pain, not your product.

> "How many times a day does your team answer the same questions — opening hours, pricing, how to book a viewing? What happens when a customer asks at 11pm on a Sunday? They go to your competitor."

Ask:
- How many customer enquiries do they get per week?
- What's the average response time?
- What percentage are the same 5–10 questions?

### Part 2 — The Demo (15 min)

**Show the widget first.** Open the embed chat page.

> "This is exactly what your customers would see. It's embedded on your website. Floating button, branded with your colours. Let me show you what it can do."

Ask it these questions live:
1. *"What 2-bedroom apartments do you have available?"*
2. *"How do I book a viewing?"*
3. *"Do you allow pets?"*
4. *"What happens with the deposit if I decide not to proceed?"*

Watch it answer from the FAQ. Point out:
- Speed (typically 2–3 seconds)
- Accuracy (only answers from the document — no hallucinations)
- Tone (professional, helpful, on-brand)

**Then show the lead capture.** Send 3 messages, then note the lead form appears automatically.

> "Anyone who interacts gets captured. You know who was on your website, what they asked, and how to follow up."

**Then show the dashboard.** Switch to the admin tab.

- Conversations page: show the real-time log of what was just asked
- Leads page: show the captured lead
- Documents page: show the FAQ that powers everything
- Settings page: show the embed code

> "This is your control panel. You can update the knowledge base in 30 seconds, see every conversation, and track every lead."

### Part 3 — Customisation Walk-through (5 min)

Open Settings → change the company name and colour. Show the embed code updating.

> "When I build yours, I'll brand it to your exact colours and wording. Takes about 10 minutes."

### Part 4 — Close (5 min)

> "Getting this live on your website takes about 3–5 days once I have your content. You give me your FAQs, pricing, whatever you want it to know — I handle the rest. After that, your website answers questions 24/7 without you lifting a finger."

**Address common objections:**

**"What if it says something wrong?"**
> "It only answers from the documents you give it. It won't invent prices or make promises. If you update the documents, it updates immediately."

**"We already have a chatbot."**
> "Most chatbots are just decision trees — you have to click through menus. This understands natural language. Ask it anything and it figures out the answer."

**"We're not a tech company."**
> "You don't need to be. The dashboard is built for non-technical users. If you can update a Google Doc, you can manage this."

---

## Businesses to Target First

These business types have high FAQ volume and low technical complexity:

| Sector | Common questions they get |
|---|---|
| Property / lettings | Availability, pricing, booking, deposits |
| Beauty / wellness | Services, pricing, booking, cancellation |
| Restaurants / venues | Menu, opening hours, private hire, bookings |
| Legal / accountancy | Service scope, fees, initial consultation |
| Gyms / fitness | Membership pricing, class schedule, facilities |
| E-commerce | Shipping, returns, size guides, product info |

---

## Loom Walkthrough Structure

Record a 5-minute screen recording for async pitching:

1. **00:00** — Show the widget on a demo website (screen share Luminary Homes demo)
2. **01:00** — Ask 3 live questions, show answers
3. **02:00** — Show lead capture triggering
4. **02:30** — Switch to dashboard — conversations, leads, documents
5. **03:30** — Show the Settings embed code
6. **04:00** — Explain the offer and CTA

Upload to Loom and share the link in outreach DMs/emails.

---

## Outreach Template

> **Subject:** Your website could answer customer questions 24/7

> Hi [Name],
>
> I built an AI chatbot tool for local businesses that answers customer questions automatically — using your own content (FAQs, pricing, service info).
>
> Here's a 5-minute demo using a property agency as an example: [Loom link]
>
> I can have something like this live on your website within a week. Happy to show you a version branded to [their business] on a quick call?
>
> [Your name]

---

## Pricing Positioning

Anchor against the cost of the alternative:

- 1 hour of customer service time = £15–25
- 50 FAQ questions/day × 5 min each = 4 hours/day = £60–100/day
- Monthly cost: £1,200–£2,000 in staff time
- **Your price: £800 setup + £50/month hosting**

Frame it as replacing 95% of repetitive enquiries, not replacing the team.
