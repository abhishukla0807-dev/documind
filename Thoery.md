### Step 1.6 — Async Processing (Theory only, code baad me)

---

## Problem samjho pehle

Abhi jo humne banaya (`JGitCloningService`), agar isse seedha controller se call karo:

```
Client → POST /api/repos → clone shuru → ... 5-30 seconds wait ... → response
```

Client (browser/Postman) **poora clone hone tak** response ka wait karega — bade repo ke liye ye 30+ seconds bhi ho sakta hai. HTTP request thread block rehta hai, aur agar 10 log ek saath repo submit karein, server ke saare thread busy ho jayenge sirf cloning me — koi aur request handle nahi hogi.

---

## Solution: Async

```
Client → POST /api/repos → DB me row save (status=PENDING) → turant response (repoId)
                                    │
                                    └──► background thread me clone shuru (status=CLONING → CLONED/FAILED)

Client → GET /api/repos/{id}/status → jab chahe poll karke dekh le progress
```

Request turant return ho jati hai, actual heavy kaam (cloning) alag thread me chalta hai.

---

## Core concepts

### 1. `@EnableAsync`

Spring Boot me by default async support **off** hota hai. Ek jagah (usually main class ya ek `@Configuration` class) pe `@EnableAsync` likhna padta hai — ye Spring ko batata hai: "async annotations ko scan karo aur activate karo."

### 2. `@Async` annotation

Kisi bhi method pe laga do, Spring us method ko **alag thread** me chalayega, caller thread turant aage badh jayega bina wait kiye.

```
Normal method call:  caller ──call()──► method runs ──► caller waits ──► returns
@Async method call:  caller ──call()──► turant return  |  method runs somewhere else in parallel
```

**Important limitation:** `@Async` tabhi kaam karta hai jab method **doosri class se** call ho (Spring proxy ke through). Agar same class ke andar ek method doosre `@Async` method ko call kare, proxy bypass ho jata hai aur async kaam nahi karega — ye ek common beginner mistake hai.

### 3. Thread Pool — kyu zaroori

Bina configuration ke, Spring `@Async` ke liye ek **default simple executor** use karta hai jo har call pe naya thread bana deta hai — unbounded, risky (resource exhaustion ho sakta hai agar 1000 requests aa jayein).

Isliye hum custom `ThreadPoolTaskExecutor` bean banayenge, jisme:

| Setting | Matlab |
|---|---|
| Core pool size | Hamesha itne threads ready rakho |
| Max pool size | Zarurat pe itne tak badha sakte ho |
| Queue capacity | Agar sab threads busy hain, itni requests wait-line me rakho |

Ye ek **bounded resource pool** hai — controlled tarike se concurrent clones handle honge, server crash nahi hoga load me.

### 4. Return type — `void` vs `CompletableFuture`

Do tarike ho sakte hain async method likhne ke:

```java
@Async
void cloneAsync(...)              // fire-and-forget, kuch return nahi
```
ya
```java
@Async
CompletableFuture<Path> cloneAsync(...)   // future me result milega, agar chahiye ho
```

Humare case me: clone hone ke baad hume **status DB me update karna hai**, result seedha caller ko wapas nahi bhejna. Isliye **`void` + andar hi status update logic** likhenge — simpler approach.

---

## Application Events ka connection (Step 1.8 se link)

Async clone complete hone ke baad, ek **event publish** karenge (`RepoClonedEvent`) instead of directly agla kaam call karne ke. Ye Phase 2 (ingestion trigger) ke liye important hoga — abhi bas dhyan rakhna, agle steps me connect hoga:

```
JGitCloningService (clone karta hai)
        │
        ▼
RepoService.cloneAsync() [@Async]
        │  clone success
        ▼
publish RepoClonedEvent
        │
        ▼
(Phase 2 me) IngestionListener isse sunega, chunking shuru karega
```

**Kyu event use karenge, seedha method call nahi:** Loose coupling. `RepoService` ko pata nahi hona chahiye ki clone ke baad "ingestion" naam ki koi cheez hoti hai — wo sirf itna kehta hai "maine clone kar diya", jo bhi sunna chahta hai sun le. Kal agar 2-3 aur cheezein clone ke baad trigger karni ho (jaise notification bhejna), `RepoService` ka code touch nahi karna padega.

---

## SOLID preview for Step 1.6

| Principle | Kaise apply hoga |
|---|---|
| **S**RP | `RepoService` sirf orchestration karega (clone call karo, status update karo) — actual git logic `JGitCloningService` me hi rahega |
| **O**CP (Open-Closed) | Event-based design se naye "listeners" add kar sakte ho bina `RepoService` ko modify kiye — class extension ke liye open, modification ke liye closed |

---

