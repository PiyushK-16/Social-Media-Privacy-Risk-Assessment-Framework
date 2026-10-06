"""checklist.py - the printable Social Media Privacy Checklist."""
CHECKLIST = [
    "Review profile visibility", "Hide unnecessary contact information", "Review birth-date visibility",
    "Review location sharing", "Avoid unnecessary real-time location posts", "Review tagging permissions",
    "Review followers/friends", "Verify unfamiliar requests", "Enable MFA",
    "Enable login alerts where available", "Review active sessions", "Review connected apps",
    "Remove unused integrations", "Review old public posts", "Review photo privacy",
    "Be cautious with unexpected links", "Never share verification codes", "Review privacy settings periodically",
]


def checklist_text():
    lines = ["SOCIAL MEDIA PRIVACY CHECKLIST", "=" * 30, ""] + [f"[ ] {item}" for item in CHECKLIST]
    lines += ["", "Educational checklist - review your settings every 3-6 months."]
    return "\n".join(lines) + "\n"
