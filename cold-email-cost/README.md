# Cold Email Cost Calculator

Static, self-contained tool. The true all-in monthly cost of cold-email tooling
(software + mailboxes + domains) across the leading platforms.

## Files
- `index.html` — the app (vanilla JS, no build step, no dependencies).
- `data.js` — the pricing dataset (`window.CEC_DATA`). This is the unique-data asset.

## Status
STAGING on p2d.space/cold-email-cost/ (noindex). Intended home: a dedicated domain.

## Money
Recurring SaaS affiliate. Each tool in `data.js` has an `affiliate` field
(`{url, recurringPct, cookieDays}`). When `affiliate.url` is set, the tool's "View"
button uses it; otherwise it falls back to `homepage`. Confirmed programs:
- Smartlead — up to 35% recurring, 90-day cookie (smartlead.ai/affiliate-partners)
- Instantly — up to 40% recurring (instantly.ai/affiliate)

## Freshness moat
Vendors change pricing constantly. `data.js` has a per-dataset `lastUpdated`.
A scheduled job should re-fetch each vendor's pricing page, diff against the dataset,
and update. Freshness is the defensible edge over static blog comparisons.

## Cost model (see methodology section in index.html)
mailboxes = ceil((monthlyVolume / sendingDays) / emailsPerMailboxPerDay)
domains   = ceil(mailboxes / mailboxesPerDomain)
infra/mo  = mailboxes * mailboxMonthly + domains * (domainAnnual/12)
For each tool: cheapest plan where sends, prospects, and maxMailboxes all fit; + infra.
