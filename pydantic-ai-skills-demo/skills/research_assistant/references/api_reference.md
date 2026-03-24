# Semantic Scholar API Reference

Semantic Scholar provides free access to a corpus of over 214 million academic papers with rich metadata, citations, and AI-generated summaries.

## Base URL

```
https://api.semanticscholar.org/graph/v1
```

## Authentication

No API key required for basic use. Unauthenticated requests share a pool of 1000 requests/second.

For higher rate limits, request an API key at: https://www.semanticscholar.org/product/api

Include key in header: `x-api-key: YOUR_KEY`

---

## Paper Search Endpoint

**GET** `/paper/search`

Search for papers by keyword query.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search terms |
| `fields` | string | No | Comma-separated fields to return |
| `limit` | int | No | Results per page (default: 10, max: 100) |
| `offset` | int | No | Pagination offset (max: 9999) |
| `year` | string | No | Filter by year: `2023` or range `2020-2023` |
| `openAccessPdf` | boolean | No | Only papers with free PDF |
| `minCitationCount` | int | No | Minimum citations |
| `publicationTypes` | string | No | Filter: `JournalArticle`, `Conference`, `Review` |
| `fieldsOfStudy` | string | No | Filter: `Computer Science`, `Medicine`, etc. |

### Example Request

```
GET https://api.semanticscholar.org/graph/v1/paper/search?query=machine+learning&fields=title,authors,year,citationCount,abstract,tldr&limit=10&year=2023-2024
```

### Example Response

```json
{
  "total": 1250000,
  "offset": 0,
  "data": [
    {
      "paperId": "649def34f8be52c8b66281af98ae884c09aef38b",
      "title": "Example Paper Title",
      "year": 2023,
      "citationCount": 150,
      "authors": [
        {"authorId": "123456", "name": "Jane Smith"},
        {"authorId": "789012", "name": "John Doe"}
      ],
      "abstract": "This paper presents...",
      "tldr": {
        "model": "tldr@v2.0",
        "text": "A concise AI-generated summary of the paper."
      }
    }
  ]
}
```

---

## Paper Details Endpoint

**GET** `/paper/{paper_id}`

Get detailed information about a specific paper.

### Paper ID Formats

| Format | Example |
|--------|---------|
| S2 ID | `649def34f8be52c8b66281af98ae884c09aef38b` |
| DOI | `DOI:10.18653/v1/N18-3011` |
| ArXiv | `ARXIV:2106.15928` |
| PubMed | `PMID:19872477` |
| ACL | `ACL:W12-3903` |
| MAG | `MAG:112218234` |
| Corpus ID | `CorpusId:215416146` |

### Example Request

```
GET https://api.semanticscholar.org/graph/v1/paper/ARXIV:1706.03762?fields=title,authors,year,citationCount,abstract,tldr,references,citations
```

---

## Paper Fields Reference

Use these in the `fields` parameter (comma-separated):

### Basic Fields
| Field | Description |
|-------|-------------|
| `paperId` | Unique Semantic Scholar ID |
| `title` | Paper title |
| `year` | Publication year |
| `abstract` | Full abstract text |
| `tldr` | AI-generated summary (when available) |

### Citation Fields
| Field | Description |
|-------|-------------|
| `citationCount` | Number of citations |
| `influentialCitationCount` | Citations that are influential |
| `referenceCount` | Number of references |
| `citations` | List of citing papers |
| `references` | List of referenced papers |

### Author & Venue Fields
| Field | Description |
|-------|-------------|
| `authors` | List of authors with IDs and names |
| `venue` | Publication venue (journal/conference) |
| `publicationVenue` | Detailed venue information |
| `publicationDate` | Full date (YYYY-MM-DD) |

### Access Fields
| Field | Description |
|-------|-------------|
| `url` | Semantic Scholar URL |
| `openAccessPdf` | Free PDF URL if available |
| `externalIds` | DOI, ArXiv, PubMed IDs |
| `isOpenAccess` | Boolean open access status |

### Classification Fields
| Field | Description |
|-------|-------------|
| `fieldsOfStudy` | List of fields (e.g., "Computer Science") |
| `s2FieldsOfStudy` | Detailed field classification |
| `publicationTypes` | Type: Journal, Conference, Review, etc. |

