/* seed dataset — illustrative, with sourced estimates where possible.
   numbers labeled [est.] are triangulated, not published. methodology at the bottom. */

window.GRAPH = {

  // ─── headline KPIs (top of page) ───
  kpis: [
    {
      value: "$375B",
      label: "announced AI capex, FY25",
      caption: "top 4 US hyperscalers combined",
      footnote: "AWS + Azure + Google + Meta capex guidance, mostly AI infrastructure."
    },
    {
      value: "60 GW",
      label: "new US AI power demand by 2030",
      caption: "≈ 65% of current US nuclear fleet (95 GW)",
      footnote: "[est.] Range across DOE, S&P, Bain forecasts: 50–100 GW."
    },
    {
      value: "~$5",
      label: "fully-loaded cost per 1M Sonnet tokens",
      caption: "vs. $15 API revenue → ~65% gross margin",
      footnote: "[est.] Hardware + power + DC overhead, excluding R&D / labor."
    },
    {
      value: "3",
      label: "firms control >90% of leading-edge fab",
      caption: "ASML (EUV), TSMC (3nm/2nm), Samsung (3rd, distant)",
      footnote: "By revenue share at ≤5nm logic nodes."
    }
  ],

  // ─── the receipt: 1M tokens, every flow accounted ───
  receipt: {
    title: "1 MILLION TOKENS",
    subtitle: "Claude Sonnet 4.6 output · single-user share · mid-2026",
    sections: [
      {
        heading: "Revenue & cost",
        rows: [
          { k: "API revenue",           v: "$15.00",     unit: "USD",   note: "Anthropic posted output price." },
          { k: "Fully-loaded cost",     v: "~$5",        unit: "USD",   note: "[est.] hardware + power + DC.", emph: false },
          { k: "Hardware (amortized)",  v: "~$3",        unit: "USD",   note: "B200 (~$30k) + DC at 2× overhead, 4-yr life." }
        ]
      },
      {
        heading: "Compute & energy",
        rows: [
          { k: "GPU compute",           v: "~1.5",       unit: "GPU-hr (B200)", note: "[est.] 1M tok / ~1500 tok·s⁻¹ on 8×B200 batched." },
          { k: "Wall electricity",      v: "~7",         unit: "kWh",   note: "[est.] node @ ~12 kW, PUE 1.3, 5–10 kWh range." },
          { k: "Embodied energy",       v: "~1.2",       unit: "kWh",   note: "Chip + DC manufacturing, amortized." }
        ]
      },
      {
        heading: "Atoms & water",
        rows: [
          { k: "Cooling water",         v: "~14",        unit: "L",     note: "Evap-cooled DC avg ~2 L/kWh." },
          { k: "Copper",                v: "~120",       unit: "mg",    note: "GPU boards + cabling, amortized." },
          { k: "Silicon (B200 dies)",   v: "~2",         unit: "mg",    note: "~5 g/module over 4-yr life." },
          { k: "Neodymium",             v: "~0.6",       unit: "mg",    note: "Fans, magnets." }
        ]
      },
      {
        heading: "Externalities",
        rows: [
          { k: "Carbon",                v: "~2.8",       unit: "kg CO₂e", note: "7 kWh × ~400 gCO₂e/kWh (US grid avg)." }
        ]
      }
    ],
    scale: {
      heading: "AT ANTHROPIC'S SCALE",
      subtitle: "extrapolated to ~2T tokens/month [est.]",
      rows: [
        { k: "Continuous grid load",   v: "~14 MW",    note: "≈ load of a small town." },
        { k: "Annual cooling water",   v: "~25 ML",    note: "≈ 10 Olympic pools." },
        { k: "B200-equivalent GPUs",   v: "~25k",      note: "in continuous flight." },
        { k: "Annual API revenue",     v: "~$30B",     note: "at posted rates, all tokens." }
      ]
    },
    methodology: "Throughput estimate from public benchmarks of similarly-sized MoE models on 8×B200; production batching efficiency varies 500–3000 tok·s⁻¹. Energy assumes node-level power of ~12 kW (8× B200 @ ~1 kW + ~50% node overhead) at PUE 1.3. Embodied energy uses ~3000 kWh per leading-edge GPU lifecycle (TSMC fab + packaging + HBM), amortized 35,000 hr at 80% utilization. All numbers labeled [est.] are triangulated, not first-party. Anthropic does not publish unit economics."
  },

  // ─── recent moves: layer-tagged news ───
  news: [
    { date: "2026-05-19", headline: "Anthropic ships Claude Opus 4.7 with 1M-token context",     tags: ["models"] },
    { date: "2026-05-17", headline: "CoreWeave signs 1.5 GW PPA with Constellation through 2035", tags: ["cloud", "energy"] },
    { date: "2026-05-12", headline: "MP Materials, Apollo close $1B rare-earth processing facility", tags: ["materials"] },
    { date: "2026-05-09", headline: "Oklo selects first four datacenter sites for SMR co-location", tags: ["energy"] },
    { date: "2026-05-04", headline: "Mistral raises €1.2B at €15B valuation; NVIDIA participates",  tags: ["models"] },
    { date: "2026-04-28", headline: "TSMC accelerates Arizona Fab 21 to N2 process by 2027",        tags: ["compute"] },
    { date: "2026-04-22", headline: "Microsoft restarts second Three Mile Island reactor for AI",   tags: ["energy", "cloud"] }
  ],

  // ─── layers (top to bottom in viewport: user-facing → upstream) ───
  layers: [
    { id: "apps",      label: "Apps & Agents" },
    { id: "services",  label: "Services" },
    { id: "tooling",   label: "Tooling & Middleware" },
    { id: "data",      label: "Data Layer" },
    { id: "models",    label: "Foundation Models" },
    { id: "cloud",     label: "Cloud & Inference" },
    { id: "compute",   label: "Compute" },
    { id: "energy",    label: "Energy" },
    { id: "materials", label: "Raw Materials" }
  ],

  // ─── nodes (with size 1-10 for visual weight; rough proxy for capex/scale) ───
  nodes: [
    // apps
    { id: "cursor",      name: "Cursor",      layer: "apps", size: 4, region: "US", blurb: "AI-native code editor; built atop frontier model APIs.", metrics: { "ARR (2025)": "$500M+", "founded": 2022, "headcount": "~80" } },
    { id: "perplexity",  name: "Perplexity",  layer: "apps", size: 4, region: "US", blurb: "Answer engine combining search and LLM reasoning.", metrics: { "valuation": "$9B (2025)", "founded": 2022 } },
    { id: "harvey",      name: "Harvey",      layer: "apps", size: 3, region: "US", blurb: "LLM platform for legal workflows; enterprise law firms.", metrics: { "valuation": "$5B (2025)", "founded": 2022 } },
    { id: "replit",      name: "Replit",      layer: "apps", size: 3, region: "US", blurb: "Browser IDE; AI agents for end-to-end app generation.", metrics: { "valuation": "$1.2B", "founded": 2016 } },

    // services
    { id: "accenture",   name: "Accenture",   layer: "services", size: 6, region: "Global", blurb: "Integrator deploying GenAI inside Fortune 500 stacks.", metrics: { "AI bookings (FY25)": "$3B+", "headcount": "750k" } },

    // tooling
    { id: "pinecone",    name: "Pinecone",    layer: "tooling", size: 3, region: "US", blurb: "Managed vector database for retrieval over embeddings.", metrics: { "valuation": "$750M", "founded": 2019 } },
    { id: "langchain",   name: "LangChain",   layer: "tooling", size: 3, region: "US", blurb: "Open-source orchestration framework; LangSmith observability.", metrics: { "GitHub stars": "95k+", "founded": 2022 } },
    { id: "braintrust",  name: "Braintrust",  layer: "tooling", size: 2, region: "US", blurb: "Evals and observability for LLM applications.", metrics: { "founded": 2023 } },

    // data
    { id: "scaleai",     name: "Scale AI",    layer: "data", size: 5, region: "US", blurb: "Human-labeled training and eval data at hyperscale.", metrics: { "valuation": "$14B", "Meta stake": "49% (2024)" } },
    { id: "surge",       name: "Surge AI",    layer: "data", size: 3, region: "US", blurb: "Premium RLHF and labeled data; rivals Scale at the high end.", metrics: { "founded": 2020 } },

    // models
    { id: "anthropic",   name: "Anthropic",   layer: "models", size: 8, region: "US", blurb: "Claude model family; safety-focused frontier lab.", metrics: { "valuation": "$183B (2025)", "founded": 2021 } },
    { id: "openai",      name: "OpenAI",      layer: "models", size: 9, region: "US", blurb: "GPT model family; ChatGPT consumer product.", metrics: { "valuation": "$500B (2025)", "founded": 2015 } },
    { id: "deepmind",    name: "Google DeepMind", layer: "models", size: 8, region: "UK/US", blurb: "Gemini model family; vertically integrated with Google infra.", metrics: { "parent": "Alphabet", "founded": 2010 } },
    { id: "meta",        name: "Meta AI",     layer: "models", size: 7, region: "US", blurb: "Llama open-weights family; consumer AI inside Meta apps.", metrics: { "parent": "Meta", "open weights": "yes" } },
    { id: "mistral",     name: "Mistral",     layer: "models", size: 4, region: "FR", blurb: "Open-weights and proprietary frontier models; EU sovereign play.", metrics: { "valuation": "$15B (2026)", "founded": 2023 } },

    // cloud
    { id: "aws",         name: "AWS",         layer: "cloud", size: 10, region: "US", blurb: "Largest hyperscaler; primary infrastructure partner for Anthropic.", metrics: { "AI capex (FY25)": "~$95B", "parent": "Amazon" } },
    { id: "azure",       name: "Microsoft Azure", layer: "cloud", size: 10, region: "US", blurb: "Hyperscaler; exclusive cloud partner of OpenAI through 2030.", metrics: { "AI capex (FY25)": "~$95B" } },
    { id: "coreweave",   name: "CoreWeave",   layer: "cloud", size: 6, region: "US", blurb: "GPU-specialized neocloud; IPO'd 2025.", metrics: { "deployed GPUs": "~250k", "market cap": "~$35B" } },
    { id: "together",    name: "Together AI", layer: "cloud", size: 3, region: "US", blurb: "Open-model inference provider; hosts Llama, Mistral, others.", metrics: { "valuation": "$3.3B" } },

    // compute
    { id: "nvidia",      name: "NVIDIA",      layer: "compute", size: 10, region: "US", blurb: "Dominant AI accelerator vendor; H100 → B200 → Rubin.", metrics: { "market cap": "$3.5T", "AI revenue (FY25)": "~$130B" } },
    { id: "amd",         name: "AMD",         layer: "compute", size: 5, region: "US", blurb: "MI300/MI350 accelerators; closing the gap on memory bandwidth.", metrics: { "AI revenue": "~$8B" } },
    { id: "tsmc",        name: "TSMC",        layer: "compute", size: 9, region: "TW", blurb: "Fabricates >90% of leading-edge AI accelerators globally.", metrics: { "market cap": "$1.1T", "3nm capacity": "~150k wpm" } },
    { id: "asml",        name: "ASML",        layer: "compute", size: 7, region: "NL", blurb: "Sole supplier of EUV lithography tools to TSMC, Samsung, Intel.", metrics: { "market cap": "$290B" } },
    { id: "cerebras",    name: "Cerebras",    layer: "compute", size: 3, region: "US", blurb: "Wafer-scale engine; specialized inference cloud.", metrics: { "valuation": "$8B (2024)" } },

    // energy
    { id: "constellation", name: "Constellation Energy", layer: "energy", size: 7, region: "US", blurb: "Largest US nuclear operator; restarted Three Mile Island for Microsoft.", metrics: { "nuclear capacity": "23 GW", "market cap": "$95B" } },
    { id: "vistra",      name: "Vistra",      layer: "energy", size: 6, region: "US", blurb: "Integrated power producer; long-dated PPAs to hyperscalers.", metrics: { "capacity": "41 GW" } },
    { id: "oklo",        name: "Oklo",        layer: "energy", size: 3, region: "US", blurb: "Small modular reactor startup; targeting datacenter co-location.", metrics: { "first plant": "2027-28", "backers": "Sam Altman" } },

    // materials
    { id: "shinetsu",    name: "Shin-Etsu",   layer: "materials", size: 5, region: "JP", blurb: "World's largest supplier of silicon wafers for semiconductors.", metrics: { "wafer share": "~30%" } },
    { id: "mpmaterials", name: "MP Materials", layer: "materials", size: 4, region: "US", blurb: "Only US rare-earth mine + processing (Mountain Pass).", metrics: { "NdPr": "~15% of non-China supply" } },
    { id: "freeport",    name: "Freeport-McMoRan", layer: "materials", size: 6, region: "US", blurb: "Major copper producer; AI buildout is a copper-demand story.", metrics: { "copper output": "~4B lbs/yr" } }
  ],

  edges: [
    // ─── SUPPLY ───
    { s: "shinetsu",     t: "tsmc",       lens: "supply", label: "silicon wafers" },
    { s: "mpmaterials",  t: "nvidia",     lens: "supply", label: "rare earths" },
    { s: "freeport",     t: "tsmc",       lens: "supply", label: "copper" },
    { s: "asml",         t: "tsmc",       lens: "supply", label: "EUV tools" },
    { s: "tsmc",         t: "nvidia",     lens: "supply", label: "fab (3nm/4nm)" },
    { s: "tsmc",         t: "amd",        lens: "supply", label: "fab" },
    { s: "tsmc",         t: "cerebras",   lens: "supply", label: "fab (wafer-scale)" },
    { s: "nvidia",       t: "aws",        lens: "supply", label: "H100/B200" },
    { s: "nvidia",       t: "azure",      lens: "supply", label: "H100/B200" },
    { s: "nvidia",       t: "coreweave",  lens: "supply", label: "H100/B200" },
    { s: "amd",          t: "azure",      lens: "supply", label: "MI300X" },
    { s: "cerebras",     t: "together",   lens: "supply", label: "inference chips" },
    { s: "aws",          t: "anthropic",  lens: "supply", label: "compute" },
    { s: "azure",        t: "openai",     lens: "supply", label: "compute (exclusive)" },
    { s: "coreweave",    t: "anthropic",  lens: "supply", label: "compute" },
    { s: "coreweave",    t: "openai",     lens: "supply", label: "compute" },
    { s: "coreweave",    t: "mistral",    lens: "supply", label: "compute" },
    { s: "together",     t: "mistral",    lens: "supply", label: "model hosting" },
    { s: "anthropic",    t: "cursor",     lens: "supply", label: "Claude API" },
    { s: "anthropic",    t: "harvey",     lens: "supply", label: "Claude API" },
    { s: "openai",       t: "cursor",     lens: "supply", label: "GPT API" },
    { s: "openai",       t: "perplexity", lens: "supply", label: "GPT API" },
    { s: "anthropic",    t: "replit",     lens: "supply", label: "Claude API" },
    { s: "deepmind",     t: "replit",     lens: "supply", label: "Gemini API" },
    { s: "pinecone",     t: "cursor",     lens: "supply", label: "vector DB" },
    { s: "langchain",    t: "harvey",     lens: "supply", label: "orchestration" },
    { s: "braintrust",   t: "openai",     lens: "supply", label: "evals" },
    { s: "scaleai",      t: "openai",     lens: "supply", label: "labeled data" },
    { s: "surge",        t: "anthropic",  lens: "supply", label: "RLHF data" },
    { s: "scaleai",      t: "meta",       lens: "supply", label: "labeled data" },
    { s: "accenture",    t: "harvey",     lens: "supply", label: "deployment" },

    // ─── CAPITAL ───
    { s: "azure",        t: "openai",     lens: "capital", label: "$13B+ (Microsoft)" },
    { s: "aws",          t: "anthropic",  lens: "capital", label: "$8B (Amazon)" },
    { s: "deepmind",     t: "anthropic",  lens: "capital", label: "$2B+ (Alphabet)" },
    { s: "nvidia",       t: "coreweave",  lens: "capital", label: "anchor investor" },
    { s: "nvidia",       t: "mistral",    lens: "capital", label: "Series A/B" },
    { s: "nvidia",       t: "perplexity", lens: "capital", label: "strategic investor" },
    { s: "nvidia",       t: "together",   lens: "capital", label: "strategic investor" },
    { s: "azure",        t: "mistral",    lens: "capital", label: "minority stake" },
    { s: "meta",         t: "scaleai",    lens: "capital", label: "49% stake, $14B" },

    // ─── RESOURCE (flows weighted by magnitude) ───
    { s: "constellation",t: "azure",      lens: "resource", label: "9 TWh/yr nuclear", weight: 9 },
    { s: "vistra",       t: "aws",        lens: "resource", label: "12 TWh/yr", weight: 12 },
    { s: "oklo",         t: "aws",        lens: "resource", label: "1.5 GW planned 2030", weight: 1.5 },
    { s: "tsmc",         t: "nvidia",     lens: "resource", label: "~4M units/yr (B200-class)", weight: 4 },
    { s: "nvidia",       t: "coreweave",  lens: "resource", label: "~250k GPUs deployed", weight: 2.5 },
    { s: "nvidia",       t: "azure",      lens: "resource", label: "~1M GPUs deployed", weight: 10 },
    { s: "aws",          t: "anthropic",  lens: "resource", label: "$4B/yr compute", weight: 4 },
    { s: "azure",        t: "openai",     lens: "resource", label: "$13B+ compute reservation", weight: 13 },
    { s: "scaleai",      t: "openai",     lens: "resource", label: "~50M labeled examples", weight: 5 }
  ]
};
