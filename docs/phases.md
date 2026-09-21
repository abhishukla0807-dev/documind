**Task:** DocuMind — phase-wise development plan

---

## Overview

```
P0 Setup → P1 Spring Core → P2 Ingestion → P3 Basic RAG → P4 LangGraph
   → P5 Chat + Citations → P6 Auth + UI → P7 Polish + Docker
```

| Phase | Name | IDE | Est. time | Output |
|---|---|---|---|---|
| 0 | Setup | Both | 1 day | Env ready, DBs running |
| 1 | Spring backend | IntelliJ | 4-5 days | Repo clone + status API |
| 2 | Ingestion pipeline | PyCharm | 5-6 days | Chunks in Qdrant |
| 3 | Basic RAG | PyCharm | 3-4 days | Retrieve → answer |
| 4 | LangGraph agent | PyCharm | 5-6 days | Self-correcting RAG |
| 5 | Chat + citations | Both | 4-5 days | History + file:line sources |
| 6 | Auth + UI | Both | 5-6 days | JWT + React app |
| 7 | Polish + Docker | Both | 3-4 days | One-command run |

**Total: ~5-6 weeks** (part-time).

---

## Phase 0: Setup

**Goal:** Dono projects skeleton + infra chal rahe.

- [ ] Root repo `documind/` + `.gitignore`
- [ ] Spring Initializr project (IntelliJ)
- [ ] FastAPI skeleton + venv (PyCharm)
- [ ] `docker-compose.yml` (MySQL + Qdrant)
- [ ] Ollama models pull

**Done when:** `GET :8080/health` aur `GET :8001/health` dono 200 dete hain.

---

## Phase 1: Spring backend (Spring Core focus)

**Goal:** Repo submit karo → clone ho → status track ho.

| Task | Concept |
|---|---|
| Entities: `Repo`, `User` | JPA |
| `GitCloneService` | JGit, `@Service`, DI |
| `POST /api/repos`, `GET /api/repos/{id}/status` | REST |
| Async clone | `@Async`, thread pool bean |
| `RepoClonedEvent` | ApplicationEvent |
| `LoggingAspect` | AOP |
| `@ConfigurationProperties` | Externalized config |
| `@ControllerAdvice` | Exception handling |

**Done when:** URL POST karo → `/repos/{id}` folder me code aa jaye, status = `CLONED`.

---

## Phase 2: Ingestion pipeline

**Goal:** Cloned code → chunks → embeddings → Qdrant.

| Task | Concept |
|---|---|
| File filter (skip `node_modules`, binaries) | Preprocessing |
| Language-aware splitter | Chunking |
| Metadata `{file, start_line, end_line}` | Payload |
| Embeddings via Ollama `nomic-embed-text` | Embeddings |
| Qdrant collection per repo | Vector DB |
| `POST /ai/ingest` | FastAPI |
| Spring → Python call via `WebClient` | Inter-service |

**Done when:** Qdrant dashboard (`:6333/dashboard`) me points dikhen with correct metadata.

---

## Phase 3: Basic RAG

**Goal:** Simple retrieve → generate, **bina LangGraph**.

```
question → embed → top-k search → prompt + chunks → LLM → answer
```

| Task | Concept |
|---|---|
| Retriever with `repo_id` filter | Metadata filtering |
| Prompt template (grounded) | Prompt engineering |
| LCEL chain | LangChain |
| `POST /ai/query` | FastAPI |

**Done when:** Sawal puchne par relevant code ke basis pe answer aaye.

**Why separate phase:** baseline banta hai. Phase 4 me compare kar sakte ho ki LangGraph ne kitna improve kiya.

---

## Phase 4: LangGraph agent

**Goal:** Basic RAG → self-correcting agentic RAG.

Build incrementally:

| Step | Add |
|---|---|
| 4a | `AgentState` + Retrieve → Generate (same as P3, but graph) |
| 4b | Router node (retrieval needed?) |
| 4c | Grade node (chunk relevant?) |
| 4d | Rewrite loop (max 2 retries) |
| 4e | Hybrid search (vector + keyword) |

**Done when:** Vague question pe agent query rewrite karke better answer deta hai. Logs me graph path dikhe.

---

## Phase 5: Chat + citations

**Goal:** History + clickable sources.

| Side | Task |
|---|---|
| Spring | `ChatSession`, `Message` entities, `POST /api/chat/{repoId}` |
| Spring | `@Cacheable` for repeat questions |
| Spring | Files API: `GET /api/repos/{id}/files?path=` |
| Python | Return `sources: [{file, from, to}]` |
| Python | LangGraph checkpointer (conversation memory) |

**Done when:** Follow-up question ("aur ye kahan use hota hai?") context samajhta hai, aur response me file:line milti hai.

---

## Phase 6: Auth + UI

**Goal:** Secure + usable app.

| Task | Detail |
|---|---|
| Spring Security + JWT | `/auth/register`, `/auth/login` |
| Repo ownership check | User apni repos hi dekhe |
| React app | Wahi 2-pane design |
| Citation chip → source pane | Already designed in `documind-ui.html` |
| Repo status polling | Every 3s jab tak `READY` |

**Done when:** Register → login → repo add → chat → citation click, poora flow browser se chale.

---

## Phase 7: Polish + Docker

| Task | Detail |
|---|---|
| Dockerfiles (Spring, Python, React) | Multi-stage |
| Full `docker-compose.yml` | 5 services + Ollama |
| Streaming responses (SSE) | Better UX |
| `@Profile` dev/prod | Ollama vs OpenAI |
| README + architecture diagram | Resume ready |
| Basic tests | JUnit + pytest |

**Done when:** Fresh machine pe `docker compose up` se sab chal jaye.

---

## Dependency Map

```
P0 ──► P1 ──┐
  └──► P2 ──┼──► P3 ──► P4 ──► P5 ──► P6 ──► P7
            │
     (P1 aur P2 parallel ho sakte hain)
```

---

## Milestones

| After | You can demo |
|---|---|
| P1 | "Repo clone API working" |
| P3 | "Ask questions about a repo" |
| P4 | "Agent self-corrects bad retrieval" |
| P6 | "Full working app" |
| P7 | "Deployable project" |

---

## Optional Phase 8 (extras)

- Reranker (cross-encoder)
- Multi-repo search
- GitHub webhook → auto re-index on push
- Evaluation (RAGAS metrics)

---

**Next:** Phase 0 checklist ke saath start karein? Root folder structure + `docker-compose.yml` + dono skeletons ka exact code de deta hu.