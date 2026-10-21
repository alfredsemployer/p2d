# NVIDIA GTC Berlin 2026 keynote: Jensen Huang (21 Oct 2026)

About 93 minutes, from YouTube's automatic captions (`gtc-berlin-2026-transcript.txt`, timestamps in brackets).
The captions mishear some names: "Neotron" is Nemotron, "Grog 3" is Groq 3, "MVLink" is NVLink, "Jensen Wong" is Jensen Huang.

## Announcements
- **DSX Pod** [0:30]: a factory-built, pre-cabled, pre-tested AI factory unit. It is seven liquid-cooled Vera Rubin NVL72 racks linked by 17 km of Spectrum-X cabling, shipped in transportable containers with dry coolers and 800 V DC power. Huang says turn-on time drops from about 4–5 months to about 1 month, and each month counts: a 1 GW factory costs about $50B and earns tens of billions a year.
- **OpenShell + Sentry** [0:43]: OpenShell is an open-source (Apache 2.0) secure runtime for AI agents. It runs each agent in a sandbox, enforces policy on system calls, files and network, keeps keys outside the agent, and formally verifies policy changes. Sentry runs on BlueField-4 and monitors agents from a hardware-isolated domain, quarantining them in milliseconds. NVIDIA and Anthropic are partnering on Claude OpenShell agents.
- **Hyperion robotaxi platform** [1:11]: VW van, a new JLR car, Volvo and next-generation Mercedes join the standard AV architecture (14 cameras, 9 radars, 3 lidars, dual NVIDIA computers) for ride-hailing robotaxi fleets.
- **NVIDIA Agile One** [1:16]: a reference humanoid robot built with Agile Robots, pre-assembled with computer and software. Available Q1 next year.
- **RTX Spark PCs** [1:17]: a new line of Windows PCs (desktops, laptops, workstations) built over 4 years with Microsoft on the N1X chip, with 1 PFLOP and 128 GB memory. There is also a Windows DGX Station (20 PFLOPS, 754 GB), available at the end of this year.

## Other key points
- **Europe** [0:04]: NVIDIA invested nearly $10B in Europe in the last year, announced 14 startup investments this week, and has 12,000+ partnerships there. Huang tells Europe to produce AI, not just consume it.
- **AI as a "five-layer cake"** [0:09]: energy → chips → AI factories → models → applications.
- **Vera Rubin is in full production** [0:21]: 100% liquid cooled, no cables, and a node assembles in under 5 minutes versus 2 hours for Grace Blackwell. It is about 30× Blackwell, which was about 30× Hopper. NVIDIA claims 1,000,000× AI performance in 10 years, versus 100× under Moore's law. On stage: the Vera CPU, and Spectrum-X co-packaged optics (512 ports at 200 Gb/s, in volume production).
- **Five parts of an agent** [0:42]: model, harness, sandbox, knowledge, tools.
  - Open models with full data and recipes: Nemotron, Cosmos, GR00T, Alpamayo, Ising, Earth-2.
  - Knowledge layer: Nemotron Parse/Embed/Rerank and Kumo.
  - Tools: CUDA-X libraries.
  - Demos: Lila Sciences (drug design), Siemens Erlangen factory, Dassault (adapting a VW door design).
- **Telecom** [1:06]: the first commercial call on CUDA-based RAN, with T-Mobile and Nokia. Huang sees the ~100 GW of cell sites becoming distributed AI infrastructure.
- **Demo** [1:20]: Pollen Robotics' "MicroDuck" robots, designed, simulated and trained by an agent on RTX Spark, then walked on stage.
- **The rest**: there was a brief audience interruption around [0:23]. The keynote closed with a Eurovision-style music video.
