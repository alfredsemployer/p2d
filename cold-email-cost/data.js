/*
 * Cold-email tooling cost dataset.
 * The unique-data asset behind the calculator. Kept current on a schedule.
 *
 * Pricing schema per tool:
 *   id            slug
 *   name          display name
 *   homepage      canonical URL (used if no affiliate link set)
 *   affiliate     { url, recurringPct, cookieDays } | null  -> when set, links use affiliate.url
 *   warmupIncluded  bool   (free deliverability warmup bundled in every plan)
 *   leadDatabase    bool   (built-in B2B lead/email database)
 *   plans[]       { name, monthly, annualMonthly, sends (per-month cap, null=unlimited),
 *                   prospects (active-contact cap, null=unlimited),
 *                   maxMailboxes (sending accounts allowed, null=unlimited) }
 *   notes         short caveat string
 *
 * Infrastructure (domains + mailboxes) is modelled separately and applied equally
 * to every platform, because you must buy it regardless of which sender you pick.
 */
window.CEC_DATA = {
  lastUpdated: "2026-06-06",

  // Defaults for the cost model. All user-adjustable in the UI.
  defaults: {
    emailsPerMailboxPerDay: 30,   // conservative safe-sending rate
    sendingDaysPerMonth: 22,      // business days
    mailboxesPerDomain: 3,        // typical safe ratio
    mailboxMonthly: 3.0,          // per-mailbox/mo via a reseller (Google Workspace ~$7; resellers ~$1.5-3)
    domainAnnual: 12              // per-domain/yr
  },

  tools: [
    {
      id: "smartlead",
      name: "Smartlead",
      homepage: "https://www.smartlead.ai/",
      affiliate: null, // 35% recurring, 90-day cookie -> https://www.smartlead.ai/affiliate-partners
      warmupIncluded: true,
      leadDatabase: false,
      plans: [
        { name: "Basic",          monthly: 39,  annualMonthly: 32.5,  sends: 6000,   prospects: 2000,   maxMailboxes: null },
        { name: "Pro",            monthly: 94,  annualMonthly: 78.3,  sends: 90000,  prospects: 30000,  maxMailboxes: null },
        { name: "Unlimited Smart",monthly: 174, annualMonthly: 144.5, sends: 150000, prospects: null,   maxMailboxes: null },
        { name: "Unlimited Prime",monthly: 379, annualMonthly: 314.6, sends: 500000, prospects: null,   maxMailboxes: null }
      ],
      notes: "Unlimited mailboxes on every plan; warmup pool included. Sells managed mailboxes (SmartSenders) at $4.50/mo + $13/domain/yr if you don't bring your own."
    },
    {
      id: "instantly",
      name: "Instantly",
      homepage: "https://instantly.ai/",
      affiliate: null, // up to 40% recurring -> https://instantly.ai/affiliate
      warmupIncluded: true,
      leadDatabase: true,
      plans: [
        { name: "Growth",      monthly: 47,  annualMonthly: 47,  sends: 5000,   prospects: 1000,   maxMailboxes: null },
        { name: "Hypergrowth", monthly: 97,  annualMonthly: 97,  sends: 100000, prospects: 25000,  maxMailboxes: null },
        { name: "Light Speed", monthly: 358, annualMonthly: 358, sends: 500000, prospects: 100000, maxMailboxes: null }
      ],
      notes: "Unlimited email accounts + unlimited warmup on every plan. 450M+ lead database sold as a separate credits plan (from $47/mo)."
    },
    {
      id: "lemlist",
      name: "lemlist",
      homepage: "https://www.lemlist.com/",
      affiliate: null,
      warmupIncluded: true,
      leadDatabase: true,
      plans: [
        { name: "Email",        monthly: 39,  annualMonthly: 31, sends: 5000, prospects: null, maxMailboxes: null },
        { name: "Multichannel", monthly: 109, annualMonthly: 87, sends: null, prospects: null, maxMailboxes: 5 }
      ],
      notes: "Email plan caps at 5,000 sends/mo. Multichannel adds LinkedIn/SMS/calls but limits to 5 senders per user. 650M+ lead database; enrichment is pay-per-credit."
    },
    {
      id: "quickmail",
      name: "QuickMail",
      homepage: "https://quickmail.com/",
      affiliate: null,
      warmupIncluded: true,
      leadDatabase: false,
      plans: [
        { name: "Starter", monthly: 49,  annualMonthly: 49,  sends: 5000,   prospects: 1000,   maxMailboxes: null },
        { name: "Growth",  monthly: 99,  annualMonthly: 99,  sends: 100000, prospects: 25000,  maxMailboxes: null },
        { name: "Agency",  monthly: 299, annualMonthly: 299, sends: 500000, prospects: 100000, maxMailboxes: null }
      ],
      notes: "Unlimited senders; free AutoWarmer (MailFlow) included. Bring your own mailboxes. Extra agency workspaces $49 each."
    },
    {
      id: "saleshandy",
      name: "Saleshandy",
      homepage: "https://www.saleshandy.com/",
      affiliate: null,
      warmupIncluded: true,
      leadDatabase: true,
      plans: [
        { name: "Outreach Starter",    monthly: 25,  annualMonthly: 25,  sends: 6000,   prospects: 2000,   maxMailboxes: null },
        { name: "Outreach Pro",        monthly: 69,  annualMonthly: 69,  sends: 150000, prospects: 30000,  maxMailboxes: null },
        { name: "Outreach Scale",      monthly: 139, annualMonthly: 139, sends: 240000, prospects: 60000,  maxMailboxes: null },
        { name: "Outreach Scale Plus", monthly: 209, annualMonthly: 209, sends: 300000, prospects: 100000, maxMailboxes: null }
      ],
      notes: "Cheapest entry point; unlimited email accounts. Sells managed mailboxes at $2.99-$3.99/mo. Verification $19 per 5,000."
    },
    {
      id: "mailshake",
      name: "Mailshake",
      homepage: "https://mailshake.com/",
      affiliate: null,
      warmupIncluded: true,
      leadDatabase: false,
      plans: [
        { name: "Starter",          monthly: 29, annualMonthly: 25, sends: 1500, prospects: null, maxMailboxes: 1 },
        { name: "Email Outreach",   monthly: 49, annualMonthly: 45, sends: null, prospects: null, maxMailboxes: 2 },
        { name: "Sales Engagement", monthly: 99, annualMonthly: 85, sends: null, prospects: null, maxMailboxes: 10 }
      ],
      notes: "Priced per sending account: 1 / 2 / 10 accounts by plan (Agency = unlimited, custom). Scales poorly for high-volume multi-mailbox setups."
    }
  ]
};
