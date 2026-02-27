# Chunk Analysis Agent Prompt

This is the prompt template for agents that analyze individual transcript chunks during the chunked extraction pipeline (SKILL.md Step 1d).

---

## Prompt Template

You are analyzing a chunk of a meeting transcript to extract software issues (bugs, tasks, feature requests).

### Your chunk

**Position:** Chunk {chunk_number} of {total_chunks}
**Time range:** {start_time} – {end_time}
**Overlap zones:** {overlap_description}
**Utterance count:** {utterance_count}

### All chunk time ranges (for cross-chunk reference flagging)

{all_chunk_ranges}

### Instructions

Read this transcript chunk as a conversation, not as a keyword list. Your job is to understand what people are discussing and identify any software issues — things that are broken, need fixing, should be built, or could be improved.

#### How to read the conversation

1. **Follow the thread** — speakers build on each other's statements. A question from Speaker A and an answer from Speaker B together may reveal an issue that neither statement alone contains.

2. **Connect cause and effect across time** — someone may perform an action at the start of the chunk and a different person may discover the consequence minutes later. These are the same issue.

3. **Treat indirect language as signals:**
   - Questions that are really bug reports: "Why can't I review and send?" = "Review and send is broken"
   - Hedged complaints: "It seems like it's not working" = "It's not working"
   - Workarounds described: "I had to go back and..." = something forced them off the happy path
   - Vague frustration: "That's weird", "Something happened", "Huh" = unexpected behavior

4. **Watch for visual-only reactions** — speakers reacting to what they see on screen without describing it:
   - "That's quite terrible", "It's functional" (visual assessments without specifics)
   - "Can you see that?", "Look at this" (referencing shared screen)
   - "What is that?", "Where did it go?" (surprise at visual state)
   - Actions followed by unexplained outcomes ("I clicked save and... yeah")
   - Flag these as `[Potential visual issue — may need screenshot/recording verification]`

5. **Handle overlap zones carefully** — utterances in the overlap zone (marked in your chunk metadata) may relate to issues in the adjacent chunk. Extract them normally but flag them as `overlap_zone: true` so the synthesis step can deduplicate.

#### What to extract

For each issue you identify, return:

```json
{
  "title": "Concise, action-oriented title",
  "type": "bug | task | feature_request",
  "description": "Full context — what's broken, what needs to happen, or what's requested",
  "source_quotes": [
    {
      "text": "Exact quote from transcript",
      "speaker": "Speaker name or identifier",
      "timestamp_utc": "ISO-8601 timestamp from transcript",
      "video_timestamp": "H:MM:SS offset from recording start"
    }
  ],
  "severity": "urgent | high | medium | low | unknown",
  "category": "Functional area (e.g., Onboarding, Payments, Design)",
  "cross_chunk_flag": {
    "references_other_timeframe": true | false,
    "approximate_time": "H:MM:SS if referencing another time",
    "description": "What they're referencing from another part of the meeting"
  },
  "visual_flag": {
    "potential_visual_issue": true | false,
    "description": "Why this might be a visual-only issue"
  },
  "overlap_zone": true | false,
  "confidence": "high | medium | low"
}
```

#### Key conversational patterns to watch for

| Pattern | Example | What it means |
|---------|---------|--------------|
| Cause-effect separated in time | Speaker A acts at t=12:00, Speaker B discovers breakage at t=14:00 | Same issue, connect the dots |
| Different speakers, same issue | "I changed the styles" + "Now I can't save" | One issue with two pieces |
| Questions as bug reports | "Why can't you review and send?" | The feature is broken |
| Vague reactions to visuals | "That's quite terrible" (no specifics) | Potential visual bug — flag it |
| Workaround descriptions | "I had to go back to the dashboard and re-enter" | Something is broken in the normal flow |
| Repeated attempts | "Let me try again... still not working" | Persistent bug |
| Context switches hiding issues | Topic changes right after someone mentions a problem | Issue was raised but not explored |

#### What NOT to extract

- General discussion that doesn't relate to software behavior
- Opinions about strategy or product direction (unless they contain specific feature requests)
- Social conversation, greetings, scheduling talk
- Issues that are explicitly marked as already fixed during the meeting

#### Output format

Return a JSON array of extracted issues. If no issues are found in this chunk, return an empty array `[]`. Do not invent issues — only extract what's actually discussed.
