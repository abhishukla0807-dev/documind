## Phase 3 se pehle padhne wale concepts

**What to learn

---

## 1. RAG fundamentals (agar clear nahi hai)

| Concept | Kyu chahiye |
|---|---|
| Retrieval vs Generation split | Samajhna zaroori — LLM sab kuch "yaad" nahi rakhta, retrieval **external knowledge** deta hai runtime pe |
| Semantic search vs keyword search | Vector similarity kaise keyword-match se alag hai (matlab match karta hai, exact words nahi) |
| Top-k retrieval | "Sabse zyada relevant k chunks" ka concept — kyu 5, kyu na 50 |
| Grounding / hallucination | LLM ko "sirf diye gaye context se answer do" bolna kyu zaroori hai |

**Ek line summary agar abhi bhi confuse ho:** RAG = "LLM ko poori codebase yaad nahi, isliye pehle relevant tukde dhundo (retrieval), phir LLM ko wahi tukde dikha ke answer banwao (generation)."

---

## 2. Vector similarity (thoda technical, but zaroori)

| Concept | Kyu chahiye |
|---|---|
| Cosine similarity | Qdrant search isi metric se "kitna similar hai" measure karta hai — samajhna chahiye ye kya represent karta hai (angle between vectors, 1 = identical direction) |
| Embedding space | Samajhna — similar-meaning text ke vectors "paas-paas" hote hain multi-dimensional space me |
| Asymmetric embeddings (already discuss kiya) | Recap kar lo — `search_query:` vs `search_document:` prefix kyu alag treat hote hain |

**Practical tip:** Isko deeply math se samajhne ki zarurat nahi — bas itna clear ho ki "similarity score jitna high (1 ke paas), utna relevant chunk."

---

## 3. Prompt Engineering (Step 3.2 ke liye critical)

| Concept | Kyu chahiye |
|---|---|
| System prompt vs user prompt | LLM ko "role/instruction" alag se dena (system) vs actual question (user) |
| Few-shot vs zero-shot | Abhi zero-shot use karenge (bina example ke), samajh lo difference |
| Context window | LLM ek limited amount text ek baar me "dekh" sakta hai — isliye top-k limit zaroori hai |
| Grounding instructions | "Answer only from context" jaisi phrases LLM behavior kaise change karti hain |
| Citation prompting | LLM ko structured output format (`[file:line]`) follow karne ko kaise bolte hain |

**Recommend padhna:** Anthropic ka prompt engineering guide (chhota sa) — concepts wahi generic hain, chahe koi bhi LLM ho:
`docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview`

---

## 4. LangChain basics (jo tum already use kar rahe ho, bas naye pieces)

| Concept | Kyu chahiye |
|---|---|
| `ChatOllama` vs `OllamaEmbeddings` | Do alag cheezein — ek text generate karta hai, ek vectors banata hai. Confuse mat hona |
| LangChain `Document` object (already use kar chuke ho) | Recap — `page_content` + `metadata` |
| Prompt templates (`ChatPromptTemplate`) | LangChain ka standard tarika prompts banane ka, agar use karna ho to |
| LCEL (LangChain Expression Language) — optional | Chains ko `|` operator se jodna — abhi zaroori nahi, plain Python functions se bhi kaam chal jayega |

---

## 5. FastAPI concepts (jo shayad Phase 2 me touch nahi hue)

| Concept | Kyu chahiye |
|---|---|
| Async endpoints (`async def`) | Query API bhi async hoga — samajh lo kyu (I/O-bound waits, jaise Ollama/Qdrant calls) |
| Pydantic response models | `QueryResponse` schema — validation + auto-documentation |

---

## 6. Ek important practical concept — Temperature (LLM parameter)

| Concept | Kyu chahiye |
|---|---|
| Temperature 0 vs 1 | 0 = deterministic/factual (RAG ke liye chahiye), 1 = creative/random (chatbot-jaisi baat ke liye). Samajh lo kyu low temperature (0.1-0.2) RAG me sahi hai |

---

## Priority order (agar time kam hai)

| Must-know before starting | Nice-to-know (baad me bhi chalega) |
|---|---|
| RAG fundamentals | LCEL |
| Cosine similarity (conceptually) | Few-shot prompting |
| Grounding + prompt engineering basics | Deep vector-math |
| Temperature parameter | — |

---






















### Phase 3 — Basic RAG: Step-by-Step Roadmap

**Goal:** User question poochta hai → relevant code chunks Qdrant se milte hain → LLM grounded answer deta hai citations ke saath. **Bina LangGraph ke abhi — ye baseline hai.**

```
question → embed (search_query:) → Qdrant top-k search → prompt build → LLM → answer + sources
```

---

## Step 3.1 — Retriever

| Sub-step | Kaam |
|---|---|
| 3.1.a | `retrieval/retriever.py` bana — class `CodeRetriever` |
| 3.1.b | Method: user question lo, `ContextualEmbedder.prepare_query()` se prefix lagao |
| 3.1.c | Prefixed query ko embed karo (`get_embedding_client()` se) |
| 3.1.d | Qdrant `search()` call — `collection_name=repo_{id}`, `top_k` (e.g. 5), similarity score ke saath |
| 3.1.e | Result ko structured format me return karo: `[{content, file_path, start_line, end_line, layer, score}]` |
| 3.1.f | Edge case: collection exist nahi karti (repo kabhi ingest hi nahi hua) → proper exception |

