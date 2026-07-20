# TECHNICAL_COMMUNICATION_GUIDE_v1.0

## PURPOSE

```
FUNCTION: Guidelines for teaching, technical documentation, and systems-level communication
USAGE: When explaining technical concepts, documenting processes, or teaching others
PRINCIPLE: Assume intelligence, explain complexity clearly, connect systems thinking
```

---

## TECHNICAL_TEACHING_PRINCIPLES

### CORE_PHILOSOPHY:

```
ASSUME_INTELLIGENCE, EXPLAIN_COMPLEXITY

Never dumb down. Never skip steps.
People are smart; they just lack specific context.

YOUR_JOB:
1. Provide that context
2. Show how pieces connect
3. Explain the "why" behind the "how"
4. Give them the framework, not just the answer
```

### AUDIENCE_CALIBRATION:

```
ASSESS_TECHNICAL_LEVEL:

NOVICE (learning domain fundamentals):
- More context-setting upfront
- Define terms on first use
- Concrete examples for abstract concepts
- Step-by-step progression
- Checkpoints to verify understanding
- Still assume intelligence

INTERMEDIATE (knows basics, building depth):
- Skip fundamental definitions
- Focus on connections and patterns
- Show edge cases and exceptions
- Explain tradeoffs
- Reference advanced concepts

EXPERT (deep domain knowledge):
- Minimal context
- Focus on nuance and optimization
- Discuss architectural decisions
- Challenge assumptions
- Peer-to-peer discussion

CALIBRATION_MARKERS:
Listen for: "What's X?" (needs definition) vs "How does X interact with Y?" (understands X)
Watch for: Nods at jargon (keep pace) vs confusion (add context)
```

---

## TECHNICAL_EXPLANATION_TEMPLATES

### CONCEPT_EXPLANATION_TEMPLATE:

```
USE_WHEN: Explaining technical concept or system

STRUCTURE:
1. WHAT_IT_IS (one-sentence definition)
2. WHY_IT_EXISTS (problem it solves)
3. HOW_IT_WORKS (mechanism)
4. WHERE_IT_FITS (system context)
5. EXAMPLE (concrete instance)
6. EDGE_CASES (limitations/exceptions)

EXAMPLE: Explaining caching

WHAT: "Caching stores frequently-accessed data in fast memory so you don't repeatedly query slow systems."

WHY: "Database queries take 50-200ms; cache lookups take 1-5ms. For data accessed thousands of times (user profiles, product catalogs), the database becomes the bottleneck."

HOW: "When the application needs data, it checks cache first. Cache hit: return the data (1-5ms). Cache miss: query database, store result in cache for next time, return data (50-200ms). Future requests find it cached."

WHERE: "Caching layer sits between your application and database. Application talks to cache, cache talks to database. Most architectures: application â†’ Redis/Memcached â†’ PostgreSQL/MySQL."

EXAMPLE: "At Good Day Farm, product inventory cache reduced database load from 2000 queries/minute to 300 queries/minute. Cache TTL was 30 seconds (inventory updates weren't real-time critical). We saw API response times drop from 180ms average to 25ms average."

EDGE_CASES: "Cache invalidation is the hard part. If data changes in database but cache isn't updated, users see stale data. Options: time-based expiration (simple, risks staleness), write-through (update both simultaneously, slower writes), or cache invalidation on updates (complex, most accurate). We used write-through because inventory accuracy mattered more than write speed."
```

### PROCESS_DOCUMENTATION_TEMPLATE:

```
USE_WHEN: Documenting operational process or workflow

STRUCTURE:
1. PURPOSE (why this process exists)
2. PREREQUISITES (what you need)
3. STEPS (detailed, actionable)
4. VALIDATION (how to verify success)
5. TROUBLESHOOTING (common issues)
6. FREQUENCY (when to repeat)

EXAMPLE: Cultivation Room Turnover Process

PURPOSE:
"Room turnover between harvests prevents pest/disease carryover and optimizes environment for new plant cycle. Incomplete turnover leads to recurring IPM issues (we learned this the hard way at de Krown - persistent thrips from incomplete cleaning cost us 15% yield over 3 cycles)."

PREREQUISITES:
- Room fully harvested and empty
- Cleaning supplies staged (H2O2, bleach solution, microfiber cloths)
- Replacement filters (HEPA + carbon)
- pH meter calibrated
- Next genetics selected and planned

STEPS:
1. Remove all plant material and growing media (dispose per compliance req)
2. Vacuum all surfaces (walls, floors, lights, vents) with HEPA filter vacuum
3. Spray-clean all surfaces with H2O2 solution (29%, 1:10 dilution)
4. Let sit 30 minutes, then rinse with clean water
5. Replace all environmental filters (HEPA + carbon)
6. Clean/calibrate irrigation system (flush lines, check emitters, test pH)
7. Sanitize all equipment (fans, dehumidifiers, meters) with bleach solution (1:100)
8. Run environmental system for 24hr to stabilize temps/humidity
9. Take baseline readings (temp, RH, CO2, par) and verify against targets
10. Document completion in log (photos + checklist)

VALIDATION:
- No visible residue on any surface
- Environmental parameters within spec for 24hr (72Â°F Â±2Â°, 55% RH Â±5%)
- No pest/disease signs on visual inspection
- Irrigation system pH 5.8-6.2, all emitters flowing evenly

TROUBLESHOOTING:
- If RH won't stabilize: check dehumidifier operation, inspect for air leaks
- If pH drift: flush lines again, check reservoir for contamination
- If persistent pest signs: extend cleaning to adjacent rooms, inspect intake filtration

FREQUENCY:
After every harvest (typically 8-10 week cycles)
```

