window.COMPONENTS = [
  {
    id: "trend_collector",
    file: "trend_collector.py",
    name: "Trend Collector",
    layer: "Ingestion",
    tag: "core",
    why: "Every effective AI product factory needs a reliable signal of what the market wants RIGHT NOW. The Trend Collector is the 'antenna' of the entire system — without it, we are building templates based on guesswork instead of data. It ensures we are always chasing actual trending design topics rather than last year's ideas.",
    what: "Connects to Reddit's PRAW API targeting design-heavy subreddits (r/UI_Design, r/web_design, r/SaaS) and falls back to HackerNews if Reddit is unavailable. It normalizes the score into a 0.0–0.99 floating-point popularity index and caches results to prevent quota burns on repeat pipeline executions.",
    inputs: ["Reddit API credentials", "HN API (public)", "cache.py TTL"],
    outputs: ["Trend Object: {trend, popularity_score, source, reference_url}"],
    methods: ["collect() → Trend dict", "cache.get('latest_trend')", "reddit.subreddit().hot()"],
    deps: ["praw", "requests", "cache.py", "app.config.settings"],
    failures: "If Reddit API returns 401/403 or rate-limits, the `except` block catches and falls to HackerNews. If HN also fails, a deterministic fallback dict ('AI SaaS landing page') is returned. The system never returns None.",
    future: "Replace PRAW with a Kafka consumer streaming real-time Reddit events, eliminating polling delays. Integrate Twitter/X API to capture viral UI screenshots as they emerge. Add topic clustering with BERTopic to automatically group similar trends into archetypes.",
    alternatives: "Google Trends API (paid) offers normalized volumes per geography. Brandwatch or Semrush APIs provide professional-grade social listening. The current PyTrends + Reddit approach is deliberately zero-cost and will scale until ~10K daily runs without burnout.",
    dataFlow: `Trend Object Example:
{
  "trend": "Reddit Theme: AI Dashboard UI",
  "popularity_score": 0.88,
  "source": "reddit_api: r/UI_Design",
  "reference_url": "https://vercel.com/dashboard"
}`
  },
  {
    id: "design_scraper",
    file: "design_scraper.py",
    name: "Design Scraper",
    layer: "Ingestion",
    tag: "core",
    why: "Trend topics alone are words without pictures. The Scraper converts a string like 'glassmorphic dashboard' into actual pixel-level visual references. This is what elevates the system from keyword-based generation to visual-intelligence-driven generation. Phase 3 can only generate what Phase 2 has physically seen.",
    what: "Launches real headless Chromium via Playwright. Throttles every request through the Rate Limiter module (jitter + user-agent rotation) to prevent blocks. Can authenticate natively into Pinterest, scrape Dribbble search pages, or navigate and full-page screenshot live product websites. Results are cached per topic.",
    inputs: ["Trend Object", "settings (pinterest_email, pinterest_password)", "rate_limiter"],
    outputs: ["Design Reference: {title, image_urls[], source, reputation_score}"],
    methods: ["scrape(trend)", "scrape_pinterest(topic)", "scrape_dribbble(topic)", "scrape_live_website(url)"],
    deps: ["playwright", "asyncio", "cache.py", "rate_limiter.py", "settings"],
    failures: "If Playwright crashes or CAPTCHAs appear, the try/except returns placehold.co URLs ensuring downstream modules never receive null bytes. Rate limiter prevents IP bans via randomized waits.",
    future: "Replace Playwright with Apify cloud actors (pre-built scrapers for Pinterest/Dribbble maintained by Apify team). Use rotating residential proxy services (BrightData/Oxylabs) to bypass geo-filters. Add concurrency pools to scrape multiple topics in parallel.",
    alternatives: "Apify REST API handles Pinterest/Dribbble natively without browser automation complexity. Firecrawl API offers LLM-ready markdown extraction. For pure image acquisition, Google Custom Search JSON API can fetch high-quality design images without scraping.",
    dataFlow: `Design Reference Example:
{
  "title": "Live Scraped Dribbble UI for AI Dashboard",
  "image_urls": ["https://cdn.dribbble.com/..."],
  "source": "Scraped from Dribbble: AI Dashboard",
  "reputation_score": 0.8
}`
  },
  {
    id: "trend_analyzer",
    file: "trend_analyzer.py",
    name: "Trend Analyzer",
    layer: "Analysis",
    tag: "core",
    why: "Images cannot be stored in a database and queried by 'component type'. The Analyzer is the translation layer between visual pixels and machine-readable layout logic. It uses Gemini's multimodal vision to do what no regex or CV model does cheaply: understand semantic UI intent from screenshots. This is the 'brain' of Phase 2.",
    what: "Constructs a multi-part payload containing text prompt + raw image bytes and sends it to Gemini 2.5 Flash. The prompt instructs Gemini to extract layout sections, typography, color palette, implied animations, AND spatial bounding coordinates [x,y,w,h] for each identified component. The response is cleaned of markdown fences and parsed to JSON.",
    inputs: ["List of Design Reference objects", "Image files (local screenshots or remote URLs)"],
    outputs: ["Visual Analysis: {popular_sections, typography, colors, implied_animations, annotations[]}"],
    methods: ["analyze(designs[])", "requests.get(url) for image download", "model.generate_content(payload)"],
    deps: ["google.generativeai", "requests", "json", "settings"],
    failures: "If Gemini returns malformed JSON or markdown-wrapped output, the fallback strips fences and retries parsing. If completely unparseable, returns a safe static dict with basic section types. LLM quota errors are bubbled up to the pipeline for full retry.",
    future: "Switch to Gemini 2.0 Flash for 3x faster inference with native image understanding. Add Vision Transformer (ViT) fallback for local bounding box detection when API quotas are exceeded. Store annotated image metadata in a vector DB (Pinecone/Weaviate) for semantic pattern retrieval.",
    alternatives: "OpenAI GPT-4o Vision offers competitive multimodal understanding. Anthropic Claude 3.5 Sonnet is exceptional at structured JSON output from images. Local models like LLaVA or Moondream 2 could run entirely offline — critical for enterprise data sensitivity.",
    dataFlow: `Visual Analysis Output Example:
{
  "popular_sections": ["hero", "metrics_grid", "chart_card"],
  "typography": "Inter 700 for headings, 400 for body",
  "colors": ["#0f172a", "#3b82f6", "#10b981"],
  "implied_animations": ["fade_in", "counter_animation"],
  "annotations": [
    {"component": "sidebar_nav", "coordinates": [0.0, 0.0, 0.15, 1.0]},
    {"component": "metrics_card", "coordinates": [0.2, 0.1, 0.7, 0.2]}
  ]
}`
  },
  {
    id: "pattern_extractor",
    file: "pattern_extractor.py",
    name: "Pattern Extractor",
    layer: "Analysis",
    tag: "core",
    why: "Raw LLM output is inconsistent — sometimes verbose, sometimes terse, sometimes structured differently. Pattern Extractor is the 'standardization tax' that every LLM output must pay before touching storage. It ensures every downstream module receives a normalized, predictable UI Pattern Object regardless of how creative Gemini was in responding.",
    what: "Takes the raw visual analysis output from the Trend Analyzer and maps it to a canonical Pattern schema. Extracts layout_type, structure array, and style flags into a consistent object that the Demand Estimator, Brief Generator, and Pattern Library all understand.",
    inputs: ["Visual Analysis JSON from Trend Analyzer"],
    outputs: ["UI Pattern: {layout_type, structure[], style, complexity_score}"],
    methods: ["extract(analysis_dict)"],
    deps: ["market_intelligence.trend_analyzer (indirect)"],
    failures: "Returns graceful fallback with basic hero+feature structure if field mapping fails.",
    future: "Train a fine-tuned classification model on historical patterns to auto-tag pattern archetypes (e.g. 'SaaS Dashboard', 'Landing Page', 'Web3 Dashboard'). Generate vector embeddings of patterns to enable semantic similarity search across pattern library.",
    alternatives: "JSON Schema validation (jsonschema library) could handle normalization. Pydantic v2 models would automatically enforce field contracts with typed coercion.",
    dataFlow: `UI Pattern Object:
{
  "layout_type": "dashboard",
  "structure": ["sidebar_nav", "metrics_grid", "chart_panel"],
  "style": "glassmorphic_dark",
  "complexity_score": 0.75
}`
  },
  {
    id: "demand_estimator",
    file: "demand_estimator.py",
    name: "Demand Estimator",
    layer: "Analysis",
    tag: "core",
    why: "Visual beauty ≠ market viability. A stunning UI pattern may have zero customers searching for it. The Demand Estimator bridges the gap between aesthetic quality and commercial opportunity by anchoring design decisions to real Google search volume data — ensuring we build what people are actually paying for.",
    what: "Uses PyTrends (unofficial Google Trends API) to query 30-day search interest for the pattern type as a keyword. Normalizes the interest index (0-100) to a 0.0-1.0 floating-point Demand Score. Falls back to an empirical 0.91 score for AI-related templates based on known market dominance.",
    inputs: ["UI Pattern Object"],
    outputs: ["Demand Object: {template_type, demand_score, competition_score}"],
    methods: ["estimate(patterns)", "pytrends.build_payload()", "pytrends.interest_over_time()"],
    deps: ["pytrends", "settings"],
    failures: "PyTrends frequently gets rate-limited by Google. The module catches all exceptions and falls back to a hardcoded 0.91 score ensuring the pipeline never stalls on trend data acquisition.",
    future: "Integrate SerpAPI (Google Search Volume) for paid, reliable keyword research. Add SEMrush API for competition analysis (CPC, keyword difficulty). Build a time-series trend forecasting model using ARIMA or Prophet to predict demand 30 days into the future.",
    alternatives: "Google Ads Keyword Planner API (requires billing) provides real CPC and volume data. Ahrefs API offers professional SEO data including backlink difficulty. For zero-cost: use Google Autocomplete frequency as a proxy for demand.",
    dataFlow: `Demand Object:
{
  "template_type": "AI SaaS dashboard template",
  "demand_score": 0.82,
  "competition_score": 0.45,
  "trend_velocity": 1.2
}`
  },
  {
    id: "opportunity_ranker",
    file: "opportunity_ranker.py",
    name: "Opportunity Ranker",
    layer: "Evaluation",
    tag: "eval",
    why: "Not all high-demand items are equally worth building. A competitive red ocean with 0.95 demand but 0.99 competition is less valuable than a niche market with 0.8 demand and 0.1 competition. The Opportunity Ranker injects this economic rationality into the template selection process via a multidimensional scoring function.",
    what: "Applies the formula: `Opportunity Score = Demand Score × Trend Velocity × (1 - Competition Score)`. Sorts the resulting array descending, returning the top-ranked opportunity as the primary build target for Phase 3.",
    inputs: ["Array of Demand Objects"],
    outputs: ["Sorted list of Demand Objects with opportunity_score added"],
    methods: ["rank_opportunities(opportunities[])"],
    deps: ["None (pure computation)"],
    failures: "Defaults to returning the original demand object unchanged if the array is empty or malformed.",
    future: "Build a multi-objective Pareto optimization replacing the scalar formula. Add portfolio tracking to ensure Phase 3 builds a diverse mix of product types instead of repeatedly building the highest-scoring template archetype.",
    alternatives: "Use a trained ML regression model on historical Phase 3 sales/engagement data to predict true commercial value instead of computed approximations.",
    dataFlow: `Ranked Output:
{
  "template_type": "AI SaaS dashboard",
  "demand_score": 0.82,
  "competition_score": 0.45,
  "trend_velocity": 1.0,
  "opportunity_score": 0.451
}`
  },
  {
    id: "design_brief_generator",
    file: "design_brief_generator.py",
    name: "Brief Generator",
    layer: "Synthesis",
    tag: "core",
    why: "All the data gathered — trends, visual patterns, demand scores, reputation — is meaningless to Phase 3 unless it is translated into a clear, actionable specification. The Brief Generator is the 'Product Manager' of the system, synthesizing raw intelligence into a structured engineering specification that the code generator can execute without ambiguity.",
    what: "Aggregates all previous pipeline state objects and sends them to Gemini 2.5 Pro with a strict prompt requiring exactly the Design Brief schema. Any markdown wrapping is stripped and the response is parsed. If Gemini fails, falls back to an algorithmically composed brief using the collected data directly.",
    inputs: ["trends, designs, analysis, patterns, demand, references"],
    outputs: ["Design Brief: {product_type, target_market, style, sections[], animation_type, demand_score, quality_score, provenance{}}"],
    methods: ["generate(...all state objects...)", "model.generate_content(prompt)", "json.loads(cleaned_text)"],
    deps: ["google.generativeai", "settings"],
    failures: "Fallback brief construction ensures all required keys exist even when Gemini fails, preventing validator rejection on first execution.",
    future: "Fine-tune a small LLM (Mistral 7B) on curated Design Brief → Template pairings to produce consistently structured outputs without cloud API dependency. Store all pair data now for future fine-tuning corpus.",
    alternatives: "Use GPT-4o with strict JSON mode (response_format=json_object) for guaranteed schema adherence. Anthropic Claude 3.5 Sonnet with XML tags offers excellent structured extraction.",
    dataFlow: `Final Design Brief:
{
  "product_type": "AI SaaS Dashboard Template",
  "target_market": "AI Startups & DevTool companies",
  "style": "glassmorphic dark mode with subtle gradients",
  "sections": ["sidebar_nav","hero_metrics","chart_panel","ai_feed"],
  "animation_type": "staggered fade-in with counter animations",
  "demand_score": 0.82,
  "quality_score": 0.87,
  "provenance": { "trend_source": "reddit_api", ... }
}`
  },
  {
    id: "brief_scorer",
    file: "brief_scorer.py",
    name: "Brief Scorer",
    layer: "Evaluation",
    tag: "eval",
    why: "LLMs can confidently produce structurally valid but semantically weak briefs. A brief may pass schema validation while containing 'hero' as its only section and 'blue' as its only style description — technically valid, practically useless for Phase 3. The Brief Scorer adds a quality dimension to catch these shallow outputs before they consume Phase 3 compute.",
    what: "Computes a weighted sum across four dimensions: pattern clarity (style specificity), component completeness (section count), design complexity (animation type presence), and market demand contribution. Normalizes to a 0.0-1.0 scale and stamps the result as quality_score directly onto the brief dict.",
    inputs: ["Design Brief dict"],
    outputs: ["Same dict with quality_score: float added"],
    methods: ["score_brief(brief)"],
    deps: ["None"],
    failures: "Cannot fail — operates on dict field presence/absence with safe defaults.",
    future: "Train a regression model on 'quality_score vs Phase 3 output rating' pairs collected during production. After 500+ runs the model will outperform heuristic rules at predicting which briefs produce premium templates.",
    alternatives: "Use an LLM as a judge (meta-evaluation): prompt GPT-4o to rate the brief quality 1-10. More expensive but semantically richer than algorithmic scoring.",
    dataFlow: `Scoring Factors:
  style_score   = 0.30 if style is specific
  section_score = 0.30 if len(sections) >= 3
  anim_score    = 0.20 if animation_type != "none"
  demand_score  = demand * 0.20 contribution
  unique_bonus  = 0.0 - 0.20 based on string richness
  ─────────────────────────────────────────
  final quality_score = min(sum, 1.0)`
  },
  {
    id: "generator_validator",
    file: "generator_validator.py",
    name: "Generator Validator",
    layer: "Evaluation",
    tag: "eval",
    why: "Phase 3 (the Code Generator) is the most expensive component in the entire system — it consumes significant LLM tokens, compute, and time. Letting a malformed brief reach Phase 3 wastes all of that. The Generator Validator is the 'circuit breaker' preventing bad inputs from propagating downstream. This single class protects all Phase 3 spending.",
    what: "Performs a final pre-flight compatibility check verifying the brief has non-empty sections, a defined style, target_market context, and a quality_score above the minimum threshold (default 0.6). Returns a (bool, reason_string) tuple. On failure, raises an exception that triggers pipeline retry.",
    inputs: ["Scored Design Brief"],
    outputs: ["(True, 'Compatible') or (False, error_message)"],
    methods: ["is_compatible(brief)"],
    deps: ["None"],
    failures: "The validator itself cannot fail — it inspects dict fields with safe .get() defaults.",
    future: "Define a strict Pydantic v2 model as the Brief schema and validate against it directly — providing field-level error messages. Add a schema_version check ensuring Phase 3 always receives briefs in the schema version it was compiled against.",
    alternatives: "JSON Schema + jsonschema library validation. Pydantic model validation with detailed error reporting. Deep validation using Cerberus library for complex rule sets.",
    dataFlow: `Validation Rules:
  ✓ sections must be non-empty list
  ✓ style must be truthy string
  ✓ target_market must exist
  ✓ quality_score must be >= 0.6
  → All pass: return (True, "Compatible")
  → Any fail: raise Exception → pipeline retry`
  },
  {
    id: "reputation_scorer",
    file: "reputation_scorer.py",
    name: "Reputation Scorer",
    layer: "Evaluation",
    tag: "eval",
    why: "A Pinterest 'repost' of a design is fundamentally different from the original live product itself. Pinterest images are often aspirational designs that were never shipped. A live product website represents actual shipped, validated, revenue-generating UI. The Reputation Scorer injects this real-world signal quality distinction directly into the opportunity math.",
    what: "Inspects the source URL string of the scraped design to classify the content origin. Returns a reputation float that is recorded in the brief's provenance block and fed into the opportunity ranking formula as a quality multiplier.",
    inputs: ["source_url string, metadata_source string"],
    outputs: ["reputation_score: float (0.6 - 1.0)"],
    methods: ["get_source_score(source_url, metadata_source)"],
    deps: ["None"],
    failures: "Returns 1.0 (live site score) as the safe default for any unrecognized source, erring on the side of trust.",
    future: "Build a Domain Authority integration (Moz API / Ahrefs) to score live sites by actual web authority instead of flat 1.0. Add verified design system databases (Material, Apple HIG) as gold-standard sources with 1.2x bonus multipliers.",
    alternatives: "Use ML-based URL classification with a pre-trained website category classifier. Integrate Common Crawl metadata to verify domain age + traffic as additional quality signals.",
    dataFlow: `Source Score Mapping:
  live product site  → 1.0
  hacker_news post   → 0.9
  dribbble shot      → 0.8
  reddit reference   → 0.7
  pinterest repost   → 0.6
  default unknown    → 1.0`
  },
  {
    id: "deduplication_engine",
    file: "deduplication_engine.py",
    name: "Deduplication Engine",
    layer: "Evaluation",
    tag: "eval",
    why: "Without deduplication, the same trending design would be scraped, analyzed, and stored on every pipeline run — burning API quota, inflating storage, and generating duplicate briefs for Phase 3. Over time this compounds: 100 runs could produce 98 identical briefs from the same Dribbble front page. Deduplication keeps the dataset clean and the metrics honest.",
    what: "Generates a deterministic MD5 hash from a sorted string representation of the dictionary content (excluding timestamps). Maintains an in-memory set of seen hashes. Returns True (is_duplicate) if the hash exists — the agent skips the scrape_success metric increment and logs a warning instead.",
    inputs: ["Any dictionary object"],
    outputs: ["Boolean: is_duplicate"],
    methods: ["generate_hash(item)", "is_duplicate(item)", "reset()"],
    deps: ["hashlib"],
    failures: "The in-memory set resets on process restart — acceptable for a single-run pipeline. Does not persist cross-run deduplication.",
    future: "Persist the seen_hashes set to a local Redis instance (TTL: 7 days) to enable cross-run deduplication. Use perceptual hashing (pHash) on actual image files to detect visually similar designs even when the metadata differs.",
    alternatives: "Bloom filters offer O(1) membership testing with minimal memory — ideal for high-volume deduplication at 1M+ items. MinHash LSH (Locality Sensitive Hashing) for near-duplicate detection across similar (not identical) designs.",
    dataFlow: `Hash Generation:
  input_dict = {"source": "dribbble", "title": "Dark Dashboard"}
  sorted_repr = str(sorted values)
  md5_hash = MD5(sorted_repr.encode('utf-8'))
  → "a7b3f9c1..." already in seen_hashes → True (skip)`
  },
  {
    id: "dataset_manager",
    file: "dataset_manager.py",
    name: "Dataset Manager",
    layer: "Storage",
    tag: "store",
    why: "A pipeline that runs continuously will accumulate thousands of PNG screenshots and JSON blobs. Without lifecycle management, disk usage grows unboundedly — a critical production failure mode. The Dataset Manager is the 'janitor' that runs at every pipeline start, silently maintaining the system's environmental hygiene.",
    what: "Scans `storage/design_images/` for files older than `max_days` (default 30) or in excess of `max_images` (default 100). Moves qualifying files to `storage/archive/` using shutil.move (zero file loss). Directories `storage/archive/` and `storage/compressed/` are created automatically.",
    inputs: ["storage/ directory tree", "max_days, max_images thresholds"],
    outputs: ["Files moved to archive/, log messages"],
    methods: ["enforce_retention_policy()", "_archive_old_images()", "_limit_stored_images()"],
    deps: ["os", "shutil", "time"],
    failures: "File permission errors or locked files are not caught — this is a deliberate choice to surface infrastructure problems early.",
    future: "Add gzip/zstd compression before archiving (PIL + zstd). Implement tiered storage: local disk → S3-compatible object storage (MinIO or AWS S3) → Glacier for 90+ day assets. Add storage telemetry to Prometheus metrics.",
    alternatives: "Use a dedicated object store from day one (MinIO is free, S3-compatible). Cloudflare R2 offers zero egress costs for image CDN delivery — important when Phase 3 needs to serve screenshots.",
    dataFlow: `Retention Logic:
  for each image file in storage/design_images/:
    if age > max_days or total_count > max_images:
      shutil.move(file → storage/archive/)
      log: "Archived: file.png"`
  },
  {
    id: "structured_pattern_library",
    file: "structured_pattern_library.py",
    name: "Pattern Library",
    layer: "Storage",
    tag: "store",
    why: "Patterns extracted in one pipeline run should be available as building blocks in future runs — not regenerated from scratch each time. The Pattern Library builds a compounding knowledge base of validated UI component structures. Over time, it becomes the 'component catalog' from which Phase 3 picks pre-validated layout patterns instead of generating them blind.",
    what: "Organizes extracted patterns into category-specific JSON files within the `patterns/` directory. Each category file (hero_patterns.json, dashboard_patterns.json, etc.) accumulates entries over pipeline runs, building a rich structural repository.",
    inputs: ["UI Pattern Object", "category string (e.g., 'glassmorphic_dark')"],
    outputs: ["patterns/{category}_patterns.json"],
    methods: ["save_pattern(category, pattern_data)", "get_patterns(category)"],
    deps: ["os", "json"],
    failures: "JSON parse errors on existing files default to empty list, preventing cascading failures.",
    future: "Index all patterns in a vector database (Qdrant/Weaviate) enabling semantic search: 'find patterns similar to glassmorphic SaaS with sidebar nav'. Add versioning to patterns so Phase 3 can request 'pattern_version >= 2' to avoid deprecated structures.",
    alternatives: "SQLite with FTS5 for full-text pattern search. Airtable API as a visual pattern management interface where designers can manually curate and tag patterns.",
    dataFlow: `Pattern Library Entry:
{
  "pattern_name": "glassmorphic_pricing_card",
  "components": ["plan_selector","price_label","cta_button"],
  "layout": "3_column_card_grid",
  "style": "glassmorphic_dark",
  "source_run": "pipeline_id_f82bac..."
}`
  },
  {
    id: "metadata_store",
    file: "metadata_store.py",
    name: "Metadata Store",
    layer: "Storage",
    tag: "store",
    why: "Every artifact produced by the pipeline — trends, patterns, demand scores, briefs — needs a persistent home that survives server restarts. The Metadata Store is the system's memory. Without it, every pipeline run would be stateless and the system could not be debugged, audited, or resumed after failure.",
    what: "A flat-file JSON database that reads and writes `market_data.json` atomically. Maintains five collections: trends, design_references, ui_patterns, demand_scores, design_briefs. Enforces schema_version '1.0' on every write enabling future migrations.",
    inputs: ["Any pipeline state object"],
    outputs: ["market_data.json (persisted JSON)"],
    methods: ["save_trend()", "save_design_brief()", "get_trends()", "get_design_briefs()", "_read_db()", "_write_db()"],
    deps: ["json", "os"],
    failures: "File corruption or concurrent write conflicts would cause data loss — the flat-file approach has no ACID guarantees.",
    future: "Migrate to SQLite (with WAL mode) for concurrent read safety. Long-term: PostgreSQL with JSONB columns preserving the flexible schema while adding indexing, full-text search, and connection pooling.",
    alternatives: "TinyDB — a lightweight document database with concurrent access guards, built on top of flat files but with proper locking. SQLite with sqlalchemy is the best pragmatic next step — zero deployment overhead, ACID compliant, and queryable.",
    dataFlow: `market_data.json Schema:
{
  "schema_version": "1.0",
  "trends": [ ... trend objects ... ],
  "design_references": [ ... ],
  "ui_patterns": [ ... ],
  "demand_scores": [ ... ],
  "design_briefs": [ ... final briefs ... ]
}`
  },
  {
    id: "image_storage",
    file: "image_storage.py",
    name: "Image Storage",
    layer: "Storage",
    tag: "store",
    why: "Image URLs from Dribbble or Pinterest expire within hours — CDN tokens are temporary. If we only store the URL, the reference is useless next week. Image Storage captures the metadata contract between the URL (scraped today), the local disk path (where it would be saved), and the unique ID — creating a durable, queryable reference index.",
    what: "Maintains `storage/design_images/index.json` as an array of image metadata objects. Assigns each image a UUID-based image_id. Currently tracks metadata only — the actual file download would be added by extended scraper logic using the stored original_url.",
    inputs: ["image_url string", "source string"],
    outputs: ["image_metadata dict + index.json entry"],
    methods: ["store_image_metadata()", "get_all_images()"],
    deps: ["os", "uuid", "json"],
    failures: "Thread-safe only for single-process execution. Concurrent writes would cause index.json corruption.",
    future: "Add actual image download + local save using httpx async. Integrate PIL for image validation (verify it's actually an image), cropping, and WEBP conversion for 60% size reduction. Connect to S3 for durable storage with pre-signed URL generation.",
    alternatives: "SQLite BLOB storage for images < 1MB. AWS S3 + DynamoDB metadata index for production scale. Cloudinary for automatic image optimization and CDN delivery.",
    dataFlow: `Image Index Entry:
{
  "image_id": "design_a3f8bc12",
  "source": "dribbble",
  "file_path": "storage/design_images/design_a3f8bc12.png",
  "original_url": "https://cdn.dribbble.com/..."
}`
  },
  {
    id: "state_tracker",
    file: "state_tracker.py",
    name: "State Tracker",
    layer: "Storage",
    tag: "store",
    why: "Without state tracking, a failed pipeline run at stage 7 (after 3 minutes of scraping and LLM calls) requires a full restart from stage 1. State Tracker enables forensic debugging ('which stage failed?'), resume-from-checkpoint capability ('skip completed stages'), and production monitoring ('how many pipelines succeeded today?').",
    what: "Persists pipeline execution state to `pipeline_states.json` as a dictionary keyed by pipeline_id. Tracks current_stage, completed_stages[], status, start_time, end_time, and errors[]. Updated at every major stage transition by the MarketPipeline orchestrator.",
    inputs: ["pipeline_id", "stage transitions", "error strings"],
    outputs: ["pipeline_states.json"],
    methods: ["create_pipeline()", "update_stage()", "complete_pipeline()", "fail_pipeline()", "get_pipeline()"],
    deps: ["json", "os", "time"],
    failures: "No file locking — concurrent pipeline writes would corrupt the JSON file.",
    future: "Replace JSON flat-file with Redis (HASH type per pipeline_id, TTL: 7 days). Add Prometheus gauge metric for 'pipelines_in_flight'. Build a simple REST API endpoint GET /pipelines/{id} for live monitoring from a dashboard.",
    alternatives: "Celery + Redis task state tracking (mature, production-proven). Prefect or Airflow for full orchestration state management with UI, retry policies, and alerting built-in.",
    dataFlow: `Pipeline State Object:
{
  "pipeline_id": "f82bac1a-...",
  "current_stage": "design_brief_generation",
  "completed_stages": ["started","trend_collection","design_scraping"],
  "status": "running",
  "start_time": 1741879200.0,
  "end_time": null,
  "errors": []
}`
  },
  {
    id: "scheduler",
    file: "scheduler.py",
    name: "Scheduler",
    layer: "Orchestration",
    tag: "core",
    why: "A market intelligence system that only runs when manually triggered is not intelligence — it is a script. The Scheduler transforms the system into continuous, autonomous market monitoring that discovers new trends, scrapes new references, and generates updated briefs every 12 hours without human intervention. This is what makes the factory truly hands-off.",
    what: "Provides scaffolding for integrating with FastAPI's lifecycle events using fastapi-utils periodic tasks. The automated_scan_job function runs MarketPipeline asynchronously on a configured interval. Currently structured as a service hook — not yet wired into app/main.py.",
    inputs: ["Timer config (seconds interval)", "FastAPI app instance"],
    outputs: ["Triggered pipeline execution"],
    methods: ["automated_scan_job()", "scheduler.setup_scheduling(app)"],
    deps: ["fastapi_utils", "asyncio", "market_pipeline"],
    failures: "If a scheduled run fails, it logs the error and the next scheduled run attempts fresh. No duplicate-run prevention yet.",
    future: "Replace fastapi-utils with Celery Beat + Redis for production scheduling with distributed task queues, task deduplication, and retry policies. Add dynamic scheduling: run hourly when trending topics spike, slow to 12h during low-signal periods.",
    alternatives: "APScheduler for lightweight in-process scheduling. Celery Beat for distributed worker queues. Cloud-native: AWS EventBridge + Lambda for completely serverless triggering. GitHub Actions cron jobs for zero-infrastructure operation.",
    dataFlow: `Scheduling Flow:
  FastAPI startup → register @repeat_every(seconds=43200)
  → automated_scan_job() fires every 12 hours
  → MarketPipeline().run("Automated Scheduled Run")
  → Results persisted to market_data.json
  → Next cycle begins`
  },
  {
    id: "template_generator_agent",
    file: "agents/template_generator_agent.py",
    name: "Template Generator Agent",
    layer: "Phase 3 · Generation",
    tag: "core",
    why: "Phase 2 produces Design Briefs — structured JSON specifications. But specifications alone don't ship products. The Template Generator Agent is the system's 'robot programmer' — it takes a brief and physically outputs working React/Tailwind code files. This is the transition from intelligence to production.",
    what: "Orchestrates a 9-step generation pipeline: Brief Parsing → Project Scaffolding → Style Generation → Layout Building → Component Generation → Asset Creation → Code Validation → Preview Building → Packaging. Each step is a dedicated module in template_generator/. The agent extends BaseAgent and emits events at every stage.",
    inputs: ["Design Brief JSON (from market_data.json)", "Output directory path"],
    outputs: ["Complete Vite+React+Tailwind project", ".zip archive", "template_registry.json entry"],
    methods: ["run(task)", "parse → scaffold → style → layout → components → assets → validate → preview → package"],
    deps: ["template_generator.*", "BaseAgent", "event_bus", "metrics"],
    failures: "Each stage has try/except with descriptive error messages. Validation catches broken templates before packaging. Preview builder has graceful fallback if Node.js is unavailable.",
    future: "Use LLaMA to generate richer component content (headlines, features) instead of placeholder text. Add multi-template batch generation. Integrate Figma export for pixel-perfect components.",
    alternatives: "v0.dev API for AI code generation. Vercel's AI SDK for component generation. Direct GPT-4o code generation with structured outputs.",
    dataFlow: `Template Generation Pipeline:
  Brief → BriefParser → spec
  spec → ProjectBuilder → scaffold
  spec → StyleGenerator → tailwind.config + CSS
  spec → LayoutBuilder → layout.json
  layout → ComponentGenerator → JSX files
  spec → AssetManager → SVG icons
  project → CodeValidator → validation report
  project → PreviewBuilder → screenshot
  project → TemplatePackager → .zip + registry`
  },
  {
    id: "llm_gateway",
    file: "core/llm_gateway.py",
    name: "Dual-LLM Gateway",
    layer: "Core · AI",
    tag: "core",
    why: "Relying solely on Gemini means a single quota exhaustion stops the entire system. Relying solely on local LLaMA means lower quality output. The Dual-LLM Gateway gives the system TWO brains — a fast local model for drafts and validation, and a powerful cloud model for refinement — with automatic mutual fallback. This eliminates single-point-of-failure AI dependency.",
    what: "Routes requests between LLaMA 3.2 3B (local, via Ollama, CPU-only) and Gemini 2.5 Pro (cloud, via Google API) using task-type routing rules. Supports 3 modes: LOCAL only, CLOUD only, DUAL (Draft-Refine). In DUAL mode, LLaMA produces a fast JSON draft (~13s), then Gemini refines it. If either provider fails, the other is used automatically.",
    inputs: ["prompt", "task_type", "provider override", "json_mode flag"],
    outputs: ["{ result, provider_used, llama_draft, gemini_refined, time_seconds }"],
    methods: ["query()", "_llama_query()", "_gemini_query()", "_dual_query()", "_auto_route()", "get_stats()"],
    deps: ["ollama", "google.generativeai", "app.config.settings"],
    failures: "LLaMA OOM (model too large for available RAM) returns graceful error. Gemini 429 quota errors fall back to LLaMA-only output. Both failing raises RuntimeError caught by pipeline retry loop.",
    future: "Add streaming support for real-time token output. Integrate more local models (Qwen, Phi-3). Add response caching to avoid re-running identical prompts. Build A/B testing framework to measure quality difference between providers.",
    alternatives: "LiteLLM for unified API across 100+ LLM providers. LangChain router chains for complex multi-model orchestration. Ollama + llama.cpp for maximum local performance tuning.",
    dataFlow: `Task Routing Rules:
  trend_analysis    → GEMINI_CLOUD  (needs vision)
  brief_generation  → DUAL          (draft + refine)
  code_review       → LLAMA_LOCAL   (fast, free)
  section_planning  → LLAMA_LOCAL   (structured JSON)
  style_suggestion  → DUAL          (best of both)
  content_writing   → DUAL          (speed + quality)
  validation        → LLAMA_LOCAL   (speed-critical)
  general           → AUTO          (pick by availability)`
  },
  {
    id: "component_generator",
    file: "template_generator/component_generator.py",
    name: "Component Generator",
    layer: "Phase 3 · Generation",
    tag: "core",
    why: "The heart of Phase 3 — translates abstract section names into physical React JSX code. Without it, the system produces specifications but never actual code. This module is what makes MCP Brain a product factory rather than a research tool.",
    what: "Contains JSX blueprints for common section types (hero, features, pricing, testimonials, CTA, footer, generic). Given a layout spec, it selects the appropriate blueprint, applies style/animation presets (Tailwind classes, Framer Motion attributes), and writes individual .jsx component files plus a main LandingPage.jsx that imports and composes them all.",
    inputs: ["Layout JSON (section order + config)", "Template spec (style preset, animation preset)", "Project directory path"],
    outputs: ["src/components/*.jsx files", "src/pages/LandingPage.jsx"],
    methods: ["generate(layout, spec, project_dir)", "_get_blueprint(section_type)", "_apply_style_classes()", "_apply_animations()"],
    deps: ["os", "json", "re"],
    failures: "Unknown section types fall back to a generic blueprint with heading + paragraph. Empty layouts generate a minimal single-section page.",
    future: "Use LLaMA to generate section-specific content (headlines, feature descriptions) instead of placeholder text. Add component variant system (dark/light/neon themes per component). Generate Storybook stories alongside components.",
    alternatives: "AI-based code generation (GPT-4o, Claude) for more creative components. Shadcn/ui component library integration for pre-built primitives. AST-based code generation for guaranteed syntactic correctness.",
    dataFlow: `Component Generation:
  layout.json sections: [hero, features, pricing, ...]
       ↓
  For each section:
    1. Match blueprint: hero → HeroSection.jsx
    2. Apply style: dark_glassmorphic → bg-gray-950, glass-card
    3. Apply animation: scroll_reveal → Framer whileInView
    4. Write file: src/components/HeroSection.jsx
       ↓
  Generate LandingPage.jsx importing all components`
  }
];
