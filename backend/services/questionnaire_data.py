"""
questionnaire_data.py
=====================
SINGLE SOURCE OF TRUTH for the privacy questionnaire.

Every question carries everything the rest of the framework needs:
  * how it is asked (text, answer options),
  * which answer is the RISKY one (so we can turn answers into risk values),
  * how important it is (weight inside its category),
  * what finding + recommendation it produces when the answer is risky.

PRIVACY NOTE: questions only ask "is X publicly visible?" (YES/NO...).
The app NEVER asks for the actual phone number, e-mail, address, etc.
"""

YN_OPTIONS = ["YES", "NO", "SOMETIMES", "NOT_SURE"]
VIS_OPTIONS = ["PUBLIC", "FRIENDS", "PRIVATE", "NOT_SURE"]

OPTION_LABELS = {
    "YES": "Yes", "NO": "No", "SOMETIMES": "Sometimes", "NOT_SURE": "Not sure",
    "PUBLIC": "Public (anyone)", "FRIENDS": "Friends / connections only",
    "PRIVATE": "Private (only me)",
}

# Ten risk categories. 'weight' values are EDUCATIONAL ASSUMPTIONS (sum = 1.0).
CATEGORIES = [
    {"key": "profile", "letter": "A", "label": "Profile Visibility",
     "score_name": "Profile Exposure Score", "weight": 0.10,
     "description": "How easily strangers can see and find your profile."},
    {"key": "personal_info", "letter": "B", "label": "Personal Information",
     "score_name": "Personal Information Score", "weight": 0.15,
     "description": "Which personal details are visible (we only ask YES/NO, never the details)."},
    {"key": "location", "letter": "C", "label": "Location Privacy",
     "score_name": "Location Exposure Score", "weight": 0.15,
     "description": "Real-time location, geotags, check-ins and travel posts."},
    {"key": "content", "letter": "D", "label": "Posts & Content",
     "score_name": "Content Exposure Score", "weight": 0.10,
     "description": "Who sees your posts and what your photos may reveal."},
    {"key": "connections", "letter": "E", "label": "Friends / Followers",
     "score_name": "Connection Risk Score", "weight": 0.10,
     "description": "Who can connect with you and how you manage connections."},
    {"key": "tagging", "letter": "F", "label": "Tagging & Mentions",
     "score_name": "Tagging Risk Score", "weight": 0.05,
     "description": "How other people's posts can expose you."},
    {"key": "account_security", "letter": "G", "label": "Authentication & Account Security",
     "score_name": "Account Security Score", "weight": 0.15,
     "description": "MFA, passwords, login alerts, sessions and recovery options."},
    {"key": "third_party", "letter": "H", "label": "Third-Party Apps",
     "score_name": "Third-Party App Risk Score", "weight": 0.05,
     "description": "Apps and websites connected to your social account."},
    {"key": "social_engineering", "letter": "I", "label": "Messaging & Social Engineering",
     "score_name": "Social Engineering Score", "weight": 0.10,
     "description": "Habits that scammers and impersonators try to exploit."},
    {"key": "digital_footprint", "letter": "J", "label": "Digital Footprint",
     "score_name": "Digital Footprint Score", "weight": 0.05,
     "description": "Old posts, old accounts and how often you review settings."},
]
CATEGORY_BY_KEY = {c["key"]: c for c in CATEGORIES}

FIELDS = ["id", "category", "kind", "risky", "weight", "feature", "text",
          "finding_type", "severity", "finding", "recommendation", "priority"]