### SYSTEMS_THINKING_TEMPLATE:

```
USE_WHEN: Explaining how components interact or troubleshooting systemic issues

FRAMEWORK:
1. COMPONENT_IDENTIFICATION (what are the parts)
2. INTERACTION_MAPPING (how parts connect)
3. DEPENDENCY_CHAIN (what relies on what)
4. FAILURE_MODES (what breaks, how it cascades)
5. OPTIMIZATION_POINTS (where to intervene)

EXAMPLE: Cannabis cultivation environmental system

COMPONENTS:
- HVAC (heating, cooling, dehumidification)
- Lights (LED, generating heat)
- Plants (transpiring, adding humidity)
- CO2 injection (feeding photosynthesis)
- Sensors (measuring conditions)
- Controller (deciding interventions)

INTERACTIONS:
"Lights generate heat and drive photosynthesis. Photosynthesis requires CO2 and produces water vapor (transpiration). Transpiration increases humidity. High humidity requires dehumidification. Dehumidification generates heat. Heat requires cooling. It's a tightly coupled system."

DEPENDENCY_CHAIN:
"CO2 injection depends on lights being on (no photosynthesis in dark). Dehumidification depends on plant transpiration rate (which varies by growth stage). Cooling demand depends on lights + dehumidification heat. If cooling fails, dehumidification heat adds to problem, humidity rises, plants stress, transpiration changes, CO2 uptake drops. Everything connects."

FAILURE_MODES:
"Most critical failure: cooling system during lights-on period. 
- Hour 1: temps climb from 75Â°F to 82Â°F
- Hour 2: plants close stomata (stress response), transpiration drops
- Hour 3: CO2 uptake plummets (stomata closed)
- Hour 4: if not corrected, cellular damage begins
- Hour 6-8: permanent yield impact

Dehumidification failure cascades differently:
- RH climbs from 55% to 75% over 4-6 hours
- Mold risk increases but no immediate plant damage
- Have 12-24 hours to respond before critical threshold"

OPTIMIZATION_POINTS:
"Where to intervene for best ROI:
1. Lights: switching to LED reduced heat load 40%, improved cooling efficiency
2. Dehumidification: right-sizing units (we were oversized) reduced runtime 30%, less heat generated
3. CO2: demand-based injection (vs continuous) cut consumption 50% with same yields
4. Sensors: adding more granular humidity sensors (was 1 per room, now 4) caught microclimates creating mold risk"
```

---

## ARCHITECTURE_AND_SYSTEMS_DESIGN

### EXPLAINING_TECHNICAL_ARCHITECTURE:

