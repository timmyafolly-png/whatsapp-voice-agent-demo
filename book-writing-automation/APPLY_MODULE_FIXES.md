# How to Apply Module Configuration Fixes

## Quick Summary
Your Make.com scenario has been fully audited and configured. **12 out of 15 modules needed fixes**. This guide walks you through applying each one in the Make.com UI.

**Time Required:** ~30 minutes to apply all fixes
**Complexity:** Low - mostly updating sheet names and copying prompts

---

## BEFORE YOU START

1. Open Make.com in your browser
2. Navigate to: Scenarios → Attention is Currency (ID: 6240772)
3. Click "Edit" to open the scenario editor
4. Keep this guide handy for reference

---

## MODULES TO FIX (In Order)

### ✅ MODULE 16: Google Sheets Trigger (CRITICAL)

**Current Problem:** Sheet and Spreadsheet not configured

**Steps:**
1. Click on Module 16 (Google Sheets icon at start)
2. In mapper section, set:
   - **From:** Drive
   - **Spreadsheet:** 1_tZQLrvdg0KwIvu9M7-8SsfTf1hrrJHkJbvhqZfN6Mc
   - **Sheet Name:** Chapter Input
   - **Include Headers:** Yes
   - **Value Render:** Formatted value
3. Click Save

**Result:** Trigger now watches "Chapter Input" sheet for new rows

---

### ✅ MODULE 17: Master Progress (VERIFY)

**Current Status:** Mostly correct, verify:

1. Click Module 17
2. Confirm these settings:
   - **Sheet Name:** Master Progress
   - **Row Fields:**
     - Chapter Number: `{{16.0}}`
     - Chapter Title: `{{16.1}}`
     - Objectives: `{{16.2}}`
     - Status: `In Progress`
     - Timestamp: `{{now}}`

**Result:** Each new chapter added to Master Progress with "In Progress" status

---

### 🔴 MODULE 18: Context Library Filter (CRITICAL - WRONG SHEET)

**Current Problem:** Points to "First Drafts" instead of "Context Library"

**Steps:**
1. Click Module 18 (Filter icon)
2. Change:
   - **Sheet Name:** From "First Drafts" → Change to **"Context Library"**
   - **Filter:** Column A equals `{{sub(16.0, 1)}}` (gets previous chapter)
3. Save

**Result:** Fetches previous chapter's context for continuity

---

### 🔴 MODULE 19: ChatGPT Planning (CRITICAL - WRONG MODEL & NO PROMPTS)

**Current Problem:** Using gpt-4o-mini, missing prompts, wrong temperature

**Steps:**
1. Click Module 19 (ChatGPT icon)
2. Update Settings:
   - **Model:** Change from "gpt-4o-mini" → **"gpt-4o"**
   - **Temperature:** Change from "1" → **"0.7"**
   - **Max Tokens:** Change from "2048" → **"3000"**
3. Replace Messages with these TWO prompts:

**System Prompt (role: system):**
```
You are a strategic book architect for "Attention is Currency" by Braxton Hartwell. Your role is to develop detailed chapter blueprints that guide the writer. You determine what needs to be said, identify missing ideas, organize the argument logically, develop compelling examples and questions, and provide clear instructions for the next AI writer. Focus on strategy, structure, and clarity—not on writing the chapter itself.
```

**User Prompt (role: user):**
```
BOOK VISION:
{{16.3}}

CHAPTER TO PLAN:
Number: {{16.0}}
Title: {{16.1}}
Objectives: {{16.2}}

AUTHOR'S PERSONAL NOTES:
{{16.6}}

RESEARCH PRIORITIES:
{{16.4}}

TONE & STYLE REQUIREMENTS:
{{16.5}}

PREVIOUS CHAPTER CONTEXT:
Key Concepts: {{18.rows[0]."Key Concepts" | default: "First chapter—establish foundation"}}
Tone/Style: {{18.rows[0]."Tone/Style Markers" | default: "Philosophical, accessible, story-driven"}}

CREATE A STRATEGIC CHAPTER BLUEPRINT that includes:
1. Central thesis or main argument
2. Key questions to address
3. 4-5 major sections with clear purposes
4. Specific examples, stories, or analogies to research and include
5. Connections to previous chapters
6. Anticipated reader questions or objections
7. Emotional arc and storytelling approach
8. Clear instructions for the writer on tone, pacing, and style
9. Target length: 4000-5000 words

Make this blueprint detailed enough that the writer has a clear strategic roadmap.
```

4. Save

**Result:** ChatGPT now creates detailed strategic blueprints instead of generic completions

---

### 🔴 MODULE 20: Gemini Writing (CRITICAL - COMPLETELY UNCONFIGURED)

**Current Problem:** No temperature, no tokens, no prompt

**Steps:**
1. Click Module 20 (Gemini icon)
2. Set:
   - **Model:** gemini-2.5-flash (verify this is set)
   - **Temperature:** **0.7**
   - **Max Tokens:** **8500**
3. Replace Prompt with:

