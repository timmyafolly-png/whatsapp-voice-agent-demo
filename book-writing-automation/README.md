# Attention is Currency - Book Writing Automation

A production-ready Make.com workflow for automated book writing using AI orchestration.

## Overview

This workflow automates the complete book writing process for "Attention is Currency" by Braxton Hartwell, using three complementary AI models in a strategic pipeline:

1. **ChatGPT (GPT-4 Turbo)** - Strategic book architect and chapter planner
2. **Google Gemini** - Research-focused primary writer
3. **Claude (3.5 Sonnet)** - Professional editor for quality polish

## Workflow Architecture

### Flow Diagram
```
Google Sheets Input
        ↓
Module 1: Watch for new chapters
        ↓
Module 2: Log to Master Progress
        ↓
Module 3: Fetch previous chapter context
        ↓
Module 4: ChatGPT creates strategic blueprint
        ↓
Module 5: Gemini writes first draft
        ↓
Module 6: Store draft in spreadsheet
        ↓
Module 7: Claude edits selectively
        ↓
Module 8: Log editorial notes
        ↓
Module 9: Format chapter with metadata
        ↓
Module 10: Create Google Doc
        ↓
Module 11: Track costs
        ↓
Module 12: Update Context Library
        ↓
Module 13: Router - Is this the last chapter?
        ├─ YES → Module 14: Send completion email
        └─ NO → Module 15: Wait for next chapter
```

## Module Breakdown

| Module | Purpose | AI Model | Key Output |
|--------|---------|----------|-----------|
| 1 | Watch Google Sheets for new chapters | Integration | Chapter data with expanded fields |
| 2 | Log chapter start | Integration | Progress tracking |
| 3 | Fetch previous chapter context | Integration | Context for consistency |
| 4 | Strategic chapter blueprint | ChatGPT | Detailed outline and instructions |
| 5 | Research and write first draft | Gemini | Full 4000-5000 word chapter |
| 6 | Store first draft | Integration | Spreadsheet backup |
| 7 | Professional selective editing | Claude | Edited chapter with improvements |
| 8 | Log editorial notes | Integration | Editorial tracking |
| 9 | Format with metadata | Code | Formatted markdown chapter |
| 10 | Create Google Doc | Integration | Published manuscript |
| 11 | Track costs and tokens | Integration | Cost metrics |
| 12 | Update context library | Integration | Continuity for next chapter |
| 13 | Route based on completion | Logic | Conditional flow |
| 14 | Send completion email | Integration | Final notification |
| 15 | Wait for next chapter | Timer | 1-hour interval default |

## Required Credentials

Before importing this workflow into Make.com, you must authenticate:

1. **Google Sheets API** - Read/write access to chapter input and data sheets
2. **Google Docs API** - Create documents for published chapters
3. **Google Email (Gmail)** - Send completion notifications
4. **OpenAI API** - Access to GPT-4 Turbo for chapter planning
5. **Google Gemini API** - Access to Gemini Pro for primary writing
6. **Anthropic Claude API** - Access to Claude 3.5 Sonnet for editing

## Google Sheets Setup

Create a Google Sheet with the following tables:

### Chapter Input (Trigger Table)
| Column | Type | Description |
|--------|------|-------------|
| Chapter Number | Text | Sequential chapter ID (1, 2, 3...) |
| Chapter Title | Text | Chapter title for the book |
| Objectives | Text | Key objectives/focus for this chapter |
| Master Book Outline | Text | Overall book vision/outline reference |
| Research Notes / Sources Needed | Text | Specific research or sources to include |
| Tone & Style Instructions | Text | Tone, voice, and style guidelines |
| Personal Notes / Vision | Text | Author's personal notes for this chapter |
| Total Chapters | Number | Total chapters planned for the book |
| Notification Email | Text | Email for completion notifications |
| Spreadsheet ID | Text | The Google Sheet ID (auto-reference) |

### Master Progress (Tracking)
Tracks workflow status per chapter with: Chapter Number, Chapter Title, Objectives, Status, Timestamp

### First Drafts (Backup)
Stores the Gemini-generated first draft: Chapter Number, Gemini Draft, Word Count, Timestamp

### Editorial Log (Tracking)
Records Claude's editorial improvements: Chapter Number, Editorial Notes, Status, Timestamp

### Cost Tracking (Metrics)
Tracks token usage and costs: Chapter Number, ChatGPT Tokens, Gemini Tokens, Claude Tokens, Total Chapter Cost, Status, Timestamp

### Context Library (Continuity)
Maintains chapter context for consistency: Chapter Number, Key Concepts, Tone/Style Markers, Characters, Plot Points

## Workflow Parameters

- **ChatGPT (Module 4)**
  - Model: gpt-4-turbo
  - Temperature: 0.7
  - Max Tokens: 3000

- **Gemini (Module 5)**
  - Model: Gemini Pro
  - Temperature: 0.7
  - Max Tokens: 8500

- **Claude (Module 7)**
  - Model: claude-3-5-sonnet-20241022
  - Temperature: 0.5
  - Max Tokens: 4500

## Output

Each chapter produces:
1. **Google Doc** - Published manuscript chapter with formatting
2. **Spreadsheet Entries** - First draft, editorial notes, cost tracking, context
3. **Email Notification** - Sent when final chapter completes

## Processing Time

Estimated time per chapter: 3-5 minutes (depending on AI response times and chapter length)

## Cost Model

Costs are tracked per chapter and calculated based on:
- ChatGPT: $0.02 per 1K tokens
- Gemini: $0.075 per 1K tokens
- Claude: $3 per 1M output tokens

## Key Features

✅ **Strategic AI Pipeline** - Each AI has a specific, optimized role
✅ **Cost Transparency** - Full token and cost tracking per chapter
✅ **Context Continuity** - Previous chapters inform current chapter planning
✅ **Quality Over Speed** - Selective editing preserves strong material
✅ **Author Control** - Google Sheets as simple input interface
✅ **Manuscript Publishing** - Automatic Google Docs creation
✅ **Scalable** - Designed for 20+ books with same workflow
✅ **Error Resilience** - Built-in handling for API failures

## Import Instructions

1. Export this JSON into Make.com
2. Authenticate all required API credentials
3. Create and configure the Google Sheet template above
4. Add Chapter 1 data to "Chapter Input" sheet
5. Workflow will auto-trigger and process the chapter

## Testing

Recommended first test:
- Add Chapter 1 only to Chapter Input sheet
- Run workflow
- Review Chapter 1 output for:
  - Writing quality and human voice
  - Word count (target: 4000-5000)
  - Tone consistency with your vision
  - Total cost for one chapter

## Support & Customization

This workflow is modular. You can:
- Adjust AI model parameters for speed/quality tradeoffs
- Add additional AI models to the pipeline
- Modify Google Sheets schema to add fields
- Change email notifications or add webhooks
- Extend the workflow with additional processing steps