---

## Author Search Endpoint

**GET** `/author/search`

Search for authors by name.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Author name |
| `fields` | string | No | Author fields to return |
| `limit` | int | No | Results (default: 10, max: 100) |
| `offset` | int | No | Pagination offset |

### Example Request

```
GET https://api.semanticscholar.org/graph/v1/author/search?query=Geoffrey+Hinton&fields=name,paperCount,citationCount,hIndex
```

---

## Author Details Endpoint

**GET** `/author/{author_id}`

Get details about a specific author.

### Author Fields

| Field | Description |
|-------|-------------|
| `authorId` | Unique author ID |
| `name` | Author name |
| `paperCount` | Number of papers |
| `citationCount` | Total citations |
| `hIndex` | H-index |
| `papers` | List of author's papers |
| `affiliations` | Current affiliations |
| `homepage` | Author's website |

### Example Request

```
GET https://api.semanticscholar.org/graph/v1/author/1741101?fields=name,paperCount,citationCount,hIndex,papers.title,papers.year
```

---

## Paper Citations Endpoint

**GET** `/paper/{paper_id}/citations`

Get papers that cite a specific paper.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | string | No | Fields for citing papers |
| `limit` | int | No | Results (default: 100, max: 1000) |
| `offset` | int | No | Pagination offset |

### Example Request

```
GET https://api.semanticscholar.org/graph/v1/paper/ARXIV:1706.03762/citations?fields=title,authors,year,citationCount&limit=20
```

---

## Paper References Endpoint

**GET** `/paper/{paper_id}/references`

Get papers referenced by a specific paper.

### Example Request

```
GET https://api.semanticscholar.org/graph/v1/paper/ARXIV:1706.03762/references?fields=title,authors,year,citationCount&limit=20
```

---

## Paper Recommendations Endpoint

**GET** `/recommendations/v1/papers/forpaper/{paper_id}`

Get papers similar to a given paper.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | string | No | Paper fields to return |
| `limit` | int | No | Results (default: 10, max: 500) |

### Example Request

```
GET https://api.semanticscholar.org/recommendations/v1/papers/forpaper/649def34f8be52c8b66281af98ae884c09aef38b?fields=title,authors,year,citationCount&limit=10
```

---

## Bulk Paper Lookup

**POST** `/paper/batch`

Get details for multiple papers at once.

### Request Body

```json
{
  "ids": [
    "ARXIV:1706.03762",
    "DOI:10.18653/v1/N18-3011",
    "CorpusId:215416146"
  ]
}
```

### Example Request

```
POST https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,citationCount

Body: {"ids": ["ARXIV:1706.03762", "ARXIV:2106.15928"]}
```

---

## Fields of Study

Common values for `fieldsOfStudy` filter:

- Computer Science
- Medicine
- Biology
- Physics
- Chemistry
- Mathematics
- Engineering
- Psychology
- Economics
- Sociology
- Political Science
- Environmental Science
- Materials Science
- Business
- Art
- History
- Philosophy
- Linguistics
- Geography
- Education
- Law
- Agricultural and Food Sciences

---

## Rate Limits

| Tier | Rate Limit |
|------|------------|
| Unauthenticated | Shared pool of 1000 req/sec |
| API Key (Free) | 1 request/second |
| Partner | Higher limits (contact S2) |

---

## Error Responses

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 404 | Paper/Author not found |
| 429 | Rate limit exceeded |
| 500 | Server error |

---

## Constructing Paper URLs

To link to a paper on Semantic Scholar:
```
https://www.semanticscholar.org/paper/{paperId}
```

Example:
```
https://www.semanticscholar.org/paper/649def34f8be52c8b66281af98ae884c09aef38b
```

---

## Tips for Best Results

1. **Use specific queries**: "transformer attention mechanism" beats "AI"
2. **Always specify fields**: Reduces response size and speeds up requests
3. **Use year filters**: Narrow down to recent or specific time periods
4. **Check `tldr` field**: AI summaries save time when available
5. **Use `minCitationCount`**: Filter out obscure papers
6. **Paginate large results**: Use `offset` for more than 100 results
