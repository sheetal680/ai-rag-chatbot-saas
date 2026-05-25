"""
Seed the database with a polished demo client — "Luminary Homes" (property agency).

Usage:
  cd backend
  python ../scripts/seed_demo.py

Requires:
  - A running backend with .env configured (DATABASE_URL, GROQ_API_KEY, etc.)
  - The Supabase tables already created (run schema.sql in the SQL Editor first,
    or let the app's startup create them via ensure_tables()).

What it creates:
  - An admin account: demo@luminaryhomes.com / Demo1234!
  - The Luminary Homes FAQ as an ingested text document
  - A sample lead record
"""

import asyncio
import os
import sys

# ── Add the backend package to the path ──────────────────────────────────────
SCRIPT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.join(SCRIPT_DIR, "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

# ── Demo content ──────────────────────────────────────────────────────────────

DEMO_EMAIL    = "demo@luminaryhomes.com"
DEMO_PASSWORD = "Demo1234!"
DEMO_NAME     = "Luminary Demo"
CLIENT_ID     = "luminary-homes"

FAQ_TEXT = """
Luminary Homes — Frequently Asked Questions

About Luminary Homes
Luminary Homes is a boutique property rental agency based in Manchester, UK. We specialise
in residential lettings across the city centre, Ancoats, Didsbury, and Chorlton.

Available Properties
We currently manage over 120 rental properties. Our portfolio includes:
- Studio apartments from £750/month
- One-bedroom apartments from £950/month
- Two-bedroom apartments from £1,200/month
- Three-bedroom houses from £1,650/month

All properties are fully managed — we handle maintenance, tenant queries, and compliance.

Booking a Viewing
To arrange a viewing, you can:
1. Click "Book a viewing" on any property listing on our website
2. Call us on 0161 400 5500 (Mon–Sat, 9am–6pm)
3. Email us at lettings@luminaryhomes.co.uk

Viewings are available 7 days a week, including evenings by appointment.

Tenancy Requirements
To rent with Luminary Homes you will need:
- A valid government-issued photo ID (passport or driving licence)
- Proof of income (3 months' payslips or employer letter)
- A UK-based reference from a previous landlord or employer
- One month's deposit (held in a government-approved deposit scheme)

We carry out credit checks via Experian for all applicants.

Deposits and Fees
We charge a holding deposit of one week's rent to secure a property during referencing.
This is refunded if the landlord withdraws or deducted from your first month's rent on move-in.
We do not charge admin fees or referencing fees to tenants.

Pet Policy
Pets are permitted in some of our properties. Please mention this when booking a viewing
and we will confirm which listings are pet-friendly.

Maintenance and Repairs
All managed properties include a 24/7 maintenance reporting service via our online portal.
Emergency repairs (heating, plumbing, security) are responded to within 4 hours.
Routine repairs are completed within 3–5 working days.

Contact Information
Address: 14 Spinningfields, Manchester, M3 3EB
Phone: 0161 400 5500
Email: hello@luminaryhomes.co.uk
Website: www.luminaryhomes.co.uk
Opening hours: Mon–Fri 9am–6pm, Sat 10am–4pm
""".strip()


# ── Seed functions ────────────────────────────────────────────────────────────

async def seed() -> None:
    # Late imports so the path is set up first
    from app.core.config import settings  # noqa: F401 — triggers .env load
    from app.db.postgres import connect_db, ensure_tables, get_pool
    from app.services.auth_service import register_user
    from app.models.user import UserCreate
    from app.rag.pipeline import ingest_document
    from app.utils.id_generator import new_id
    from datetime import UTC, datetime

    print("Connecting to PostgreSQL (Supabase)…")
    await connect_db()
    await ensure_tables()
    pool = get_pool()

    # ── 1. Create admin user ─────────────────────────────────────────────
    print(f"Creating demo user: {DEMO_EMAIL}")
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", DEMO_EMAIL)
    if existing:
        print("  ✓ User already exists — skipping")
    else:
        try:
            await register_user(
                UserCreate(name=DEMO_NAME, email=DEMO_EMAIL, password=DEMO_PASSWORD)
            )
            print("  ✓ Created")
        except Exception as e:
            print(f"  ✗ Failed: {e}")

    # ── 2. Ingest FAQ document ───────────────────────────────────────────
    print("Ingesting Luminary Homes FAQ…")
    doc_id = f"luminary_faq_{new_id()[:8]}"
    chunk_count = 0
    try:
        chunk_count = await ingest_document(
            text=FAQ_TEXT,
            doc_id=doc_id,
            client_id=CLIENT_ID,
            metadata={"filename": "luminary_homes_faq.txt", "type": "text"},
        )
        print(f"  ✓ Indexed {chunk_count} chunks (doc_id: {doc_id})")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # Record the document in PostgreSQL so it shows in the dashboard
    now = datetime.now(UTC)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO documents (id, client_id, filename, type, chunk_count, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (id) DO NOTHING
            """,
            doc_id, CLIENT_ID, "luminary_homes_faq.txt", "text", chunk_count, now,
        )

    # ── 3. Create a sample lead ──────────────────────────────────────────
    print("Creating sample lead…")
    demo_session_id = f"demo_session_{new_id()[:8]}"
    async with pool.acquire() as conn:
        existing_lead = await conn.fetchrow(
            "SELECT id FROM leads WHERE email = $1 AND client_id = $2",
            "sarah.chen@example.com", CLIENT_ID,
        )
        if existing_lead:
            print("  ✓ Lead already exists — skipping")
        else:
            await conn.execute(
                """
                INSERT INTO leads
                    (id, client_id, name, email, phone, session_id, status, source, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, 'new', 'web_widget', $7)
                """,
                new_id(), CLIENT_ID, "Sarah Chen", "sarah.chen@example.com",
                "+44 7911 123456", demo_session_id, now,
            )
            print("  ✓ Sample lead created")

    print("\n✅  Demo data seeded successfully!")
    print(f"\nLogin credentials:\n  Email:    {DEMO_EMAIL}\n  Password: {DEMO_PASSWORD}")
    print(f"\nClient ID: {CLIENT_ID}")
    print("The FAQ is now in the knowledge base. Try asking:")
    print("  - 'What 2-bed apartments do you have?'")
    print("  - 'How do I book a viewing?'")
    print("  - 'What are your maintenance response times?'")


if __name__ == "__main__":
    asyncio.run(seed())
