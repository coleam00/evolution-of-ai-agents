# Research Search Tips & Best Practices

This guide helps you construct effective searches and present research findings clearly.

## Query Construction

### Basic Search Strategies

**Be Specific, Not Broad**
| Instead of... | Try... |
|---------------|--------|
| "AI" | "large language models reasoning" |
| "medicine" | "CRISPR gene therapy cancer" |
| "climate" | "carbon capture industrial emissions" |

**Use Domain Terminology**
Academic papers use technical language. Match it:
| User Says... | Search For... |
|--------------|---------------|
| "brain scans" | "fMRI neuroimaging" |
| "heart disease" | "cardiovascular disease atherosclerosis" |
| "machine learning" | "deep learning neural networks" |

### Advanced Query Techniques

**Phrase Searching**
Use quotes for exact phrases (when supported):
- `"attention is all you need"` - finds exact phrase
- `transformer attention mechanism` - finds papers with all terms

**Combining Concepts**
Include multiple related terms:
- `"large language models" OR "LLMs"`
- `BERT transformer NLP`

**Field-Specific Searches**
Target specific areas with fieldsOfStudy:
- Computer Science papers: `fieldsOfStudy=Computer Science`
- Medical research: `fieldsOfStudy=Medicine`
- Cross-disciplinary: search multiple fields

---

## Filtering Strategies

### By Time Period

| Use Case | Year Parameter |
|----------|----------------|
| Latest research | `year=2024` |
| Recent 3 years | `year=2022-2024` |
| Decade overview | `year=2015-2024` |
| Classic papers | `year=1990-2000` |

### By Impact

**High-Impact Papers**
Use `minCitationCount` to find influential work:
- Seminal papers: `minCitationCount=1000`
- Established work: `minCitationCount=100`
- Notable papers: `minCitationCount=50`
- Recent quality: `minCitationCount=10` (for papers < 2 years old)

**Note**: New papers have few citations. For recent work, lower the threshold or remove it.

### By Publication Type

| Type | Description |
|------|-------------|
| `JournalArticle` | Peer-reviewed journal papers |
| `Conference` | Conference proceedings |
| `Review` | Literature reviews and surveys |
| `Book` | Book chapters |
| `Dataset` | Dataset papers |

**Pro tip**: Literature `Review` papers are great for understanding a field quickly.

### By Open Access

Set `openAccessPdf=true` to only return papers with free PDFs. Useful when the user needs to actually read the papers.

---

## Presenting Results

### Standard Result Format

For each paper, present:

```
**[Paper Title]**
Authors: [First Author] et al. ([Year])
Citations: [count] | Venue: [journal/conference]
TLDR: [AI summary if available]
Abstract: [First 2-3 sentences if no TLDR]
Link: [Semantic Scholar URL]
```

### For Literature Overviews

When summarizing a research area:

1. **Start with the most-cited papers** (foundational work)
2. **Include recent highly-cited papers** (current directions)
3. **Note any survey/review papers** (comprehensive overviews)
4. **Group by subtopic** if results span multiple areas

### Example Output Format

```
## Research on [Topic]: Key Papers

### Foundational Work
1. **Attention Is All You Need** (Vaswani et al., 2017)
   - Citations: 95,000+ | The paper that introduced Transformers
   - Key contribution: Self-attention mechanism replacing RNNs

### Recent Advances (2023-2024)
2. **[Recent Paper Title]** (Author et al., 2024)
   - Citations: 150 | Published in NeurIPS
   - Key finding: [Summary]

### Review Papers
3. **A Survey of Transformers** (Lin et al., 2022)
   - Comprehensive overview of transformer architectures
   - Good starting point for understanding the field
```

---

## Common Research Tasks

### Task: Find Seminal Papers in a Field

1. Search with broad field terms
2. Set `minCitationCount=500` or higher
3. Sort mentally by citation count
4. Look for papers from 5+ years ago (time to accumulate citations)

### Task: Find State-of-the-Art

1. Search specific topic + "state of the art" or technique name
2. Filter to recent years: `year=2023-2024`
3. Include top conferences/venues
4. Check citation count relative to age

### Task: Literature Review

1. First, find any existing Review papers: `publicationTypes=Review`
2. Find foundational papers (high citations, older)
3. Find recent papers (last 2-3 years)
4. Get citations and references of key papers
5. Synthesize themes across papers

### Task: Find Related Work

1. Get the paperId of the starting paper
2. Use `/paper/{id}/references` - what does it build on?
3. Use `/paper/{id}/citations` - what builds on it?
4. Use recommendations endpoint for similar papers

### Task: Track a Researcher

1. Search author by name
2. Get their papers sorted by year
3. Identify their most-cited work
4. Note recent publications and trends

---

## Handling Edge Cases

### No Results Found

If search returns nothing:
1. Simplify the query (fewer terms)
2. Remove year filters
3. Try alternate terminology
4. Check spelling of technical terms
5. Search broader category

### Too Many Results

If overwhelmed by results:
1. Add `minCitationCount` filter
2. Narrow year range
3. Add `fieldsOfStudy` filter
4. Use more specific terms
5. Focus on Review papers first

### User Asks About Very Recent Work

Recent papers (< 1 year) have few citations:
- Don't use `minCitationCount`
- Look at author reputation instead
- Check venue quality (top conferences)
- Note the work is recent and citations pending

### User Asks About Non-Academic Sources

Semantic Scholar covers academic papers only. For:
- Blog posts, news: Use web search
- Patents: Use Google Patents
- Technical reports: May be in S2 if archived on ArXiv

---

## Quality Signals

### Indicators of Important Papers

- **High citation count** relative to age
- **Published in top venues** (Nature, Science, NeurIPS, ICML, ACL, etc.)
- **Authors from major institutions**
- **Has many influential citations** (not just total citations)
- **Referenced by other highly-cited papers**

### Indicators of Relevant Results

- **Title matches query intent**
- **Abstract discusses the specific topic**
- **TLDR confirms relevance**
- **Fields of study align with user's interest**
- **Year matches user's timeframe needs**

---

## Top Venues by Field

### Computer Science / AI
- NeurIPS, ICML, ICLR (machine learning)
- ACL, EMNLP, NAACL (NLP)
- CVPR, ICCV, ECCV (computer vision)
- Nature Machine Intelligence, JMLR

### Medicine / Biology
- Nature, Science, Cell
- NEJM, Lancet, JAMA
- Nature Medicine, Nature Biotechnology

### Physics
- Physical Review Letters
- Nature Physics
- Science

Knowing top venues helps prioritize results when citation counts are similar.