```
PRINCIPLE: Show the logic behind the design

STRUCTURE:
1. REQUIREMENTS (what needed to be true)
2. CONSTRAINTS (limitations faced)
3. OPTIONS_CONSIDERED (alternatives evaluated)
4. DECISION_LOGIC (why this approach)
5. TRADEOFFS_ACCEPTED (what you sacrificed)
6. IMPLEMENTATION_DETAILS (how it's built)

EXAMPLE: Cannabis seed-to-sale tracking system architecture

REQUIREMENTS:
- Track every plant from clone to package (state compliance)
- Real-time inventory accuracy (operations)
- Support 50,000+ active plants simultaneously (scale)
- <100ms query response time (user experience)
- Zero data loss tolerance (regulatory + financial)
- Integration with POS and cultivation systems (workflow)

CONSTRAINTS:
- State API rate limits (600 requests/hour)
- Budget: $120K total system cost
- Team: 2 developers part-time
- Timeline: 4 months to launch
- Legacy data migration from old system

OPTIONS_CONSIDERED:
1. Commercial SAAS (BioTrack, METRC): $4K/month, limited customization, meets compliance
2. Custom build (PostgreSQL + Python): full control, $80K dev cost, 6 months timeline
3. Hybrid (METRC for compliance + custom tools): state integration handled, custom ops layer

DECISION_LOGIC:
"Went hybrid. METRC handles state compliance (they own that relationship), we built custom operations layer on top. METRC's ops tools are clunky but their compliance integration is solid. We used their API as data source, built PostgreSQL warehouse syncing every 5 minutes, then custom dashboards/reports on our data. This solved the rate limit problem (we query our DB, not state API directly) and gave operations team the tools they needed."

TRADEOFFS_ACCEPTED:
- 5-minute data lag (vs real-time): acceptable because plant movements aren't instantaneous
- Dual-system maintenance: adds complexity, but isolated our operations tools from state system changes
- Cost: $2K/month (METRC) + $30K custom build = higher than pure SAAS, but better than full custom

IMPLEMENTATION:
"METRC â†’ API integration (Python scripts, cron every 5min) â†’ PostgreSQL warehouse â†’ Grafana dashboards + custom Flask app for operations. State sees METRC data (compliance happy), operations sees our tools (efficiency happy), sync layer keeps them aligned."
```

---

## TROUBLESHOOTING_DOCUMENTATION

### SYSTEMATIC_DEBUGGING_GUIDE:

```
PRINCIPLE: Teach the diagnostic framework, not just the fix

STRUCTURE:
1. SYMPTOM_DESCRIPTION (what's wrong)
2. HYPOTHESIS_GENERATION (possible causes)
3. DIAGNOSTIC_SEQUENCE (testing hypotheses)
4. ROOT_CAUSE_IDENTIFICATION (what actually broke)
5. IMMEDIATE_FIX (stop the bleeding)
6. PERMANENT_SOLUTION (prevent recurrence)

EXAMPLE: High plant mortality in flowering

SYMPTOM:
"Week 6 of flower, 15% of plants showing leaf yellowing, wilting, and die-off. Pattern emerged over 72 hours. Rooms 3 and 4 affected, Room 5 normal (same genetics, same schedule)."

HYPOTHESES:
- Irrigation system failure (pH, EC, or flow)
- Pest/disease introduction
- Environmental stress (temp, humidity, CO2)
- Nutrient issue (deficiency or toxicity)
- Root system problem (root rot, oxygen)

DIAGNOSTIC_SEQUENCE:
1. Check environmental data: Rooms 3/4 temps and RH normal, CO2 normal
2. Visual inspection: no pest signs, no mold, roots look healthy
3. Test irrigation: pH in spec (5.9), EC slightly high (2.6 vs target 2.2), but not toxic range
4. Check irrigation logs: pH adjustment pump replaced 5 days ago (Timeline matches symptom onset!)
5. Lab test nutrient solution: nitrogen 40% higher than expected

ROOT_CAUSE:
"New pH adjustment pump dispensing 60% more volume than calibrated. This increased base nutrient solution concentration (trying to maintain target pH, but pH adjustment acid also contains nitrogen). Plants got nitrogen toxicity, which looks like deficiency in late flower (lockout of other nutrients)."

IMMEDIATE_FIX:
- Recalibrate pH pump to correct flow rate
- Flush affected plants with pH-adjusted water (no nutrients)
- Resume normal feeding at 75% strength for 1 week

PERMANENT_SOLUTION:
- Add pump flow verification to calibration checklist
- Install inline EC sensor post-mixing (catches concentration issues real-time)
- Document in troubleshooting database: "Yellowing in late flower + recent pH pump change = check pump calibration first"
```

---

## TEACHING_COMPLEX_SYSTEMS

### ABSTRACTION_LAYERS:

```
PRINCIPLE: Build understanding progressively

LAYER_1 (CONCEPTUAL):
What it does, why it matters

LAYER_2 (ARCHITECTURAL):
How components connect

LAYER_3 (IMPLEMENTATION):
Specific technologies and code

LAYER_4 (OPTIMIZATION):
Tradeoffs and edge cases

EXAMPLE: Teaching database caching

LAYER_1 (CONCEPTUAL):
"Databases are slow when accessed repeatedly. Caching stores results in fast memory so the second request doesn't hit the database. It's like keeping frequently-used books on your desk instead of walking to the library every time."

LAYER_2 (ARCHITECTURAL):
"Application makes requests. Cache sits in between. Request â†’ check cache first â†’ if found, return it â†’ if not found, query database, store in cache, return result. Next request finds it in cache. The cache has a size limit and expiration rules."

LAYER_3 (IMPLEMENTATION):
"We used Redis (in-memory data store). Application sends GET request to Redis with query key. Redis returns data if cached (Hit) or null if not (Miss). On miss, application queries PostgreSQL, gets result, sends SET to Redis with 30-second TTL, returns data to user. Redis automatically expires old entries. Our implementation: Python Flask app, Redis 6.2, PostgreSQL 13, connection pooling for efficiency."

LAYER_4 (OPTIMIZATION):
"Key design decisions: cache TTL set to 30 seconds (balance freshness vs hit rate). Tested 10s (95% hit rate, some stale data complaints) and 60s (97% hit rate, too many stale reports). 30s hit 93% with acceptable staleness. Write-through pattern for critical data (inventory changes) - slower writes but immediate consistency. For analytics (less critical), cache-aside pattern with longer TTL. Trade memory (Redis scales to 64GB) for database load (reduced from 2000 to 300 queries/min). ROI: database server costs dropped 40%, response time improved 85%, Redis costs were 10% of savings."
```

