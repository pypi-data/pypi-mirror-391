## Summary — The 9 Foundational Crawler Categories
 Category | Core Question It Answers | Example Type 
 --- | --- | -- 
[Purpose](#by-purpose-goal-or-intent)	| Why is it crawling? | Scraping crawler
[Crawl Strategy](#by-crawl-strategy-traversal-logic) | How does it traverse pages? | BFS, DFS, Focused
[Scheduling Behavior](#by-scheduling-behavior-temporal-logic) | When does it crawl? | Incremental, Continuous
[Architecture](#by-architecture-system-design) | How is it organized? | Distributed crawler
[Scope](#by-scope-coverage-target) | How wide does it crawl? | Site-wide crawler
[Data Access Method](#by-data-access-method) | Where does it get data from? | API crawler
[Ethical Behavior](#by-ethical-or-policy-behavior) | How does it treat site rules? | Polite crawler
[Intelligence Level](#by-intelligence-level) | How does it make decisions? | LLM-guided crawler
[Integration Role](#by-integration-role-system-position) | How does it fit into a pipeline? | Modular crawler

## By Purpose (Goal or Intent)

Defines why the crawler exists — what it aims to achieve.

### Type Description
- [ ] **Discovery Crawler** - Finds and collects URLs or metadata; builds an index or frontier.
- [ ] **Scraping Crawler** - Extracts structured data from pages *(e.g., tables, text, entities)*.
- [ ] **Monitoring Crawler** - Tracks updates or changes in content over time.
- [ ] **Archival Crawler** - Saves full page copies for preservation or offline analysis.
- [ ] **Testing / Auditing Crawler** - Used for SEO, broken-link checking, or site compliance validation.

## By Crawl Strategy (Traversal Logic)

Defines how pages are selected or ordered during crawling.

### Type Description
- [X] **Breadth-First (BFS)** - Crawl all pages at one depth before moving deeper.
- [x] **Depth-First (DFS)** - Crawl one path as deep as possible before backtracking.
- [x] **Priority-Based** - Assign numerical priority scores to URLs.
- [ ] **Adaptive Adjust** - strategy dynamically based on feedback or results.
- [ ] **Context-Aware** - Use HTML structure and semantics to guide crawling decisions.

## By Scheduling Behavior (Temporal Logic)

Defines when and how often the crawler operates.

### Type Description
- [x] **One-Shot** - Runs once and stops after completion.
- [x] **Incremental** - Re-crawls known pages periodically to detect updates.
- [x] **Continuous** - Never stops constantly cycles through crawl/revisit loops.
- [ ] **Event-Driven** - Triggered by signals such as webhooks or detected changes.

## By Scope (Coverage Target)

Defines how broadly the crawler explores the web.

### Type Description
- [ ] **Focused** - only relevant pages based on topic or keyword.
- [x] **Site-Wide** - Restricted to one domain or subdomain.
- [x] **Multi-Domain**	- Crawls a fixed list of domains.
- [ ] **Vertical / Domain-Specific** - Focused on one industry (e.g., sports, jobs, e-commerce).
- [ ] **Web-Scale** - Crawls the entire public web; search-engine level.

## By Architecture (System Design)

Defines how the crawler is built and organized internally.

### Type-Description
- [ ] Centralized	Single control node managing all crawl tasks.
- [ ] Distributed	Multiple coordinated nodes sharing workload and URL queues.
- [ ] Peer-to-Peer	Decentralized — nodes share discovered URLs without a central coordinator.
- [ ] Cloud / Serverless	Uses scalable, ephemeral functions to perform crawl tasks.


## By Data Access Method

Defines where and how data is retrieved.

### Type Description
- [ ] HTML / Page Crawler	Fetches and parses HTML pages.
- [ ] API Crawler	Pulls structured data through APIs.
- [ ] Headless / Rendered Crawler	Uses browsers or headless engines to handle JavaScript.
- [ ] Hybrid Crawler	Combines HTML, API, and headless methods adaptively.

## By Ethical or Policy Behavior

Defines how the crawler interacts with site policies.

### Type Description
- [ ] Polite Crawler	Obeys robots.txt, rate limits, and crawl delays.
- [ ] Aggressive Crawler	Ignores some restrictions (not recommended).
- [ ] Authenticated Crawler	Operates within login-required environments.

## By Intelligence Level

Defines how much decision-making or AI the crawler uses.

### Type Description
- [ ] Rule-Based	Follows fixed rules or regex filters.
- [ ] Heuristic-Based	Uses handcrafted scoring or relevance functions.
- [ ] ML-Guided	Uses machine learning for link scoring or prioritization.
- [ ] LLM-Guided	Uses large language models to interpret pages and guide navigation.

## By Integration Role (System Position)

Defines how the crawler fits into the larger data pipeline.

### Type Description
- [ ] **Standalone Crawler** - Operates independently, outputs raw pages or URLs.
- [ ] **Coupled Crawler**	- Integrates scraping logic directly inside the crawl loop.
- [ ] **Modular Crawler**	- Works with separate scraper, parser, and storage components.
- [ ] **Streaming Crawler** - Feeds data continuously into real-time pipelines (Kafka, etc.).