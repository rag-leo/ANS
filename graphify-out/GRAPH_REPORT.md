# Graph Report - ANS  (2026-09-03)

## Corpus Check
- Corpus is ~27,048 words - fits in a single context window. You may not need a graph.

## Summary
- 466 nodes · 947 edges · 35 communities
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 72 edges (avg confidence: 0.94)
- Token cost: 104,391 input · 0 output

## Community Hubs (Navigation)
- Scraping Adapters & Logging
- Content Generation Engine
- Source Config Schema
- Ingestion Pipeline & Chunking
- Embedding & Search API
- Agrowon Scraper & Transform
- Evaluation Repository
- Frontend API Client
- DB Migrations & ORM Base
- Generation & Publish API
- App Lifecycle & Health Checks
- App Settings & Config
- Source Config Rationale
- LLM Metadata Service Tests
- Bayer Xivana Article
- Analytics Repository
- Tobacco AI Grading Article
- Request Logging Middleware
- DB Session Management
- Azure OpenAI Connectivity Check
- Root Health Endpoint

## God Nodes (most connected - your core abstractions)
1. `ScraperAdapter` - 25 edges
2. `AgrowonAdapter` - 23 edges
3. `KrishiJagranAdapter` - 23 edges
4. `ETAgricultureAdapter` - 22 edges
5. `ScrapedArticle` - 21 edges
6. `SourceConfig` - 18 edges
7. `EmbeddingService` - 18 edges
8. `_process_article()` - 16 edges
9. `get_logger()` - 15 edges
10. `RobotsChecker` - 15 edges

## Surprising Connections (you probably didn't know these)
- `test_rate_limit_is_read_from_config_not_hardcoded()` --uses--> `AgrowonAdapter`  [INFERRED]
  tests/test_rate_limiting_runtime.py → backend/ingestion/adapters/agrowon.py
- `test_rate_limit_is_read_from_config_not_hardcoded()` --uses--> `ETAgricultureAdapter`  [INFERRED]
  tests/test_rate_limiting_runtime.py → backend/ingestion/adapters/et_agriculture.py
- `test_load_all_adapters_registers_all_three_sources()` --uses--> `KrishiJagranAdapter`  [INFERRED]
  tests/test_adapter_registry.py → backend/ingestion/adapters/krishi_jagran.py
- `test_imports()` --uses--> `AgrowonScraper`  [INFERRED]
  tests/test_ingestion_structure.py → backend/ingestion/agrowon_scraper.py
- `test_imports()` --uses--> `EmbeddingService`  [INFERRED]
  tests/test_architecture.py → backend/services/embedding_service.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Shared Source Adapter Config Schema** — backend_ingestion_configs_agrowon_sourceconfig, backend_ingestion_configs_et_agriculture_sourceconfig, backend_ingestion_configs_krishi_jagran_sourceconfig [INFERRED 0.85]
- **AI Grading Pilot News Event (ET Agriculture)** — tests_fixtures_et_agriculture_ai_grading_tobacco_auctions_tobacco_board, tests_fixtures_et_agriculture_ai_grading_tobacco_auctions_constems_ai, tests_fixtures_et_agriculture_ai_grading_tobacco_auctions_fcv_tobacco, tests_fixtures_et_agriculture_ai_grading_tobacco_auctions_andhra_pradesh, tests_fixtures_et_agriculture_ai_grading_tobacco_auctions_ai_based_grading_pilot [EXTRACTED 1.00]
- **Xivana Smart Fungicide Launch Event (Krishi Jagran)** — tests_fixtures_krishi_jagran_bayer_xivana_smart_bayer, tests_fixtures_krishi_jagran_bayer_xivana_smart_xivana_smart, tests_fixtures_krishi_jagran_bayer_xivana_smart_frac_group_49, tests_fixtures_krishi_jagran_bayer_xivana_smart_downy_mildew, tests_fixtures_krishi_jagran_bayer_xivana_smart_late_blight [EXTRACTED 1.00]

## Communities (35 total, 0 thin omitted)

### Community 0 - "Scraping Adapters & Logging"
Cohesion: 0.05
Nodes (41): ABC, configure_logging(), get_logger(), JsonFormatter, AgrowonAdapter, BeautifulSoup, Agrowon News Scraper, adapter form. Selenium + BeautifulSoup, config-driven via…, Scrolls to trigger lazy-loaded content, stopping as soon as the page stops… (+33 more)

### Community 1 - "Content Generation Engine"
Cohesion: 0.08
Nodes (24): Article, GeneratedContent, AI generated communication content. Supports: - WhatsApp - Push Notification -…, Knowledge Base Articles Stores: - Raw article content - Metadata - Source…, BaseGenerator, NewsletterGenerator, PushGenerator, retry (+16 more)

### Community 2 - "Source Config Schema"
Cohesion: 0.08
Nodes (35): FetchConfig, ListingConfig, load_source_config(), BaseModel, Path, QualityConfig, RateLimitConfig, One listing page to crawl for article links (e.g. a category page). (+27 more)

### Community 3 - "Ingestion Pipeline & Chunking"
Cohesion: 0.10
Nodes (30): _process_article(), Runs a single source end to end, isolated from the other sources: a whole-…, Runs every registered source (see backend.ingestion.adapters.registry) as an…, Runs one scraped article through dedup, chunking, metadata classification,…, run_pipeline(), _run_source(), ArticleChunk, ArticleChunkRepository (+22 more)

### Community 4 - "Embedding & Search API"
Cohesion: 0.09
Nodes (21): generate_embedding(), post, post, search(), EmbeddingRequest, EmbeddingResponse, BaseModel, BaseModel (+13 more)