# id, category, kind, risky answer, weight, feature, question text,
# finding_type, severity, finding description, recommendation, priority
_RAW = [
 # ---------------- A: Profile Visibility ----------------
 ("A1","profile","vis","PUBLIC",3,"profile_visibility",
  "How visible is your profile and its basic details? (Public = anyone, Friends = approved connections only, Private = only you / very limited)",
  "PUBLIC_PROFILE","MEDIUM","Profile is reported as publicly visible, which increases the amount of information others can reach.",
  "Move your profile to friends/connections-only where the platform allows it.","IMPORTANT"),
 ("A2","profile","yn","YES",2,"search_engine_indexing",
  "Can search engines show your profile in search results?",
  "SEARCH_INDEXED","MEDIUM","Profile may appear in search-engine results, making it easier to discover.",
  "Turn off search-engine indexing of your profile in the privacy settings.","IMPORTANT"),
 ("A3","profile","vis","PUBLIC",1,"friends_list_visibility",
  "Who can see your friends / followers list?",
  "FRIENDS_LIST_PUBLIC","LOW","Friends/followers list is visible beyond your connections, which reveals your social circle.",
  "Limit friends/followers list visibility to connections only.","GOOD PRACTICE"),
 ("A4","profile","yn","YES",2,"discoverable_by_contact",
  "Can people find your profile by searching for your phone number or e-mail address?",
  "DISCOVERABLE_BY_CONTACT","MEDIUM","Profile can be discovered through contact details, which makes targeted lookup easier.",
  "Restrict 'find me by phone/e-mail' to friends or turn it off.","IMPORTANT"),
 ("A5","profile","yn","YES",1,"real_name_photo_public",
  "Is your full real name together with a clear profile photo visible to everyone?",
  "NAME_PHOTO_PUBLIC","LOW","Full name plus clear photo is public, which makes impersonation and identification easier.",
  "Consider a first name or nickname and a profile photo that does not reveal where you live, study or work.","GOOD PRACTICE"),
 # ---------------- B: Personal Information (YES/NO: 'is it publicly visible?') ----------------
 ("B1","personal_info","yn","YES",3,"phone_public",
  "Is your phone number publicly visible on your profile?",
  "PUBLIC_PHONE","HIGH","Phone number is reported as publicly visible.",
  "Limit phone-number visibility where possible (friends only or hidden).","IMMEDIATE"),
 ("B2","personal_info","yn","YES",2,"email_public",
  "Is your personal e-mail address publicly visible on your profile?",
  "PUBLIC_EMAIL","MEDIUM","Personal e-mail address is reported as publicly visible.",
  "Hide your e-mail address or show it to friends only; consider a separate address for public use.","IMPORTANT"),
 ("B3","personal_info","yn","YES",3,"birthday_public",
  "Is your FULL birth date (day, month and year) publicly visible?",
  "PUBLIC_BIRTHDAY","HIGH","Full birth date is publicly visible; it is often used for identity checks.",
  "Hide the birth year (or the whole date) from the public.","IMPORTANT"),
 ("B4","personal_info","yn","YES",2,"home_info_public",
  "Is information about where you live (street, neighbourhood or detailed hometown) publicly visible?",
  "PUBLIC_HOME_INFO","MEDIUM","Home-related information is publicly visible.",
  "Remove or restrict home address / neighbourhood details on your profile.","IMPORTANT"),
 ("B5","personal_info","yn","YES",2,"workplace_public",
  "Is your workplace or job title publicly visible?",
  "PUBLIC_WORKPLACE","MEDIUM","Workplace details are public, which can add believable context to scams.",
  "Limit workplace visibility, or keep only what you intentionally want public.","IMPORTANT"),
 ("B6","personal_info","yn","YES",1,"education_public",
  "Is your school, college or education history publicly visible?",
  "PUBLIC_EDUCATION","LOW","Education details are publicly visible.",
  "Restrict education details to friends or remove them if not needed.","GOOD PRACTICE"),
 ("B7","personal_info","yn","YES",2,"relationship_public",
  "Are your relationship status or family members publicly visible?",
  "PUBLIC_RELATIONSHIPS","MEDIUM","Relationship/family information is publicly visible.",
  "Hide family and relationship details from the public.","IMPORTANT"),
 # ---------------- C: Location Privacy ----------------
 ("C1","location","yn","YES",3,"live_location_sharing",
  "Do you publicly share your real-time location (live location, 'currently at...' posts)?",
  "REALTIME_LOCATION","HIGH","Real-time location sharing is enabled.",
  "Avoid publicly broadcasting real-time location unless intentionally needed; share with trusted people only.","IMMEDIATE"),
 ("C2","location","yn","YES",2,"location_tagging",
  "Do your public posts and photos include location tags (geotags)?",
  "GEOTAGGED_POSTS","MEDIUM","Public posts carry location tags.",
  "Turn off automatic geotagging for public posts and in your camera app.","IMPORTANT"),
 ("C3","location","yn","YES",2,"public_checkins",
  "Do you publicly check in at places while you are still there?",
  "LIVE_CHECKINS","MEDIUM","Check-ins are posted while still at the location.",
  "Post about places after you have left, or share check-ins with close friends only.","IMPORTANT"),
 ("C4","location","yn","YES",3,"travel_posts",
  "Do you post travel plans or holiday dates publicly before or during a trip?",
  "PUBLIC_TRAVEL_PLANS","HIGH","Travel plans are shared publicly before or during trips.",
  "Share travel photos after returning, and keep trip dates private.","IMPORTANT"),
 ("C5","location","yn","YES",2,"home_work_inferable",
  "Could a stranger work out your home, school or workplace location from your public posts or photos?",
  "INFERABLE_HOME_WORK_LOCATION","MEDIUM","Home/work/school location may be inferable from public content.",
  "Review public photos for landmarks, street signs and repeated places; remove those that reveal routines.","IMPORTANT"),
 # ---------------- D: Posts & Content ----------------
 ("D1","content","vis","PUBLIC",3,"posts_public",
  "Who can see your posts by default?",
  "PUBLIC_POSTS","MEDIUM","Posts are public by default.",
  "Change the default audience of new posts to friends or a smaller list.","IMPORTANT"),
 ("D2","content","yn","YES",3,"sensitive_items_in_photos",
  "Have you posted photos showing ID badges, documents, tickets, vehicle plates or computer screens?",
  "SENSITIVE_ITEMS_IN_PHOTOS","HIGH","Photos may have revealed badges, documents, plates or screens.",
  "Review and delete photos that show IDs, tickets, plates or screens; blur such items before posting.","IMPORTANT"),
 ("D3","content","yn","YES",2,"routine_posts",
  "Do you publicly post about your regular routine (gym times, commute, class or work schedule)?",
  "ROUTINE_EXPOSED","MEDIUM","Regular routines are visible in public posts.",
  "Avoid publicly posting predictable routines; share them with close friends only.","IMPORTANT"),
 ("D4","content","yn","YES",2,"photo_metadata_unchecked",
  "Do you share original photos without checking or removing embedded metadata (EXIF)?",
  "PHOTO_METADATA_UNCHECKED","MEDIUM","Photos may be shared with embedded metadata (such as device or location data).",
  "Learn what EXIF metadata is and strip it from photos before sharing (see tools/metadata_tool.py).","IMPORTANT"),
 # ---------------- E: Friends / Followers ----------------
 ("E1","connections","yn","YES",3,"unknown_connections",
  "Do you accept connection or friend requests from people you do not know?",
  "UNKNOWN_CONNECTIONS_ACCEPTED","HIGH","Connection requests from unknown people are accepted.",
  "Verify unfamiliar profiles before accepting connections (mutual friends, profile age, behaviour).","IMPORTANT"),
 ("E2","connections","vis","PUBLIC",1,"connection_requests_open",
  "Who can send you friend / follow requests? (Public = anyone, Friends = friends of friends, Private = nobody / invitation only)",
  "OPEN_CONNECTION_REQUESTS","LOW","Anyone can send connection requests.",
  "Limit who can send requests (for example, friends of friends).","GOOD PRACTICE"),
 ("E3","connections","yn","NO",1,"connections_reviewed",
  "Do you periodically review and remove connections you no longer know or trust?",
  "CONNECTIONS_NOT_REVIEWED","LOW","Friends/followers are not reviewed regularly.",
  "Review your friends/followers list every few months and remove unknown accounts.","GOOD PRACTICE"),
 # ---------------- F: Tagging & Mentions ----------------
 ("F1","tagging","yn","YES",2,"anyone_can_tag",
  "Can anyone tag you in posts or photos without your approval?",
  "OPEN_TAGGING","MEDIUM","Anyone can tag the account.",
  "Limit who can tag you to friends only.","IMPORTANT"),
 ("F2","tagging","yn","NO",3,"tag_review_enabled",
  "Do you review tags before they appear on your profile (tag review turned on)?",
  "TAG_REVIEW_DISABLED","MEDIUM","Tag review is not enabled.",
  "Enable tag review so you approve posts before they appear on your profile.","IMPORTANT"),
 ("F3","tagging","yn","YES",1,"unknown_mentions",
  "Can people you do not know mention you or message you directly?",
  "OPEN_MENTIONS","LOW","Unknown users can mention or message the account.",
  "Restrict mentions and direct messages to people you follow or know.","GOOD PRACTICE"),
 # ---------------- G: Authentication & Account Security ----------------
 ("G1","account_security","yn","NO",3,"mfa_enabled",
  "Do you use multi-factor authentication (MFA / 2-step verification) on this account?",
  "MFA_DISABLED","HIGH","Multi-factor authentication is not enabled.",
  "Enable multi-factor authentication using the strongest supported method (authenticator app or security key).","IMMEDIATE"),
 ("G2","account_security","yn","YES",3,"password_reuse_reported",
  "Do you use the same (or a very similar) password on more than one account?",
  "PASSWORD_REUSE","HIGH","Password reuse is reported.",
  "Use a unique password for each account; change reused passwords starting with e-mail and social media.","IMMEDIATE"),
 ("G3","account_security","yn","NO",1,"password_manager_used",
  "Do you use a password manager?",
  "NO_PASSWORD_MANAGER","LOW","No password manager is used.",
  "Start using a reputable password manager to create and store unique passwords.","GOOD PRACTICE"),
 ("G4","account_security","yn","NO",2,"login_alerts_enabled",
  "Have you turned on login alerts (notifications about new logins)?",
  "LOGIN_ALERTS_DISABLED","MEDIUM","Login alerts are not enabled.",
  "Enable login alerts where available so you notice unfamiliar sign-ins quickly.","IMPORTANT"),
 ("G5","account_security","yn","NO",1,"sessions_reviewed",
  "Do you review active sessions and logged-in devices?",
  "SESSIONS_NOT_REVIEWED","LOW","Active sessions/devices are not reviewed.",
  "Review active sessions and log out of devices you do not recognise.","GOOD PRACTICE"),
 ("G6","account_security","yn","NO",2,"recovery_info_reviewed",
  "Have you checked your account-recovery options (recovery e-mail / phone) recently?",
  "RECOVERY_INFO_NOT_REVIEWED","MEDIUM","Recovery information has not been reviewed.",
  "Check that recovery e-mail and phone are current and under your control.","IMPORTANT"),
 # ---------------- H: Third-Party Apps ----------------
 ("H1","third_party","yn","NO",3,"third_party_apps_reviewed",
  "Do you review the third-party apps and websites connected to your account?",
  "THIRD_PARTY_APPS_NOT_REVIEWED","MEDIUM","Connected third-party applications have not been reviewed.",
  "Review connected apps and revoke access you no longer need (principle of least privilege).","IMPORTANT"),
 ("H2","third_party","yn","YES",2,"social_login_heavy",
  "Do you use 'Sign in with your social account' on many websites or apps?",
  "MANY_SOCIAL_LOGINS","LOW","Social sign-in is used widely, which creates many app connections.",
  "Prefer separate sign-ins for low-value sites and keep social sign-in for services you trust.","GOOD PRACTICE"),
 ("H3","third_party","yn","YES",2,"unused_apps_connected",
  "Do you have old or unused apps still connected to your account?",
  "UNUSED_APPS_CONNECTED","MEDIUM","Old or unused app integrations remain connected.",
  "Remove unused integrations and apps with unnecessary permissions.","IMPORTANT"),
 # ---------------- I: Messaging & Social Engineering ----------------
 ("I1","social_engineering","yn","NO",3,"suspicious_link_awareness",
  "Do you check unexpected links and messages (sender, URL, tone) before opening or replying?",
  "LOW_LINK_AWARENESS","HIGH","Unexpected links/messages are not reliably checked before use.",
  "Pause on unexpected links; verify the sender through another channel before clicking or replying.","IMPORTANT"),
 ("I2","social_engineering","yn","YES",2,"replies_to_unverified_dms",
  "Do you reply to direct messages from accounts you have not verified?",
  "REPLIES_TO_UNVERIFIED_DMS","MEDIUM","Direct messages from unverified accounts are answered.",
  "Do not engage with unverified accounts; check profile history and report impersonation.","IMPORTANT"),
 ("I3","social_engineering","yn","YES",3,"shared_verification_code",
  "Have you ever shared a login or verification code with another person?",
  "VERIFICATION_CODE_SHARED","HIGH","A verification code has been shared with someone else.",
  "Never share verification codes; no genuine support team will ask for them.","IMMEDIATE"),
 ("I4","social_engineering","yn","YES",2,"giveaway_participation",
  "Do you join giveaways or 'free offer' posts that ask for personal details or a link click?",
  "SUSPICIOUS_GIVEAWAYS","MEDIUM","Participation in giveaway/offer posts that request details or clicks.",
  "Treat giveaways asking for personal details or payments as suspicious and avoid them.","IMPORTANT"),
 # ---------------- J: Digital Footprint ----------------
 ("J1","digital_footprint","yn","NO",3,"old_posts_reviewed",
  "Do you regularly review (and clean up) your old public posts?",
  "OLD_POSTS_NOT_REVIEWED","MEDIUM","Historical public posts have not been reviewed.",
  "Review old public posts and remove or restrict those that reveal personal details.","IMPORTANT"),
 ("J2","digital_footprint","yn","YES",2,"unused_accounts_open",
  "Do you have old or unused social-media accounts that are still active or public?",
  "UNUSED_ACCOUNTS_ACTIVE","MEDIUM","Old or unused accounts are still active.",
  "Delete or lock down accounts you no longer use.","IMPORTANT"),
 ("J3","digital_footprint","yn","YES",2,"public_comments_personal",
  "Have you left public comments that reveal personal details (school, workplace, plans, family)?",
  "PERSONAL_PUBLIC_COMMENTS","MEDIUM","Public comments may reveal personal details.",
  "Review public comments and remove those that reveal personal details.","IMPORTANT"),
 ("J4","digital_footprint","yn","NO",2,"privacy_settings_reviewed",
  "Do you review your privacy settings regularly (at least a few times a year)?",
  "SETTINGS_NOT_REVIEWED","MEDIUM","Privacy settings are not reviewed periodically.",
  "Schedule a privacy-settings review every 3-6 months; platforms change defaults.","IMPORTANT"),
]