**Done when:** Ek test question do, function relevant chunks + metadata return kare.

---

## Step 3.2 — Prompt Template

| Sub-step | Kaam |
|---|---|
| 3.2.a | `llm/prompts.py` bana |
| 3.2.b | System prompt likho — LLM ko "sirf diye gaye context se answer do, bahar se mat banao" instruction |
| 3.2.c | Context-formatting function — retrieved chunks ko readable text me convert karo (`[file:line]` format ke saath prefix) |
| 3.2.d | Final prompt assemble — system instruction + formatted context + user question |
| 3.2.e | Citation instruction explicitly likho — "answer ke andar `[filename:start-end]` format me cite karo" |

**Done when:** Function chunks + question lekar ek complete prompt string/messages list de.

---

## Step 3.3 — Generation LLM Provider

| Sub-step | Kaam |
|---|---|
| 3.3.a | `llm/generation_provider.py` bana |
| 3.3.b | `ChatOllama` (LangChain) client setup — model=`qwen2.5-coder:7b` |
| 3.3.c | `@lru_cache` se cached client (jaisa embedding provider me kiya tha) |
| 3.3.d | Temperature/settings decide (RAG ke liye low temperature — factual rehna chahiye, creative nahi) |
| 3.3.e | Error handling — Ollama down hone pe `GenerationServiceUnavailableError` (naya custom exception) |

**Done when:** Ek prompt do, function LLM ka text response return kare.

---

## Step 3.4 — Query Orchestration API

| Sub-step | Kaam |
|---|---|
| 3.4.a | `schemas.py` me `QueryRequest` (`repo_id`, `question`) aur `QueryResponse` (`answer`, `sources`) add karo |
| 3.4.b | `api/query.py` bana — `POST /ai/query` endpoint |
| 3.4.c | Flow: retriever call karo → chunks milein → prompt build karo → LLM call karo → response assemble karo |
| 3.4.d | Sources list banao response me — sirf unique files (duplicate `file:line` avoid karo agar same file multiple chunks se aaya) |
| 3.4.e | Error handling — koi bhi step fail ho (retrieval, generation) to specific HTTP status |

**Done when:** Postman/PowerShell se `POST /ai/query {repo_id, question}` call karo, structured answer mile.

---

## Step 3.5 — Response Shape Finalize

```json
{
  "answer": "Validation errors are handled in [GlobalExceptionHandler.java:35-42]...",
  "sources": [
    {
      "file_path": "com/documind/exception/GlobalExceptionHandler.java",
      "start_line": 35,
      "end_line": 42,
      "layer": "exception handling"
    }
  ]
}
```

**Design decision to make:** LLM khud citation text me likhega (`[file:line]`), ya hum sirf structured `sources` array bhejenge aur citation-formatting frontend/Spring pe chhodenge? **Recommend:** Dono — LLM ko bolo answer ke andar bhi cite kare (readability ke liye), aur structured `sources` array bhi alag se do (programmatic use ke liye, jaisa UI mockup me citation-chip banaya tha).

---

## Step 3.6 — Testing

| Test | Kya verify karna hai |
|---|---|
| 3.6.a | Simple factual question — "Where is X handled?" → sahi file cite ho |
| 3.6.b | Vague/broad question — "How does this project work?" → reasonable generic answer (multiple chunks se) |
| 3.6.c | Out-of-scope question — "What's the capital of France?" → LLM ko bolna chahiye "context me nahi mila" (hallucination test) |
| 3.6.d | Non-existent repo_id → proper 404 |
| 3.6.e | Empty/very short question → validation |
| 3.6.f | Response time measure karo — 7B model CPU pe kitna time leta hai (baseline latency samajhne ke liye, Phase 4 comparison ke liye useful) |

---

## Dependency order

```
3.1 (retriever) ──► 3.2 (prompt) ──► 3.3 (LLM provider)
                                            │
                                            ▼
                                   3.4 (orchestration API)
                                            │
                                            ▼
                                   3.5 (response shape)
                                            │
                                            ▼
                                   3.6 (testing)
```

3.1, 3.2, 3.3 — teeno **independent** hain (parallel bhi bana sakte ho), 3.4 unko jodta hai.

---

## Key design decisions (finalize karna hai chalne se pehle)

| Decision | Options | Recommend |
|---|---|---|
| `top_k` (kitne chunks retrieve karein) | 3, 5, 8 | **5** — enough context, prompt zyada bada nahi hoga |
| Similarity threshold | Filter low-score chunks ya nahi | **Haan** — score < 0.5 (approx) wale chunks discard karo, irrelevant noise avoid |
| LLM temperature | 0 to 1 | **0.1-0.2** — factual/deterministic rehna chahiye RAG me |
| "No answer found" handling | LLM khud bole vs code se detect | **LLM ko prompt me explicitly instruct karo** — "agar context insufficient hai to bolo 'I don't have enough information'" |

---

