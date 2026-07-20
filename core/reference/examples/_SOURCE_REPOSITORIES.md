# SOURCE REPOSITORIES - Live Example Access
Version: 1.0.0  
Purpose: Document where to find live examples for voice learning

---

## PRIMARY SOURCE: Application Intelligence System

**Location:** `D:\Application Intelligence System\Applications`

This is David's **active application repository** containing real cover letters, resumes, and application materials. Ghost Writer should query this directory for examples rather than relying on static copies.

### Why This Approach

- **Always current:** New applications added regularly
- **Large sample size:** Dozens/hundreds of examples vs. small static set
- **Real outcomes:** These are actual applications that got responses
- **Context rich:** Organized by company, role, date
- **Quality proven:** Reflects what actually works

### How Ghost Writer Uses This

```yaml
When generating applications:
  1. QUERY D:\Application Intelligence System\Applications
  2. SEARCH for similar roles/companies/contexts
  3. LEARN from patterns in successful applications
  4. EXTRACT voice patterns that worked
  5. APPLY to current generation
```

### Directory Structure (Expected)

```
D:\Application Intelligence System\Applications\
├── [Company Name 1]/
│   ├── cover_letter.docx
│   ├── resume.docx
│   ├── [other materials]
├── [Company Name 2]/
│   ├── cover_letter.docx
│   ├── resume.docx
├── ...
```

### Selection Criteria

When querying for examples, prioritize:
1. **Recent applications** (last 6 months)
2. **Similar role tiers** (entry/mid/senior/executive)
3. **Similar industries** (cannabis, operations, tech)
4. **High-quality outcomes** (interviews, offers)

### Integration Commands

```bash
# List recent applications
Desktop Commander:list_directory "D:\Application Intelligence System\Applications"

# Search for specific role type
Desktop Commander:start_search --path "D:\Application Intelligence System\Applications" --pattern "VP" --searchType content

# Read specific example
Filesystem:read_text_file "D:\Application Intelligence System\Applications\[Company]\cover_letter.docx"
```

---

## SECONDARY SOURCES (Planned - Pending Oktyv)

### LinkedIn Posts
**Source:** Live LinkedIn post history  
**Access Method:** Oktyv browser automation  
**Status:** Pending Oktyv implementation

When available:
- Scrape last 20-50 posts
- Extract voice patterns
- Learn what resonates (likes, comments)
- Sample from successful posts

### Gmail/Email
**Source:** Sent email folder  
**Access Method:** Oktyv browser automation  
**Status:** Pending Oktyv implementation

When available:
- Access professional emails
- Filter by recipient type (colleagues, clients, candidates)
- Extract communication patterns
- Learn from effective exchanges

### Technical Documentation
**Source:** Project README files in D:\Dev\  
**Access Method:** Direct filesystem access  
**Status:** Available now

Locations:
- D:\Dev\KERNL\README.md
- D:\Dev\SHIM\README.md
- D:\Dev\GREGORE\README.md
- D:\Project Mind\kernl-mcp\README.md
- Other project documentation

---

## STATIC EXAMPLES (Curated, Small Set)

These remain in `core/reference/examples/` for reference:

### Personal Communications
- `emails/` - 6 example emails (friend, landlord, recruiter, etc.)
- `personal/` - Family introduction, wedding vows
- `linkedin_posts/` - 1 example LinkedIn post
- `social_media/` - Twitter/Bluesky posts, social media replies

### Long Form
- `long_form/` - Political manifesto example

### Application Responses
- `personal/` - Application questionnaire responses

**Purpose:** Rare or unique types not in active repositories

---

## AUTO-SAMPLING (Largest Source Over Time)

**Location:** `learning/samples/from_{environment}/`

Every Ghost Writer output is automatically saved here and becomes a learning source:

```yaml
Workflow:
  1. Generate content
  2. Auto-save to learning/samples/from_{environment}/
  3. pattern_extractor.py processes sample
  4. Patterns added to voice.db
  5. Future generations benefit from learned patterns

Over time: This becomes the PRIMARY voice source
```

**Why this matters:**
- Captures YOUR actual usage patterns
- Learns from YOUR feedback and revisions
- Adapts to YOUR evolving voice
- Grows continuously
- No manual curation needed

---

## USAGE PRIORITY

When Ghost Writer needs examples:

```yaml
Priority 1: Application Intelligence System
  - For cover letters, resumes, applications
  - Always check D:\Application Intelligence System\Applications first

Priority 2: Auto-samples (voice.db)
  - For all content types
  - Query voice_patterns table for high-confidence patterns
  - Sample from recent_quality_samples view

Priority 3: Technical documentation
  - For DEV environment work
  - Read from D:\Dev\ project READMEs

Priority 4: Static examples
  - For rare types (wedding vows, family communications)
  - Fallback when other sources unavailable

Priority 5: Live sources (future)
  - LinkedIn, Gmail via Oktyv
  - Pending integration
```

---

## FUTURE: Oktyv Integration

Once Oktyv is built, Ghost Writer will be able to:

### LinkedIn Integration
```yaml
Query: "Show me my last 20 LinkedIn posts"
Oktyv:
  1. Navigate to LinkedIn
  2. Access profile
  3. Scrape posts
  4. Return structured data

Ghost Writer:
  1. Receive post data
  2. Extract voice patterns
  3. Update voice.db
  4. Learn from engagement metrics
```

### Gmail Integration
```yaml
Query: "Show me professional emails from last month"
Oktyv:
  1. Navigate to Gmail
  2. Apply filters
  3. Extract email content
  4. Return structured data

Ghost Writer:
  1. Receive email data
  2. Categorize by recipient type
  3. Extract voice patterns
  4. Update voice.db
```

### Google Drive Integration
```yaml
Query: "Find documents related to [topic]"
Oktyv:
  1. Navigate to Drive
  2. Search for topic
  3. Access relevant documents
  4. Return content

Ghost Writer:
  1. Receive document data
  2. Extract relevant examples
  3. Learn from successful formats
  4. Update voice.db
```

---

## MAINTENANCE

### Regular Tasks

**Weekly:**
- Review new applications in Application Intelligence System
- Note any standout examples
- Tag high-quality outcomes

**Monthly:**
- Check auto-sample quality (learning/samples/)
- Run pattern extraction on accumulated samples
- Review voice drift metrics

**Quarterly:**
- Audit example quality across all sources
- Archive or remove outdated examples
- Update selection criteria

### Quality Indicators

Good examples have:
- Clear voice authenticity
- Specific, quantified achievements
- Natural contractions (60-95% depending on mode)
- Zero forbidden patterns
- Appropriate formality for context
- Measurable outcomes (applications: interviews/offers)

---

## NOTES

- **Do NOT copy files** from Application Intelligence System to Ghost Writer
- **Query on-demand** to always get latest
- **Learn patterns** rather than copying content
- **Respect privacy** when sampling emails/LinkedIn
- **Document outcomes** to learn what works

---

**Version:** 1.0.0  
**Status:** Application Intelligence System integration ready  
**Pending:** Oktyv integration for live LinkedIn/Gmail access
