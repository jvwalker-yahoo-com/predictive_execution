# Graph Report - sotck_predict  (2026-11-18)

## Corpus Check
- 35 files · ~14,531 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: .xml 5, (none) 2, .css 2)

## Summary
- 338 nodes · 622 edges · 20 communities (8 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3b627bce`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Orchestrator
- WebAppInterface.java
- server.py
- serve_apk.py
- engine/federation.py
- MainActivity.java
- app.js
- PROGRESS.md
- eToro ReAuth Mobile Companion (Standalone APK)
- OpenBBUnifiedRouter
- Arbitration
- Brain
- Evolution
- apply_mode_behaviour
- Parliament
- PersonalityEngine
- TemporalEngine
- FederationBrain

## God Nodes (most connected - your core abstractions)
1. `run_tick()` - 22 edges
2. `predict()` - 20 edges
3. `Orchestrator` - 14 edges
4. `OpenBBUnifiedRouter` - 12 edges
5. `MarketIntelSuite` - 12 edges
6. `WebAppInterface` - 12 edges
7. `initEventListeners()` - 11 edges
8. `impact_model()` - 10 edges
9. `latency_model()` - 10 edges
10. `slippage_model()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `2026-11-18 Full Code Audit, OpenBB Decision System Integration & Performance Optimization` --references--> `ImpactBrain`  [INFERRED]
  PROGRESS.md → models/impact.py
- `2026-11-18 Full Code Audit, OpenBB Decision System Integration & Performance Optimization` --references--> `LatencyBrain`  [INFERRED]
  PROGRESS.md → models/latency.py
- `2026-11-18 Full Code Audit, OpenBB Decision System Integration & Performance Optimization` --references--> `SlippageBrain`  [INFERRED]
  PROGRESS.md → models/slippage.py
- `2026-11-18 Full Code Audit, OpenBB Decision System Integration & Performance Optimization` --references--> `_TTLCache`  [INFERRED]
  PROGRESS.md → engine/openbb_intel.py
- `2026-11-18 Full Code Audit, OpenBB Decision System Integration & Performance Optimization` --references--> `OpenBBUnifiedRouter`  [INFERRED]
  PROGRESS.md → engine/openbb_intel.py

## Import Cycles
- None detected.

## Communities (20 total, 12 thin omitted)

### Community 0 - "Orchestrator"
Cohesion: 0.09
Nodes (15): ArbitrationPrecedent, BrainGenome, BrainPerformanceSample, BrainPersonality, ParliamentBill, TemporalEpisode, init_db(), Orchestrator (+7 more)

### Community 2 - "server.py"
Cohesion: 0.08
Nodes (37): get_mode_history(), impact_model(), latency_model(), mode_model(), predict(), risk_model(), slippage_model(), synthesize_openbb_decision() (+29 more)

### Community 3 - "serve_apk.py"
Cohesion: 0.12
Nodes (6): main(), ApkDeliveryHandler, get_file_sha256(), get_lan_ip(), main(), render_ascii_qr()

### Community 5 - "engine/federation.py"
Cohesion: 0.18
Nodes (18): _evaluate_federation(), generate_arbitration(), generate_decision(), generate_episode(), generate_federation(), generate_performance(), generate_precedent(), generate_state() (+10 more)

### Community 7 - "app.js"
Cohesion: 0.37
Nodes (15): Bridge, checkPortfolioSnapshot(), el, generateUUID(), initEventListeners(), loadSettings(), log(), pushConfigToServer() (+7 more)

### Community 8 - "PROGRESS.md"
Cohesion: 0.08
Nodes (17): fetchJSON(), tick(), update(), 2026-10-21 AI Agent Audit 401 "User not found" Diagnosis & Fix, 2026-10-21 OpenBB Integration, 2026-10-21 OpenRouter Key Verified & Applied, databases, name (+9 more)

### Community 10 - "eToro ReAuth Mobile Companion (Standalone APK)"
Cohesion: 0.25
Nodes (7): eToro ReAuth Mobile Companion (Standalone APK), 📱 Features, 🚀 How to Install on Your Phone, Option A: Via Local Wi-Fi (Fastest), Option B: Via USB Cable / ADB, Option C: Cloud Drive / Messaging, 🛠 Rebuilding the APK

### Community 12 - "OpenBBUnifiedRouter"
Cohesion: 0.07
Nodes (9): OpenBBUnifiedRouter, _fetch(), _fetch(), _fetch_series(), _TTLCache, MarketIntelSuite, _fetch(), RiskBrain (+1 more)

## Knowledge Gaps
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MarketIntelSuite` connect `OpenBBUnifiedRouter` to `PROGRESS.md`, `server.py`, `openbb_intel.py`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Orchestrator` (e.g. with `ArbitrationPrecedent` and `BrainGenome`) actually correct?**
  _`Orchestrator` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `Orchestrator` be split into smaller, more focused modules?**
  _Cohesion score 0.09407665505226481 - nodes in this community are weakly interconnected._
- **Why does `OpenBBUnifiedRouter` connect `OpenBBUnifiedRouter` to `openbb_intel.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Should `WebAppInterface.java` be split into smaller, more focused modules?**
  _Cohesion score 0.09195402298850575 - nodes in this community are weakly interconnected._
- **Should `server.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07731694828469023 - nodes in this community are weakly interconnected._
- **Should `serve_apk.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11594202898550725 - nodes in this community are weakly interconnected._