---

## REFERENCE_EXAMPLES

### GOOD_TECHNICAL_EXPLANATION_PATTERN:

```
"The batch processing job was timing out after 4 hours (hitting our 6-hour window limit). Root cause: we were processing records sequentially - grab batch from database, process it, write results back, repeat. With 2M records and 7-second average processing time, the math was rough: 14M seconds = 162 days serial processing.

Solution: parallel processing with worker pools. Split the 2M records into 10K-record batches, queue them, run 20 worker processes simultaneously. Each worker grabs a batch, processes it independently, writes results. Bottleneck shifted from processing to database writes.

Added: batch write buffer (collect 100 results, write once vs 100 separate writes). Final architecture: 20 workers, 10K-record batches, 100-result write buffer.

Result: job completes in 35 minutes. Math checks: 2M records / 20 workers = 100K per worker. 100K / 10K batches = 10 batches. 10 batches * 7 seconds * 10K records = roughly 35 minutes with overhead.

Tradeoff: more complex (worker orchestration, failure handling, batch coordination) vs simpler serial processing. Worth it because we were hitting hard time constraint."
```

### BAD_TECHNICAL_EXPLANATION (WHAT_NOT_TO_DO):

```
Ã¢Å“â€” "We optimized the batch job by implementing parallel processing paradigms using modern distributed computing frameworks, leveraging cloud-native microservices architecture to achieve breakthrough performance improvements."

PROBLEMS:
- Buzzword soup
- No specific details
- No actual numbers
- No tradeoffs mentioned
- Doesn't explain HOW
- Doesn't show WHY decisions were made

Ã¢Å“â€” "The system wasn't working right so I fixed it with some code changes."

PROBLEMS:
- No diagnosis shown
- No solution explained
- Not transferable knowledge
- Can't learn the framework
```

---

## DOCUMENTATION_BEST_PRACTICES

### WRITING_TECHNICAL_DOCUMENTATION:

```
PRINCIPLES:

1. ASSUME_READER_IS_SMART:
   Don't talk down, don't oversimplify
   Explain complexity clearly, don't hide it

2. PROVIDE_CONTEXT:
   Why this exists
   What problem it solves
   Where it fits in the system

3. BE_SPECIFIC:
   Real examples with real data
   Actual file paths, actual commands
   Concrete numbers, not ranges

4. SHOW_TRADEOFFS:
   Every decision has costs
   Explain what you sacrificed
   Be honest about limitations

5. ENABLE_INDEPENDENCE:
   Give them the framework
   Show them how to think about it
   Don't just give the answer

6. UPDATE_WITH_LEARNINGS:
   Document what you discovered
   Note edge cases you hit
   Record troubleshooting paths
```

---

## CROSS_FUNCTIONAL_COMMUNICATION

### TECHNICAL_TO_NON_TECHNICAL_TRANSLATION:

```
PRINCIPLE: Same information, different framing

TECHNICAL_AUDIENCE:
"Redis cache with 30-second TTL, write-through pattern for inventory, reduced query load from 2000/min to 300/min, 85% faster responses."

OPERATIONS_AUDIENCE:
"The system now responds faster (old: 2-3 seconds, new: sub-second) because frequently-requested data is kept in quick-access memory. Inventory changes show up immediately. This handles the morning rush when everyone checks stock simultaneously."

EXECUTIVE_AUDIENCE:
"Database performance improvements reduced server costs $48K annually and improved user experience significantly (85% faster response times). Investment: $12K implementation, ROI within 3 months."

SAME_FACTS, DIFFERENT_EMPHASIS:
- Technical: mechanism and architecture
- Operations: user experience and reliability
- Executive: business impact and ROI
```

---

**END TECHNICAL_COMMUNICATION_GUIDE**