QUESTIONS = [dict(zip(FIELDS, row)) for row in _RAW]
QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS}
FEATURE_TO_QID = {q["feature"]: q["id"] for q in QUESTIONS}
SEVERITY_RANK = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
PRIORITY_RANK = {"IMMEDIATE": 3, "IMPORTANT": 2, "GOOD PRACTICE": 1}

# Risk value (0..1) used for answers that are neither the risky nor the safe extreme.
SOMETIMES_RISK = 0.5
NOT_SURE_RISK = 0.6        # "I don't know" is treated as slightly risky (unknown exposure)
FRIENDS_RISK = 0.4
FINDING_THRESHOLD = 0.5    # risk >= 0.5 creates a finding


def options_for(q):
    return VIS_OPTIONS if q["kind"] == "vis" else YN_OPTIONS


def risk_for_answer(q, answer):
    """Convert one answer into a risk value between 0 (safest) and 1 (riskiest)."""
    if answer == "NOT_SURE":
        return NOT_SURE_RISK
    if q["kind"] == "vis":
        return {"PUBLIC": 1.0, "FRIENDS": FRIENDS_RISK, "PRIVATE": 0.0}[answer]
    if answer == "SOMETIMES":
        return SOMETIMES_RISK
    return 1.0 if answer == q["risky"] else 0.0


def safest_answer(q):
    if q["kind"] == "vis":
        return "PRIVATE"
    return "NO" if q["risky"] == "YES" else "YES"


def riskiest_answer(q):
    return "PUBLIC" if q["kind"] == "vis" else q["risky"]


def is_protective(q):
    """A 'control' question: answering YES is the good behaviour (MFA, alerts...)."""
    return q["kind"] == "yn" and q["risky"] == "NO"


def public_questionnaire():
    """Safe-to-send version of the questionnaire for the frontend (no scoring logic)."""
    return {
        "categories": [{k: c[k] for k in ("key", "letter", "label", "description")} for c in CATEGORIES],
        "questions": [
            {"id": q["id"], "category": q["category"], "text": q["text"], "kind": q["kind"],
             "options": [{"value": o, "label": OPTION_LABELS[o]} for o in options_for(q)]}
            for q in QUESTIONS
        ],
    }
