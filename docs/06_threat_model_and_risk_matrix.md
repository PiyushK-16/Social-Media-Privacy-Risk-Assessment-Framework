# Threat Model & Privacy Risk Matrix (Sections 35-36)

Scope: a **fictional** social-media user. Defensive analysis only.

## Threat model
| Asset | Threat | Exposure | Potential impact | Existing control | Recommended control |
|---|---|---|---|---|---|
| Account | Account takeover | No MFA, reused password, no login alerts | Loss of account, impersonation of contacts | Password | MFA (app/key), unique passwords + manager, login alerts, review sessions |
| Identity information | Impersonation | Public full name, photo, birth date | Fake profiles, scams against friends | Profile name | Hide birth date, limit photo/name exposure, report fake accounts |
| Contact information | Phishing / unwanted contact | Public phone/e-mail, discoverable by contact | Targeted scam calls/messages | None | Hide contact details, restrict lookup by phone/e-mail |
| Location privacy | Physical-world profiling/stalking risk | Live location, geotags, travel posts, routines | Safety risk, burglary risk when away | Audience setting | Post after leaving, disable geotags, friends-only audience |
| Private content | Oversharing / content leakage | Public posts, old posts, photos with metadata | Long-term exposure of personal details | Audience setting | Default to friends, clean old posts, strip EXIF |
| Social relationships | Social engineering via contacts | Unknown connections, public friend list | Trust abuse, scam spreading | Friend requests | Verify requests, hide friends list, periodic review |
| Third-party app data | Excess app access | Unreviewed/unused connected apps | Data exposure via app, token misuse | Platform consent screens | Review and revoke apps (least privilege) |
| Unwanted profiling | Aggregation of public data | Workplace + education + family + interests public | More convincing pretexts | None | Limit public context, reduce footprint |

## Privacy risk matrix (educational estimates)
| Exposure | Likelihood | Impact |
|---|---|---|
| Public phone number | MEDIUM | MEDIUM |
| Full birth date public | MEDIUM | MEDIUM |
| Real-time location exposure | MEDIUM | HIGH |
| Travel plans public | MEDIUM | HIGH |
| MFA disabled | MEDIUM | HIGH |
| Password reuse | MEDIUM | HIGH |
| Unknown connections accepted | HIGH | MEDIUM |
| Tag review disabled | MEDIUM | LOW |
| Unreviewed third-party apps | MEDIUM | MEDIUM |
| Old posts unreviewed | MEDIUM | LOW |

**Actual risk depends on context** (who the user is, who might target them, platform behaviour). Ratings are teaching assumptions, not measured probabilities.
