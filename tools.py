import json
import os
from datetime import datetime

TICKETS_FILE = "tickets.json"
MAX_TICKETS_PER_SESSION = 3  # Rate limit

def load_tickets():
    if not os.path.exists(TICKETS_FILE):
        return []
    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_ticket(ticket_data):
    tickets = load_tickets()
    tickets.append(ticket_data)
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=4, ensure_ascii=False)

def create_ticket(title: str, description: str, priority: str = "Medium") -> str:
    """
    Creates a support ticket after validating priority and checking rate limits.
    """
    # 1. Validate priority
    valid_priorities = ["Low", "Medium", "High", "Urgent"]
    if priority not in valid_priorities:
        priority = "Medium"  # Default fallback

    # 2. Check rate limit
    tickets = load_tickets()
    if len(tickets) >= MAX_TICKETS_PER_SESSION:
        return "Error: Rate limit reached. You can only create up to 3 tickets per session."

    # 3. Create ticket record
    ticket_id = f"TICKET-{len(tickets) + 1:03d}"
    ticket_data = {
        "ticket_id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "Open",
        "created_at": datetime.utcnow().isoformat()
    }

    # 4. Save to storage
    save_ticket(ticket_data)
    return f"Success! Ticket {ticket_id} has been created with priority '{priority}'."