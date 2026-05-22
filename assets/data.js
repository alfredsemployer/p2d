/* seed dataset — illustrative, not authoritative. swap with scraper output later. */

window.GRAPH = {
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

  nodes: [
    // apps & agents
    { id: "cursor",      name: "Cursor",      layer: "apps", region: "US", blurb: "AI-native code editor; built atop frontier model APIs.", metrics: { "ARR (2025)": "$500M+", "founded": 2022, "headcount": "~80" } },
    { id: "perplexity",  name: "Perplexity",  layer: "apps", region: "US", blurb: "Answer engine combining search and LLM reasoning.", metrics: { "valuation": "$9B (2025)", "founded": 2022 } },
    { id: "harvey",      name: "Harvey",      layer: "apps", region: "US", blurb: "LLM platform for legal workflows; enterprise law firms.", metrics: { "valuation": "$5B (2025)", "founded": 2022 } },
    { id: "replit",      name: "Replit",      layer: "apps", region: "US", blurb: "Browser IDE; AI agents for end-to-end app generation.", metrics: { "valuation": "$1.2B", "founded": 2016 } },

    // services
    { id: "accenture",   name: "Accenture",   layer: "services", region: "Global", blurb: "Integrator deploying GenAI inside Fortune 500 stacks.", metrics: { "AI bookings (FY25)": "$3B+", "headcount": "750k" } },

    // tooling & middleware
    { id: "pinecone",    name: "Pinecone",    layer: "tooling", region: "US", blurb: "Managed vector database for retrieval over embeddings.", metrics: { "valuation": "$750M", "founded": 2019 } },
    { id: "langchain",   name: "LangChain",   layer: "tooling", region: "US", blurb: "Open-source orchestration framework; LangSmith observability.", metrics: { "GitHub stars": "95k+", "founded": 2022 } },
    { id: "braintrust",  name: "Braintrust",  layer: "tooling", region: "US", blurb: "Evals and observability for LLM applications.", metrics: { "founded": 2023 } },

    // data layer
    { id: "scaleai",     name: "Scale AI",    layer: "data", region: "US", blurb: "Human-labeled training and eval data at hyperscale.", metrics: { "valuation": "$14B", "Meta stake": "49% (2024)" } },
    { id: "surge",       name: "Surge AI",    layer: "data", region: "US", blurb: "Premium RLHF and labeled data; rivals Scale at the high end.", metrics: { "founded": 2020 } },

    // foundation models
    { id: "anthropic",   name: "Anthropic",   layer: "models", region: "US", blurb: "Claude model family; safety-focused frontier lab.", metrics: { "valuation": "$183B (2025)", "founded": 2021 } },
    { id: "openai",      name: "OpenAI",      layer: "models", region: "US", blurb: "GPT model family; ChatGPT consumer product.", metrics: { "valuation": "$500B (2025)", "founded": 2015 } },
    { id: "deepmind",    name: "Google DeepMind", layer: "models", region: "UK/US", blurb: "Gemini model family; vertically integrated with Google infra.", metrics: { "parent": "Alphabet", "founded": 2010 } },
    { id: "meta",        name: "Meta AI",     layer: "models", region: "US", blurb: "Llama open-weights family; consumer AI inside Meta apps.", metrics: { "parent": "Meta", "open weights": "yes" } },
    { id: "mistral",     name: "Mistral",     layer: "models", region: "FR", blurb: "Open-weights and proprietary frontier models; EU sovereign play.", metrics: { "valuation": "$6B", "founded": 2023 } },

    // cloud & inference
    { id: "aws",         name: "AWS",         layer: "cloud", region: "US", blurb: "Largest hyperscaler; primary infrastructure partner for Anthropic.", metrics: { "AI capex (FY25)": "~$75B", "parent": "Amazon" } },
    { id: "azure",       name: "Microsoft Azure", layer: "cloud", region: "US", blurb: "Hyperscaler; exclusive cloud partner of OpenAI through 2030.", metrics: { "AI capex (FY25)": "~$80B" } },
    { id: "coreweave",   name: "CoreWeave",   layer: "cloud", region: "US", blurb: "GPU-specialized neocloud; IPO'd 2025.", metrics: { "deployed GPUs": "~250k", "market cap": "~$35B" } },
    { id: "together",    name: "Together AI", layer: "cloud", region: "US", blurb: "Open-model inference provider; hosts Llama, Mistral, others.", metrics: { "valuation": "$3.3B" } },

    // compute
    { id: "nvidia",      name: "NVIDIA",      layer: "compute", region: "US", blurb: "Dominant AI accelerator vendor; H100 → B200 → Rubin.", metrics: { "market cap": "$3.5T", "AI revenue (FY25)": "~$130B" } },
    { id: "amd",         name: "AMD",         layer: "compute", region: "US", blurb: "MI300/MI350 accelerators; closing the gap on memory bandwidth.", metrics: { "AI revenue": "~$8B" } },
    { id: "tsmc",        name: "TSMC",        layer: "compute", region: "TW", blurb: "Fabricates >90% of leading-edge AI accelerators globally.", metrics: { "market cap": "$1.1T", "3nm capacity": "~150k wpm" } },
    { id: "asml",        name: "ASML",        layer: "compute", region: "NL", blurb: "Sole supplier of EUV lithography tools to TSMC, Samsung, Intel.", metrics: { "market cap": "$290B" } },
    { id: "cerebras",    name: "Cerebras",    layer: "compute", region: "US", blurb: "Wafer-scale engine; specialized inference cloud.", metrics: { "valuation": "$8B (2024)" } },

    // energy
    { id: "constellation", name: "Constellation Energy", layer: "energy", region: "US", blurb: "Largest US nuclear operator; restarted Three Mile Island for Microsoft.", metrics: { "nuclear capacity": "23 GW", "market cap": "$95B" } },
    { id: "vistra",      name: "Vistra",      layer: "energy", region: "US", blurb: "Integrated power producer; long-dated PPAs to hyperscalers.", metrics: { "capacity": "41 GW" } },
    { id: "oklo",        name: "Oklo",        layer: "energy", region: "US", blurb: "Small modular reactor startup; targeting datacenter co-location.", metrics: { "first plant": "2027-28", "backers": "Sam Altman" } },

    // raw materials
    { id: "shinetsu",    name: "Shin-Etsu",   layer: "materials", region: "JP", blurb: "World's largest supplier of silicon wafers for semiconductors.", metrics: { "wafer share": "~30%" } },
    { id: "mpmaterials", name: "MP Materials", layer: "materials", region: "US", blurb: "Only US rare-earth mine + processing (Mountain Pass).", metrics: { "NdPr": "~15% of non-China supply" } },
    { id: "freeport",    name: "Freeport-McMoRan", layer: "materials", region: "US", blurb: "Major copper producer; AI buildout is a copper-demand story.", metrics: { "copper output": "~4B lbs/yr" } }
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

    // ─── RESOURCE ───
    { s: "constellation",t: "azure",      lens: "resource", label: "9 TWh/yr nuclear", weight: 9 },
    { s: "vistra",       t: "aws",        lens: "resource", label: "12 TWh/yr", weight: 12 },
    { s: "oklo",         t: "aws",        lens: "resource", label: "1.5 GW planned 2030", weight: 1.5 },
    { s: "tsmc",         t: "nvidia",     lens: "resource", label: "~4M units/yr (B200 class)", weight: 4 },
    { s: "nvidia",       t: "coreweave",  lens: "resource", label: "~250k GPUs deployed", weight: 2.5 },
    { s: "nvidia",       t: "azure",      lens: "resource", label: "~1M GPUs deployed", weight: 10 },
    { s: "aws",          t: "anthropic",  lens: "resource", label: "$4B/yr compute", weight: 4 },
    { s: "azure",        t: "openai",     lens: "resource", label: "$13B+ compute reservation", weight: 13 },
    { s: "scaleai",      t: "openai",     lens: "resource", label: "~50M labeled examples", weight: 5 }
  ]
};
