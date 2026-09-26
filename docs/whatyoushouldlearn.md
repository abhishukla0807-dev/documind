**Task:** DocuMind — detailed explanation + concept list

---

## 1. What it does

User GitHub repo URL deta hai → system code ingest karta hai → user natural language me sawal puchta hai → agent relevant code dhundhke answer deta hai **with file path + line numbers**.

```
Q: "Login flow kaise kaam karta hai?"
A: "JWT AuthFilter.java (L22-58) me token validate hota hai,
    phir UserService.java (L40) user load karta hai."
   Sources: [AuthFilter.java] [UserService.java]
```

---

## 2. Architecture

```
┌──────────┐   REST    ┌─────────────────┐   REST    ┌──────────────────┐
│ R  │ ◄──────── │  (Orchestraeact UI │ ────────► │  Spring Boot    │ ────────► │ Python AI Service│
│ (chat) tor) │ ◄──────── │ FastAPI+LangGraph│
└──────────┘           └───────┬─────────┘           └────────┬─────────┘
                               │                              │
                        ┌──────▼──────┐               ┌───────▼────────┐
                        │   Pgsql     │               │  Vector DB     │
                        │ users, repo,│               │ Qdrant/pgvector│
                        │ chat history│               └────────────────┘
                        └─────────────┘                       │
                               │                       ┌──────▼──────┐
                          JGit clone                   │ LLM+Embedder│
                          → local disk                 │ Ollama/OpenAI│
                                                       └─────────────┘
```

---

## 3. Two Pipelines

### A) Ingestion (one-time per repo)

```
Repo URL → JGit clone → filter files → send to AI svc
        → code-aware chunking → embeddings → store in Vector DB
        → status = READY (saved in MySQL)
```

| Step | Detail |
|---|---|
| Clone | Spring uses JGit, saves in `/repos/{id}` |
| Filter | Skip `node_modules`, `target`, binaries, `.git` |
| Chunk | Split by class/method (not blind 500 chars) |
| Metadata | `{file, start_line, end_line, language, repo_id}` |
| Embed | Each chunk → vector (768/1536 dim) |
| Store 

### B) Query (every question)

```
Question → Spring (auth, history) → AI svc → LangGraph agent → answer + sources
```

---

## 4. LangGraph Agent (heart of project)

```
                ┌─────────┐
   question ──► │ Router  │
                └────┬────┘
        needs code?  │  general Q?
          ┌──────────┴──────────┐
          ▼                     ▼
    ┌──────────┐         ┌────────────┐
    │ Retrieve │         │Direct Answer│
    └────┬─────┘         └────────────┘
         ▼
    ┌──────────┐   irrelevant   ┌──────────────┐
    │Grade Docs│ ─────────────► │ Rewrite Query│──┐
    └────┬─────┘                └──────────────┘  │
         │ relevant                     ▲──────────┘ (max 2 loops)
         ▼
    ┌──────────┐
    │ Generate │ ──► answer + citations
    └──────────┘
```

**State object (TypedDict):**

```python
class AgentState(TypedDict):
    question: str
    rewritten_q: str
    docs: list[Document]
    answer: str
    loop_count: int
    chat_history: list
```

| Node | Job |
|---|---|
| Router | LLM decides: retrieval needed or not |
| Retrieve | Top-k similarity search + metadata filter (repo_id) |
| Grade | LLM scores each chunk: relevant yes/no |
| Rewrite | Bad results → improve query, retry |
| Generate | Answer using only good chunks + cite file:line |

---

## 5. Spring Boot Side (Spring Core focus)

```
com.documind
├── controller     → RepoController, ChatController
├── service        → RepoService, IngestionService, ChatService
├── client         → AiServiceClient (WebClient)
├── git            → GitCloneService (JGit)
├── repository     → JPA repos
├── config         → BeanConfig, SecurityConfig, CacheConfig
├── aspect         → LoggingAspect, TimingAspect (AOP)
└── entity         → User, Repo, ChatSession, Message
```

**Spring Core concepts applied:**
- IoC container + DI (constructor injection of `AiServiceClient`)
- `@Configuration` + `@Bean` (WebClient, JGit config)
- Bean scopes (singleton services, prototype for clone tasks)
- `@Profile` (dev = Ollama, prod = OpenAI)
- `@ConfigurationProperties` (AI service URL, vector settings)
- AOP (log every AI call latency)
- `@Async` + `ApplicationEvent` (async ingestion, `RepoIndexedEvent`)
- `@Cacheable` (repeat questions)
- Global exception handling (`@ControllerAdvice`)

---

## 6. Data Model (MySQL)

| Table | Key columns |
|---|---|
| users | id, email, password_hash |
| repos | id, user_id, url, status (CLONING/INDEXING/READY/FAILED) |
| chat_sessions | id, repo_id, created_at |
| messages | id, session_id, role, content, sources_json |

---

## 7. API Design

| Endpoint | Purpose |
|---|---|
| `POST /api/repos` | Submit repo URL → start ingestion |
| `GET /api/repos/{id}/status` | Poll indexing progress |
| `POST /api/chat/{repoId}` | Ask question |
| `GET /api/chat/{sessionId}` | Chat history |
| `POST /ai/ingest` *(Python)* | Chunk + embed |
| `POST /ai/query` *(Python)* | Run LangGraph |

---

## 8. Concept List

### 🔹 Spring / Java
1. IoC & Dependency Injection
2. Bean lifecycle & scopes
3. `@Configuration` / `@Bean`
4. Profiles & externalized config
5. AOP (aspects, pointcuts)
6. Events (`ApplicationEventPublisher`)
7. `@Async` / thread pools
8. Caching abstraction
9. WebClient (HTTP client)
10. Spring Data JPA
11. Spring Security + JWT
12. Exception handling
13. JGit (Git operations)

### 🔹 RAG
14. Document loading
15. Text/code chunking strategies
16. Chunk overlap & metadata
17. Embeddings
18. Vector similarity (cosine)
19. Top-k retrieval
20. Metadata filtering
21. Hybrid search (vector + BM25)
22. Reranking
23. Prompt grounding + citations
24. Hallucination reduction

### 🔹 LangChain
25. Chat models & embeddings wrappers
26. Prompt templates
27. Output parsers (structured JSON)
28. Retrievers
29. Text splitters (language-aware)
30. Chains (LCEL)
31. Memory / chat history

### 🔹 LangGraph
32. StateGraph & typed state
33. Nodes & edges
34. Conditional routing
35. Cycles / loops (self-correction)
36. Agentic RAG / Corrective RAG
37. Checkpointing (persistent memory)
38. Streaming responses

### 🔹 Vector DB
39. Collections & indexes (HNSW)
40. Upsert / delete by filter
41. Dimension & distance metric
42. Payload storage

### 🔹 System Design
43. Polyglot microservices
44. Async ingestion + status polling
45. REST inter-service communication
46. Docker Compose (Spring + Python + Qdrant + MySQL)

---

## 9. Build Phases

| Phase | Goal |
|---|---|
| 1 | Spring: JGit clone + MySQL + repo API |
| 2 | Python: chunking + embeddings + Qdrant |
| 3 | Basic RAG (retrieve → generate) |
| 4 | LangGraph: router + grade + rewrite loop |
| 5 | Chat history + citations |
| 6 | JWT auth + React UI |
| 7 | Docker Compose + AOP/caching polish |

---

**Next:** Phase 1 se start karein? Project structure + `pom.xml` + JGit clone service code de deta hu.