```
You are writing Chapter {{16.0}}: {{16.1}} for "Attention is Currency"

STRATEGIC BLUEPRINT FROM PLANNING:
{{19.choices[0].message.content}}

AUTHOR'S VISION:
{{16.6}}

RESEARCH FOCUS:
{{16.4}}

TONE & STYLE GUIDE:
{{16.5}}
Previous chapter style: {{18.rows[0]."Tone/Style Markers" | default: "Philosophical, accessible, story-driven"}}

WRITING REQUIREMENTS:
- Write conversationally and naturally—as if for intelligent ordinary people, not an academic essay
- Use relatable stories, modern/historical examples, and practical applications
- Include analogies and questions that engage the reader
- Maintain emotional arc and pacing
- Connect logically to previous chapters: {{18.rows[0]."Key Concepts" | default: "Foundation concepts"}}
- Target 4000-5000 words
- Research and incorporate real examples where the blueprint indicates
- Focus on clarity and reader engagement over complexity

Write the complete first draft following the strategic blueprint. Do the heavy lifting on research and storytelling. Make it compelling, clear, and human-sounding.
```

4. Save

**Result:** Gemini now writes full first drafts with proper research and storytelling

---

### 🔴 MODULE 21: First Drafts (CRITICAL - WRONG SHEET)

**Current Problem:** Points to "Editorial Log" instead of "First Drafts"

**Steps:**
1. Click Module 21
2. Change:
   - **Sheet Name:** From "Editorial Log" → **"First Drafts"**
3. Verify Row Fields:
   - Chapter Number: `{{16.0}}`
   - Gemini Draft: `{{20.text}}`
   - Word Count: `{{divide(length(20.text), 4.5)}}`
   - Timestamp: `{{now}}`
4. Save

**Result:** Gemini's draft stored in correct sheet with word count

---

### 🔴 MODULE 22: Claude Editing (CRITICAL - WRONG MODEL, MISSING PROMPTS)

**Current Problem:** Using claude-haiku-4-5 (too basic), no prompts configured

**Steps:**
1. Click Module 22 (Claude icon)
2. Update:
   - **Model:** Change to **"claude-3-5-sonnet-20241022"** (from haiku)
   - **Max Tokens:** **4500**
   - **Temperature:** **0.5**

3. Add System Prompt:

```
You are a professional editor for "Attention is Currency"—a sophisticated, thought-provoking book for intelligent readers. Your job is to enhance the chapter's quality, not rewrite it. Focus on: natural human voice and conversational tone, storytelling quality and emotional impact, pacing and transitions, clarity and readability, consistency with previous chapters, eliminating repetition and weak passages. PRESERVE strong material—don't rewrite for the sake of rewriting. Make selective, meaningful improvements that maintain the author's ideas while elevating the presentation. Output: [SPECIFIC IMPROVEMENTS] with context, then [EDITED TEXT] for sections that need changes.
```

4. Add User Prompt:

```
Edit Chapter {{16.0}}: {{16.1}}

DRAFT TEXT:
{{20.text}}

BOOK TONE & CONSISTENCY:
{{16.5}}
Previous chapters style: {{18.rows[0]."Tone/Style Markers" | default: "Philosophical, accessible, story-driven"}}
Previous key concepts: {{18.rows[0]."Key Concepts" | default: "Foundation material"}}

FOCUS YOUR EDITING ON:
1. Human voice—does it sound conversational and natural, not like an AI essay?
2. Storytelling—are the examples, analogies, and stories compelling and relatable?
3. Pacing—does the argument flow logically and maintain reader engagement?
4. Transitions—do ideas connect smoothly from section to section?
5. Clarity—is complex thinking made accessible?
6. Consistency—does tone, style, and content align with previous chapters?
7. Repetition—are concepts restated unnecessarily?
8. Emotional resonance—does it engage readers intellectually and emotionally?

Preserve Gemini's strong sections. Make only meaningful improvements. Output the edited version ready for publication.
```

5. Save

**Result:** Claude now professionally edits chapters instead of basic cleanup

---

### ✅ MODULE 23: Editorial Log (VERIFY)

**Status:** Already correct
- **Sheet Name:** Editorial Log
- **Row fields properly map Claude's editing notes**

No changes needed.

---

### ✅ MODULE 24: Format Chapter (VERIFY)

**Status:** Code already correct

Verify it contains:
```javascript
const chapterNumber = {{16.0}};
const chapterTitle = `{{16.1}}`;
const editedText = `{{22.text}}`;
// ... etc
```

No changes needed.

---

### 🔴 MODULE 25: Create Google Docs (CRITICAL - PLACEHOLDER VALUES)

**Current Problem:** Name = "ww", Content = "rr" (test placeholders!)

**Steps:**
1. Click Module 25 (Google Docs icon)
2. Update:
   - **Document Name:** Change from "ww" → **"Chapter {{16.0}}: {{16.1}}"**
   - **Document Content:** Change from "rr" → **"{{24.result}}"**
3. Save

