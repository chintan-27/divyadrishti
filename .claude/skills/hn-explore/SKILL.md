---
name: hn-explore
description: Fetch and explore Hacker News data using Algolia and Firebase APIs. Use for testing ingestion logic, inspecting story/comment structure, or sampling data.
argument-hint: [story-id or search-query]
user-invocable: true
allowed-tools: Bash, Read, Write
---

# HN Data Explorer

Explore Hacker News data for: $ARGUMENTS

## APIs

### Algolia HN Search API
- Search stories: `https://hn.algolia.com/api/v1/search?query=QUERY&tags=story`
- Front page: `https://hn.algolia.com/api/v1/search?tags=front_page`
- Recent: `https://hn.algolia.com/api/v1/search_by_date?tags=story`
- Comments for story: `https://hn.algolia.com/api/v1/search?tags=comment,story_ID`

### Firebase HN API
- Item detail: `https://hacker-news.firebaseio.com/v0/item/ID.json`
- Top stories: `https://hacker-news.firebaseio.com/v0/topstories.json`
- New stories: `https://hacker-news.firebaseio.com/v0/newstories.json`
- Best stories: `https://hacker-news.firebaseio.com/v0/beststories.json`

## Instructions

1. If given a story ID, fetch it from Firebase and show its structure including comment tree
2. If given a search query, use Algolia to find matching stories
3. Use `curl` to fetch data and `python -m json.tool` to format output
4. Summarize the data shape — fields present, comment depth, score distribution
5. Note any fields relevant to the data model in `.claude/phase1_plan.md`
