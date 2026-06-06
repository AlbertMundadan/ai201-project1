# The Unofficial UCONN Housing Guide — Project 1
Housing guide using a RAG pipeline for cited LLM responses. 

## Domain
The domain of knowledge this system will cover is UCONN Storrs on-campus housing information. This knowledge is not typically easily accessible because it is fragmentted in various location and some information is stored in long contracts that are difficult to read. Furthermore, student's opinions are not published by the university and must be obtained from other sources. This includes qualititative information that would not be reported by the university like quietness, comfort, cleanliness, etc.  

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 |UCONN Housing Contract | PDF |https://campushousing.media.uconn.edu/wp-content/uploads/sites/3384/2026/05/2026-2027-Housing-Contract-draft-4.29.26.pdf |
| 2 |UCONN Housing Rates |Website |https://campushousing.uconn.edu/manage-housing/room-rates/ |
| 3 |UCONN Resident Requirements | Website |https://campushousing.uconn.edu/living-on-campus/policies/residency-requirement-information/ |
| 4 | Unofficial Dorm Rankings 1|Website |https://www.ratemydorm.com/dorms-ranked/university-of-connecticut |
| 5 |Unoffical Dorm Rankings 2  |Website |https://prked.com/post/best-university-of-connecticut-dorms |
| 6 |UCONN Housing FAQ |Website |https://campushousing.uconn.edu/frequently-asked-questions/ |
| 7 |UCONN Housing Dates |Website |https://campushousing.uconn.edu/manage-housing/important-dates/ |
| 8 |Unoffical Dorm Guide |PDF | https://docs.google.com/document/d/1CXZzsvqpiB5_siL-akbl4KZ99m9aTGLSgaLiTpVDjRk/edit?tab=t.0|
| 9 |UCONN Amenities by Area|Website |https://campushousing.uconn.edu/living-on-campus/amenities-by-area/ |
| 10 |UCONN Dorm Key and Card Access |Website |https://campushousing.uconn.edu/keys-and-card-access/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