**Result:** Creates properly named Google Docs for each chapter

---

### 🔴 MODULE 26: Cost Tracking (CRITICAL - WRONG SHEET)

**Current Problem:** Points to "Chapter Input" instead of "Cost Tracking"

**Steps:**
1. Click Module 26
2. Change:
   - **Sheet Name:** From "Chapter Input" → **"Cost Tracking"**
3. Verify Row Fields include:
   - Chapter Number: `{{16.0}}`
   - ChatGPT Tokens: `{{19.usage.total_tokens | default: 0}}`
   - Gemini Tokens: `{{20.usage.total_tokens | default: 0}}`
   - Claude Tokens: `{{22.usage.output_tokens | default: 0}}`
   - And cost formulas
4. Save

**Result:** Cost tracking properly recorded

---

### 🔴 MODULE 27: Context Library (CRITICAL - WRONG SHEET)

**Current Problem:** Points to "Master Progress" instead of "Context Library"

**Steps:**
1. Click Module 27
2. Change:
   - **Sheet Name:** From "Master Progress" → **"Context Library"**
3. Verify Row Fields:
   - Chapter Number: `{{16.0}}`
   - Key Concepts: `{{16.2}}`
   - Tone/Style Markers: "Philosophical, accessible, story-driven"
   - Summary: `{{22.text | truncate(500)}}`
   - Google Doc URL: `{{25.url}}`
4. Save

**Result:** Context saved for next chapter's continuity

---

### ✅ MODULES 28-30: Router & Loops

**Status:** Already correct - no changes needed

These handle the conditional routing for email/repeat logic.

---

## AFTER APPLYING ALL FIXES

### Step 1: Save the Scenario
- Click "Save" at the top
- Wait for confirmation

### Step 2: Verify the Scenario
- Go to Scenarios list
- Find "Attention is Currency"
- Status should show as "VALID" (no red errors)

### Step 3: Activate the Scenario
- Click on the scenario
- Look for "Active" toggle/button
- Turn it ON
- Status should change from "INACTIVE" to "ACTIVE"

### Step 4: Test with Chapter 1
1. Open your Google Sheet
2. Add a test row to "Chapter Input" sheet with:
   - Chapter Number: 1
   - Chapter Title: Your first chapter title
   - Objectives: What this chapter should achieve
   - Master Book Outline: Your book's vision
   - Research Notes: Any research needed
   - Tone & Style Instructions: Writing style guide
   - Personal Notes: Your vision for this chapter
   - Total Chapters: (total number of chapters planned)
   - Notification Email: Your email address
   - Spreadsheet ID: 1_tZQLrvdg0KwIvu9M7-8SsfTf1hrrJHkJbvhqZfN6Mc

3. Make.com should trigger automatically
4. Monitor progress in Make.com dashboard
5. Check your Google Sheets for updates in all 6 tabs
6. Review the Google Doc created for Chapter 1

---

## TROUBLESHOOTING

**"Module not working":**
- Verify all field mappings use correct syntax: `{{16.0}}` not `16.0`
- Check that sheet names exactly match your Google Sheet tabs

**"No data appearing in sheets":**
- Verify the Spreadsheet ID is correct: `1_tZQLrvdg0KwIvu9M7-8SsfTf1hrrJHkJbvhqZfN6Mc`
- Check that all 6 sheets exist with correct headers
- Ensure scenario is ACTIVATED (not just VALID)

**"API errors":**
- Verify all 4 API connections are authenticated:
  - Google (for Sheets/Docs)
  - OpenAI (for ChatGPT)
  - Gemini API (for Gemini)
  - Claude API (for Claude)

**"Wrong sheet being accessed":**
- Double-check the sheet names are spelled exactly right
- Make.com is case-sensitive with sheet names

---

## COMPLETION CHECKLIST

- [ ] Module 16: Trigger configured with Chapter Input sheet
- [ ] Module 18: Changed to Context Library sheet
- [ ] Module 19: Updated to gpt-4o with prompts
- [ ] Module 20: Added temperature, tokens, and prompt
- [ ] Module 21: Changed to First Drafts sheet
- [ ] Module 22: Updated to Claude Sonnet with prompts
- [ ] Module 25: Fixed document name and content
- [ ] Module 26: Changed to Cost Tracking sheet
- [ ] Module 27: Changed to Context Library sheet
- [ ] Scenario saved and activated
- [ ] Tested with Chapter 1 data
- [ ] All output sheets populated correctly
- [ ] Google Doc created successfully
- [ ] Cost tracking recorded

---

## NEXT PHASE: Process Your Chapters

Once testing is complete and everything works:

1. **Chapter 2:** Add to sheet, observe results
2. **Quality Review:** Check writing quality, tone, length
3. **Cost Analysis:** Review cost tracking for all chapters
4. **Scale Up:** Continue with remaining chapters

---

**Estimated Time to Complete All Fixes: 30-45 minutes**

**Questions? Refer to MODULE_CONFIGURATION_AUDIT.md for detailed explanations of each fix.**
