# REFERENCE - Authentic Voice Samples
Location: D:\Ghost Writer\core\reference\

## PURPOSE

Ground truth examples of David's authentic voice across contexts. These are the empirical foundation for all voice protocols and pattern extraction.

## KEY FILES

### AUTHENTIC_VOICE_REFERENCE.md
Master collection of voice examples with metadata. Each example includes:
- Context (who, what, when, why)
- Relationship dynamics
- Intensity level
- Key voice characteristics
- What works / what doesn't

**Status:** MOVE from D:\ghost writer\

## EXAMPLES DIRECTORY

Organized by communication type for easy retrieval:

### examples/cover_letters/
Professional application materials. Includes:
- Job-specific cover letters
- Consideration letters
- Application responses

**Files to move here:**
- Application_Email_and_Cover_Letter.docx
- Consideration_Letter__Blue_Sky_Corp_.docx
- Consideration_Letter__Blue_Sky_Packaging_.docx
- Consideration_Letter__F_Street_Dispensary_.docx
- Cover_Letter.docx

### examples/emails/
Email communications across contexts. Includes:
- Professional emails
- Recruiter communications
- Informal emails

**Files to move here:**
- Email_Follow_up_to_HR_Recruiter_.docx
- Email_to_Friend_.docx
- Email_to_Hiring_Manager.docx
- Email_to_Landlord_.docx
- Conversation_nwith_Recruiter.docx
- Conversation_-_Myself_and_Realtor.docx

### examples/linkedin_posts/
Social/professional thought leadership. Includes:
- Company culture posts
- Industry commentary
- Professional insights

**Files to move here:**
- LinkedIn_Post_-_Company_Culture___Psychology.docx

### examples/personal/
Personal/intimate communications. Includes:
- Family introductions
- Wedding vows
- Personal narratives

**Files to move here:**
- family_introduction.docx
- wedding_vows.docx
- Responses_to_Application_Questionaire_.docx

### examples/long_form/
Extended writing samples. Includes:
- Manifestos
- Essays
- Book excerpts

**Files to move here:**
- RBD_-_Political_Manifesto_Book.txt

## METADATA REQUIREMENTS

Each example should include:
```yaml
---
type: cover_letter | email | linkedin | personal | long_form
context: Brief description
relationship: professional | casual | intimate | formal
intensity: 1-10
audience: specific person/role
environment: career | personal | work
date_created: YYYY-MM-DD
key_patterns:
  - High contraction rate (85%)
  - Direct without being harsh
  - Minimal dashes (2 total)
lessons:
  - What worked well
  - What to replicate
  - What to avoid
---
```

## USING REFERENCE MATERIALS

**For Voice Calibration:**
Query voice.db for patterns extracted from these examples

**For Variation Generation:**
Find similar contexts in examples/ directory

**For Quality Validation:**
Compare output against AUTHENTIC_VOICE_REFERENCE.md

**For Learning:**
New outputs get saved to learning/samples/ and compared against reference

## MAINTAINING REFERENCE

Add new examples when:
- Particularly successful voice match
- New context not yet represented
- User explicitly says "save this as reference"

Remove examples when:
- Voice has evolved past this style
- Better examples exist for same context
- No longer represents authentic voice

## CROSS-REFERENCES

- `core/protocols/voice-calibration-matrix.md` (derived from these examples)
- `core/protocols/MASTER_PROTOCOL.md` (references these patterns)
- `learning/voice.db` (patterns extracted from these)