### Community 5 - "Agrowon Scraper & Transform"
Cohesion: 0.18
Nodes (9): AgrowonScraper, BaseModel, ScrapedArticle, ArticleTransformer, Converts scraped articles into ANIS database models., MetadataService, test_flow(), test_imports() (+1 more)

### Community 6 - "Evaluation Repository"
Cohesion: 0.14
Nodes (12): get_evaluation_by_generation_type(), get_evaluation_by_language(), get_evaluation_summary(), get_lowest_rated_evaluations(), get_test_cases(), get, post, submit_evaluation() (+4 more)

### Community 7 - "Frontend API Client"
Cohesion: 0.10
Nodes (8): generate_embedding(), get_backend_url(), health_check(), Calls the ANIS embedding API., Calls the ANIS health endpoint., Retrieves backend API URL from Streamlit secrets. Falls back to localhost for…, check_backend_health(), Checks if FastAPI backend is reachable. Returns: (is_healthy, error_message)

### Community 8 - "DB Migrations & ORM Base"
Cohesion: 0.17
Nodes (13): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Base, datetime, Naive UTC timestamp for use with non-timezone-aware DateTime columns.…, Base class for all ANIS ORM models. (+5 more)

### Community 9 - "Generation & Publish API"
Cohesion: 0.19
Nodes (14): generate_content(), post, get_history(), publish_content(), get, post, ContentRequest, ContentResponse (+6 more)

### Community 10 - "App Lifecycle & Health Checks"
Cohesion: 0.20
Nodes (12): lifespan(), Application startup and shutdown lifecycle. This is the correct place for: -…, check_api_status(), check_azure_openai(), check_postgresql(), health_check(), get, Basic application health. (+4 more)

### Community 11 - "App Settings & Config"
Cohesion: 0.17
Nodes (8): get_settings(), SQLAlchemy connection string, Centralized application configuration. Configuration priority: 1. Environment…, Cached singleton settings instance. Prevents repeated .env parsing., ALLOWED_ORIGINS as a list, for CORSMiddleware., Settings, BaseSettings, PostgreSQL Connectivity Check Manual script, not part of the automated test…

### Community 12 - "Source Config Rationale"
Cohesion: 0.24
Nodes (11): date_format left unset: Agrowon's datetime attribute is already ISO-8601, Agrowon Source Config, updated_date_pattern left unset: no separate 'updated' text observed on sampled articles, Sitemap listing chosen over category-page scraping (client-side pagination unexposed), ET Agriculture Source Config, Body scoped to <article> tag to exclude footer/sidebar CTA noise, Sitemap crawl capped to recent entries instead of walking full ~19k-URL historical archive, Conservative rate limit due to active Cloudflare WAF fronting the site (+3 more)

### Community 13 - "LLM Metadata Service Tests"
Cohesion: 0.49
Nodes (9): _build_service(), _fake_completion(), test_complete_retries_on_rate_limit_then_succeeds(), test_extract_metadata_calls_the_classification_deployment_not_chat(), test_extract_metadata_drops_crops_outside_the_taxonomy(), test_extract_metadata_falls_back_to_general_for_unknown_category(), test_extract_metadata_falls_back_to_general_on_malformed_json(), test_extract_metadata_falls_back_to_general_when_api_call_fails() (+1 more)

### Community 14 - "Bayer Xivana Article"
Cohesion: 0.48
Nodes (7): Bayer launches Xivana Smart fungicide (article), Bayer, Downy Mildew, FRAC Group 49, KJ Staff (author), Late Blight, Xivana Smart

### Community 15 - "Analytics Repository"
Cohesion: 0.40
Nodes (3): get_summary(), get, AnalyticsRepository

### Community 16 - "Tobacco AI Grading Article"
Cohesion: 0.60
Nodes (6): AI-based Grading Pilot, Andhra Pradesh, AI grading set to reshape tobacco auctions in Andhra Pradesh (article), Constems AI, FCV Tobacco, Tobacco Board

### Community 17 - "Request Logging Middleware"
Cohesion: 0.40
Nodes (5): log_requests(), Logs every incoming request and response. Azure Application Insights can ingest…, middleware, Request, Response

### Community 18 - "DB Session Management"
Cohesion: 0.40
Nodes (3): get_db(), Session, FastAPI dependency. Example: @router.get("/") async def get_items( db: Session…

### Community 19 - "Azure OpenAI Connectivity Check"
Cohesion: 0.50
Nodes (3): check_embedding_connection(), Azure OpenAI Connectivity Check Purpose: - Validate Azure OpenAI configuration…, Checks the Azure OpenAI embedding deployment.

### Community 22 - "Root Health Endpoint"
Cohesion: 0.67
Nodes (3): get, Root endpoint. Useful for quick checks that the application is running., root()

## Knowledge Gaps
- **1 isolated node(s):** `KJ Staff (author)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 153 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_logger()` connect `Scraping Adapters & Logging` to `Content Generation Engine`, `App Lifecycle & Health Checks`, `Ingestion Pipeline & Chunking`, `Agrowon Scraper & Transform`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `ScraperAdapter` connect `Scraping Adapters & Logging` to `Source Config Schema`, `Ingestion Pipeline & Chunking`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `EmbeddingService` connect `Embedding & Search API` to `Content Generation Engine`, `Ingestion Pipeline & Chunking`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `AgrowonAdapter` (e.g. with `SourceConfig` and `RateLimiter`) actually correct?**
  _`AgrowonAdapter` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `KrishiJagranAdapter` (e.g. with `SourceConfig` and `RateLimiter`) actually correct?**
  _`KrishiJagranAdapter` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ETAgricultureAdapter` (e.g. with `SourceConfig` and `RateLimiter`) actually correct?**
  _`ETAgricultureAdapter` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `KJ Staff (author)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._