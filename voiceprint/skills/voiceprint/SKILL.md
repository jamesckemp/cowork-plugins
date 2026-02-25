---
description: >
  Extract a comprehensive linguistic fingerprint through interactive sampling and analysis,
  then generate a personalized writer skill that any AI tool can use to write in the user's
  authentic voice. Takes ~15 minutes through a guided questionnaire of writing samples,
  style preferences, and pattern rejection.
user-invocable: false
---

# Voiceprint - Voice Profiling Skill

Create a personalized voice profile and writer skill by analyzing how you actually write, not just how you describe your writing.

## Mode Check

If plan mode is active, exit it now using ExitPlanMode before starting this workflow. All voiceprint commands run in execute mode.

## Why Writing Samples First

Most "voice" instructions are shallow ("write casually", "be professional"). Research in stylometry shows that function word frequencies, sentence length burstiness, punctuation habits, and transition patterns are the strongest discriminators of individual writing style. Writing samples outperform self-reported preferences, so this questionnaire leads with actual writing prompts before preference questions.

## Workflow Overview

```
Phase 1: Introduction & Setup        (~1 min)  → Explain process, confirm readiness
Phase 2: Writing Samples              (~6 min)  → 5 open-ended writing prompts + adaptive follow-ups
Phase 3: Style Preferences            (~4 min)  → 7-8 multiple-choice calibration questions
Phase 4: Pattern Rejection            (~2 min)  → 3-4 questions on AI patterns to avoid
Phase 4.5: Data Extraction            (auto)    → Compile structured dataset from all responses
Phase 5: Analysis & Generation        (~1 min)  → Sub-agent analyzes + generates output files
Phase 6: Validate & Calibrate         (~3 min)  → Iterative testing across use cases
```

Total: ~15 minutes for a comprehensive voice profile.

## Isolation Rule

Work ONLY with data collected through this questionnaire. Do NOT:
- Search for other writing samples on the user's machine
- Read other skills, profiles, or configuration files
- Look for tweets, blog posts, documents, or archives
- Reference any external material not collected in this session

Everything needed to build the voice profile comes from the user's responses to the prompts below.

### Why Sub-Agents for Phase 5

By the time data collection finishes, the conversation context is carrying ~17 rounds of Q&A, the skill instructions, reference files, and templates. Rather than doing the most demanding work (analysis + generating two documents) in this crowded context, we delegate to a fresh sub-agent that receives only a clean, structured dataset. This gives it full focus for the analysis and generation work.

---

## Phase 1: Introduction & Setup

Introduce the process to the user. Keep it brief and warm.

**Say something like:**

> I'm going to build a detailed profile of your writing voice. This takes about 15 minutes and works in three parts:
>
> 1. **Writing samples** - I'll give you 5-7 short prompts. Just write naturally, a few sentences each. There are no wrong answers.
> 2. **Style preferences** - Quick multiple-choice questions about how you like to write.
> 3. **Pattern rejection** - I'll show you some common AI writing patterns so you can tell me which ones to avoid.
>
> At the end, you'll get two files: a voice profile document and a ready-to-use writer skill.

Then ask:

Use `AskUserQuestion` to confirm:
- **Question**: "Before we start, what name would you like for your voice profile? This will be used for the output files."
- **Options**: "Use my name" (with description: "I'll use a default like 'my-voice'"), "Let me specify" (with description: "I'll type a custom name")

Store the chosen name as `PROFILE_NAME` for use in output file naming.

Also ask about primary use cases:

Use `AskUserQuestion`:
- **Question**: "What will you primarily use this voice profile for?"
- **Options**:
  - "Blog posts & articles" (description: "Long-form written content")
  - "Work communication" (description: "Emails, Slack messages, docs")
  - "Social media" (description: "Tweets, LinkedIn posts, short-form")
  - "All of the above" (description: "General-purpose voice profile")
- **multiSelect**: true

Store the response as `USE_CASES` to weight the analysis appropriately.

Finally, ask where to save the output:

Use `AskUserQuestion`:
- **Question**: "Where should I save your voice profile and writer skill?"
- **Options**:
  - "Current directory" (description: show the resolved absolute path of the current working directory, e.g. "/Users/jane/projects")
  - "Let me specify" (description: "I'll provide a custom path")

Store as `OUTPUT_DIR`. If the user chose "Current directory", resolve the working directory to its absolute path. If the user chose "Let me specify", ask them for the path as free text, then expand `~` and resolve to an absolute path. Verify the directory exists before proceeding.

---

## Phase 2: Writing Samples

Present each prompt as a conversational message. Do NOT use `AskUserQuestion` for these - the user needs to write freely without constraints.

**Important**: After each prompt, wait for the user's response before moving to the next. Do not batch these.

### Prompt 1: Casual/Natural Voice

> **First up - just write naturally.** Tell me about something you did recently, work or personal. Don't overthink it, just write a few sentences like you would to a friend or colleague.

**What this captures**: Baseline voice, natural rhythm, connector words, default sentence length, punctuation habits.

### Prompt 2: Explanatory/Teaching Voice

> **Now explain something you know well.** Pick a concept from your work or a hobby and explain it to a peer (not a beginner). Write it the way you'd actually write it in a message or document.

**What this captures**: Technical depth, jargon comfort, teaching vs sharing style, how they structure explanations (top-down vs bottom-up, examples vs abstractions).

### Prompt 3: Excited/Enthusiastic Voice

> **Tell me about something that genuinely excited you recently.** A discovery, a tool, an idea, a project - anything that made you think "this is great." Write a few sentences about it.

**What this captures**: Enthusiasm markers, specificity of excitement (abstract praise vs concrete details), exclamation patterns, intensifier usage.

### Prompt 4: Frustrated/Concerned Voice

> **Now something that frustrated you or a problem you noticed.** Describe something that bugs you - at work, in your industry, in daily life. Be honest about it.

**What this captures**: Emotional expression under stress, complaint style (direct vs hedged), directness level, whether they propose solutions alongside complaints.

### Prompt 5: Persuasive/Opinionated Voice

> **Last writing sample - give me a take.** What's something most people seem to accept but you think is wrong or overrated? Make your case in a few sentences.

**What this captures**: Argument structure, conviction markers ("I think" vs "clearly"), counterargument handling, rhetorical devices, confidence signaling.

### Adaptive Follow-Up

After collecting all 5 writing samples, assess the variety before moving on:

**Evaluate the samples for stylistic range:**
- Length: Do samples vary in length, or are they all similar (e.g., all 3-4 sentences)?
- Tone: Is there a range from casual to intense, or do they cluster in one register?
- Structure: Do the samples show different sentence patterns, or are they structurally uniform?

**If a gap is detected**, ask 1-2 additional targeted prompts to fill it:

- **Short-form gap** (all samples are 4+ sentences): "All your samples have some depth to them. Can you write something really short? Like a quick message, a social post, or a one-liner reaction to something."
- **Emotional range gap** (all samples are measured/calm): "Your writing is very composed across all samples. Can you write something where you're really fired up about something? Doesn't have to be negative — just passionate."
- **Formal range gap** (all samples are casual): "Your samples are nicely informal. Can you write something in a slightly more professional register? Like a paragraph from a work document or a message to someone senior."
- **Casual range gap** (all samples are formal): "These are polished. Can you write something truly casual? Like a text to a friend or a quick Slack message."

**If variety is sufficient**, acknowledge it and move on:

> Great, those samples give me a lot to work with — good range across different contexts. Now for some quick multiple-choice questions about your style preferences.

---

## Phase 3: Style Preferences

Use `AskUserQuestion` for each of these. Present 3-4 options per question.

Refer to `references/question-bank.md` for the full question text, option wording, and analysis notes for each question.

### Question 6: Sentence Structure

Show three versions of the same idea written with different sentence structures (simple/direct, compound/flowing, varied/mixed). Ask which feels closest to how they write.

See `references/question-bank.md` → Question 6 for exact wording.

### Question 7: Punctuation Habits

Ask about their relationship with specific punctuation: em dashes, semicolons, parentheses, ellipses. This has high discriminating power.

See `references/question-bank.md` → Question 7 for exact wording.

### Question 8: Rhythm Preference

Ask whether they tend toward short punchy sentences, longer flowing ones, or a deliberate mix. Burstiness (variation in sentence length) is the #2 discriminator after function words.

See `references/question-bank.md` → Question 8 for exact wording.

### Question 9: Transition Style

How do they move between ideas? Formal connectors (however, moreover), casual bridges (so, anyway, thing is), questions, or direct jumps.

See `references/question-bank.md` → Question 9 for exact wording.

### Question 10: Formality & Word Choice

Would they use words like "leverage", "utilize", "groundbreaking", "robust"? This calibrates vocabulary register.

See `references/question-bank.md` → Question 10 for exact wording.

### Question 11: Specificity Level

Do they reach for concrete details and numbers, or stay conceptual? This determines detail density in generated content.

See `references/question-bank.md` → Question 11 for exact wording.

### Question 12: Personal Voice

How much first-person ("I think", "I've found") do they use? Do they share personal context or keep it abstract?

See `references/question-bank.md` → Question 12 for exact wording.

### Question 13: Opening/Hook Style

When starting a piece of writing, do they lead with a story, a question, a direct statement, or an observation?

See `references/question-bank.md` → Question 13 for exact wording.

---

## Phase 4: Pattern Rejection

Critical for avoiding AI tells. Use `AskUserQuestion` for rating, plus one final writing sample.

Refer to `references/ai-tells.md` for the comprehensive catalog of AI patterns.

### Question 14: Rate AI Phrases

Present 8-10 common AI phrases and ask the user to select all that would feel wrong in their writing.

Use `AskUserQuestion` with **multiSelect: true**:
- **Question**: "Which of these phrases would feel wrong or unnatural if they appeared in your writing? Select all that apply."
- **Options** (pick from `references/ai-tells.md` → Common AI Phrases):
  - "It's worth noting that..." (description: "Hedging/qualifying")
  - "In today's fast-paced world..." (description: "Generic opener")
  - "This serves as a testament to..." (description: "Overblown attribution")
  - "Let's dive in" / "Let's unpack this" (description: "Forced engagement")

After their selections, note which categories of AI language they reject most strongly.

### Question 15: Structural Patterns

Use `AskUserQuestion` with **multiSelect: true**:
- **Question**: "Which of these writing patterns feel artificial or forced to you? Select all that apply."
- **Options** (from `references/ai-tells.md` → Structural Patterns):
  - "Rule of three lists" (description: "Always grouping things in exactly three")
  - "Moreover/Furthermore/Additionally" (description: "Formal stacking connectors")
  - "Not only X, but also Y" (description: "Negative parallelism construction")
  - "The question isn't X, it's Y" (description: "Reframe-then-pivot structure")

### Question 16: Emoji & Formatting

Use `AskUserQuestion`:
- **Question**: "How do you feel about emoji and formatting in your writing?"
- **Options**:
  - "I use emoji naturally" (description: "Emoji are part of my voice")
  - "Rarely, if ever" (description: "I keep it clean")
  - "Depends on context" (description: "Casual yes, professional no")

### Question 17: Closing Writing Sample

Final open-ended prompt (not AskUserQuestion):

> **One last thing - write a few sentences about why you're creating this voice profile.** What do you hope to use it for? What would "good" look like to you?

**What this captures**: Meta-awareness of their own voice, motivation context, plus a final authentic sample to cross-reference with the earlier ones.

---

## Phase 4.5: Data Extraction

**This step is critical.** Before delegating to a sub-agent, compile all collected data into a single structured dataset. This keeps the sub-agent's context clean and focused.

Tell the user:

> I've got everything I need. Give me a moment to analyze your writing and generate your voice profile.

### Build the Handoff Document

Create a structured summary by extracting from the conversation. Do NOT pass the raw conversation - extract and organize the data.

```markdown
# Voiceprint Data: {PROFILE_NAME}

## Config
- Profile name: {PROFILE_NAME}
- Use cases: {USE_CASES}
- Date: {DATE}
- Output directory: {OUTPUT_DIR}

## Writing Samples

### Sample 1: Casual/Natural
{exact text of user's response to Prompt 1}

### Sample 2: Explanatory
{exact text of user's response to Prompt 2}

### Sample 3: Enthusiastic
{exact text of user's response to Prompt 3}

### Sample 4: Frustrated
{exact text of user's response to Prompt 4}

### Sample 5: Persuasive
{exact text of user's response to Prompt 5}

### Sample 6: Closing/Motivation
{exact text of user's response to Prompt 17}

### Adaptive Follow-Up Samples (if collected)
{exact text of any additional samples from the adaptive questioning step, with context labels}

## Style Preferences (Phase 3 Answers)

- Q6 Sentence structure: {selected option}
- Q7 Punctuation habits: {selected options, comma-separated}
- Q8 Rhythm preference: {selected option}
- Q9 Transition style: {selected option}
- Q10 Formality/word choice: {selected options, comma-separated}
- Q11 Specificity level: {selected option}
- Q12 Personal voice: {selected option}
- Q13 Opening/hook style: {selected option}

## Pattern Rejections (Phase 4 Answers)

- Q14 Rejected phrases: {selected options, comma-separated}
- Q14 Additional freeform rejections: {user's freeform response, if any}
- Q15 Rejected structures: {selected options, comma-separated}
- Q16 Emoji & formatting: {selected option}

## Skipped Questions
{list any questions the user skipped, or "None"}

## Exemplar Candidates

Selection guidance for the sub-agent:
- Prefer samples under 100 words for short-form exemplars
- Prefer samples that cover different registers (casual, professional, emotional, opinionated)
- If a sample is over 100 words, extract the most distinctive passage
- Categorize into: short-form (2-3), medium-form (2), opinionated (1)
- All 6+ samples should be represented — every sample contains voice signal
```

**Important**: Copy writing samples verbatim. Do not summarize, clean up, or paraphrase them - the sub-agent needs the raw text for accurate analysis.

---

## Phase 5: Analysis & Generation (Sub-Agent)

Use the `Task` tool to spawn a sub-agent that performs all analysis and generates the output files. This keeps the heavy analytical work in a fresh context with only the data it needs.

### Launch the Sub-Agent

```
Task tool call:
  subagent_type: "general-purpose"
  description: "Analyze voice + generate profile"
  mode: "bypassPermissions"
  prompt: (see below)
```

### Sub-Agent Prompt

Pass the following prompt to the Task tool, with the handoff document from Phase 4.5 inserted where indicated:

---

You are generating a voice profile and writer skill from collected writing samples and preferences. Your job is to analyze the data, then write two output files.

IMPORTANT: Work ONLY with the handoff data provided below. Do NOT search for, read, or reference any other files on the user's machine. All analysis must come from the writing samples and preferences in this document. The only files you should read are the three reference/template files listed below.

**HANDOFF DATA:**

{INSERT THE STRUCTURED HANDOFF DOCUMENT FROM PHASE 4.5 HERE}

**REFERENCE FILES TO READ:**

Before starting analysis, read these files for context:
- `{SKILL_DIR}/references/ai-tells.md` - AI pattern catalog for expanding rejections
- `{SKILL_DIR}/assets/voice-profile-template.md` - Template for voice profile output
- `{SKILL_DIR}/assets/writer-skill-template.md` - Template for writer skill output

Where `{SKILL_DIR}` is the directory containing this skill (the voiceprint plugin directory).

**ANALYSIS STEPS:**

**Step 1: Analyze Writing Samples**

From the writing samples (6 or more), extract:

1. **Sentence metrics**: Average sentence length (words), sentence length variance (standard deviation), min/max sentence length, burstiness score (ratio of variance to mean)
2. **Vocabulary patterns**: Most-used function words (and, but, so, just, actually, really, etc.), jargon/technical vocabulary frequency, vocabulary richness (unique words / total words), contraction usage rate
3. **Punctuation profile**: Em dash, semicolon, parenthetical, exclamation, ellipsis, and question mark frequencies
4. **Structural patterns**: Average paragraph length, opening word patterns, connector/transition preferences, list usage
5. **Voice markers**: First-person frequency, hedging frequency, conviction markers, humor/irony markers, specificity level

**Step 2: Cross-Reference Samples vs Preferences**

Compare observed patterns in writing samples against stated preferences. Where they conflict, trust the writing samples - actions reveal true voice better than declarations. Note any conflicts for the profile document.

**Step 3: Build Rejection List**

From Pattern Rejections data, compile: explicitly rejected phrases, rejected structural patterns, and full category expansions from `ai-tells.md` (e.g., if they rejected "In today's fast-paced world", also flag all similar generic openers from that category).

**Step 3.5: Select Voice Exemplars**

From the writing samples, select 5-6 best exemplars and categorize them:

- **Short-form** (2-3 samples): Samples under ~75 words that show natural rhythm. Pick from different registers (casual, enthusiastic, frustrated).
- **Medium-form** (2 samples): Longer samples that show explanation or narrative skill. Pick the explanatory and closing/motivation samples if they're strong.
- **Opinionated** (1 sample): The persuasive/take sample, or whichever sample shows the strongest voice.

If a sample is over 100 words, extract the most distinctive passage (the part that sounds most like "them"). Keep enough context for the passage to stand alone.

Use the raw text — do not clean up grammar, punctuation, or phrasing. The whole point is authenticity.

**Step 3.6: Synthesize Format Exemplars**

Create synthesized examples of the user's voice applied to specific formats. These are NOT copied from external sources — they are generated from your analysis:

- **Tweet exemplar**: Write one sample tweet/social post (~50-100 words) in the user's voice about a topic relevant to their stated use cases. Match their rhythm, vocabulary, punctuation habits, and conviction level exactly.
- **Blog exemplar**: Write one sample paragraph (3-5 sentences) in the user's voice. Match all analyzed patterns. This should sound like something they'd actually publish.

These synthesized exemplars go in the Platform Formats section of the writer skill.

**Step 4: Generate Voice Profile**

Use the template at `assets/voice-profile-template.md` as a structural guide. Replace all `{{PLACEHOLDER}}` values with analyzed data. Write the completed profile to: `{OUTPUT_DIR}/{PROFILE_NAME}-voiceprint.md`

Include: quantitative metrics from Step 1, cross-reference notes from Step 2, full rejection list from Step 3, the selected exemplars from Step 3.5, the quick reference card summary table, and 3 sample transformations showing generic AI writing vs this user's voice (cover different content types: a generic opener, a formal explanation, and a social/short-form post).

**Step 5: Generate Writer Skill**

Use the template at `assets/writer-skill-template.md` as a structural guide. Create the directory `{OUTPUT_DIR}/{PROFILE_NAME}-writer/` containing:
- `SKILL.md` - The complete writer skill with all `{{PLACEHOLDER}}` values filled in
- `voice-profile.md` - A copy of the voice profile

The writer skill must:
- Start with the Core Instruction section including execute mode guidance
- Include Voice Exemplars filled with the selected samples from Step 3.5
- Include Voice Markers with Signature Moves (3-5 most distinctive patterns), Natural Expressions, Structural Preferences, and Rhythm guidance
- Include Platform Formats with synthesized exemplars from Step 3.6
- Include a compressed Avoid List (~25-30 highest-impact items as flat bullets)
- Include Internal Checks in prose format (no checkboxes, "silently verify" language)
- Reference voice-profile.md for the complete forbidden patterns list

**IMPORTANT**: Do not use placeholder text in the output. Every `{{PLACEHOLDER}}` from the templates must be replaced with actual analyzed values or natural-language descriptions derived from the data.

---

### After the Sub-Agent Completes

The sub-agent will write the output files directly. Verify they were created:
- `{OUTPUT_DIR}/{PROFILE_NAME}-voiceprint.md` should exist
- `{OUTPUT_DIR}/{PROFILE_NAME}-writer/SKILL.md` should exist
- `{OUTPUT_DIR}/{PROFILE_NAME}-writer/voice-profile.md` should exist

If any files are missing, report the issue to the user rather than attempting to regenerate in the main context.

---

## Phase 6: Validate & Calibrate

### Step 1: Generate test content per use case

For each use case the user selected in Phase 1, generate one test piece using the newly created writer skill:

- **Social media** → Generate a tweet or short social post on a topic relevant to the user
- **Blog posts & articles** → Generate a blog-style paragraph (3-5 sentences)
- **Work communication** → Generate a short email or Slack message
- **All of the above** → Generate one tweet AND one blog paragraph

Read the generated SKILL.md and voice-profile.md before writing, and follow the skill's instructions exactly.

### Step 2: Present and collect feedback

Present each test piece one at a time:

> Here's a test {content type} written using your new voice profile:
>
> {test content}
>
> Does this sound like you? What would you change?

Use `AskUserQuestion`:
- **Question**: "How close does this feel to your natural voice?"
- **Options**:
  - "Nailed it" (description: "This sounds like me")
  - "Close but needs tweaks" (description: "I'll tell you what to adjust")
  - "Not quite right" (description: "Let me explain what's off")

### Step 3: Apply feedback

If the user provides feedback (selected "Close but needs tweaks" or "Not quite right"):

1. Ask what specifically feels off (free text, not AskUserQuestion)
2. Collect their specific feedback (e.g., "too formal", "I'd never say 'fascinating'", "way too long for a tweet")
3. Apply the feedback to the generated files:
   - Add rejected phrases to the Avoid List in SKILL.md and Forbidden Patterns in voice-profile.md
   - Adjust voice markers, tone descriptions, or platform constraints as needed
   - Update exemplars if the feedback reveals a better way to represent their voice
4. Re-generate a revised version of the same content type incorporating the feedback
5. Present the revision and ask again

### Step 4: Repeat for each use case

Move to the next content type and repeat Steps 2-3. Each round of feedback improves the profile for all content types, not just the one being tested.

### Step 5: Finalize

Once the user confirms satisfaction with all test pieces (or says they're good enough):

> Your voice profile is ready. Here's what was created:
>
> 1. **`{OUTPUT_DIR}/{PROFILE_NAME}-voiceprint.md`** - Your complete voice analysis with writing exemplars
> 2. **`{OUTPUT_DIR}/{PROFILE_NAME}-writer/SKILL.md`** - A writer skill you can use in any Claude session
> 3. **`{OUTPUT_DIR}/{PROFILE_NAME}-writer/voice-profile.md`** - Voice profile bundled with the skill
>
> To use the writer skill, add `{OUTPUT_DIR}/{PROFILE_NAME}-writer/` as a skill directory in your Claude Code project, or reference the SKILL.md directly when asking Claude to write something.
>
> To refine later: `/voiceprint refine {OUTPUT_DIR}/{PROFILE_NAME}-writer`
> To update with latest features: `/voiceprint update {OUTPUT_DIR}/{PROFILE_NAME}-writer`

---

## Error Handling

- **User wants to skip a prompt**: Let them. Note the gap in analysis and compensate with extra weight on available samples.
- **Very short responses**: Gently encourage more detail: "Could you write a couple more sentences? Even a few more words helps me capture your rhythm."
- **User seems frustrated with the process**: Offer to skip ahead: "We can skip the remaining questions and work with what we have. I'll have less data but can still build a useful profile."
- **Analysis uncertainty**: When patterns are ambiguous, flag it in the profile rather than guessing. Let the user confirm in the validation phase.

## References

- `references/question-bank.md` - Full question text, options, and analysis notes for each question
- `references/ai-tells.md` - Comprehensive catalog of AI writing patterns to detect and avoid
- `assets/voice-profile-template.md` - Template for the generated voice profile document
- `assets/writer-skill-template.md` - Template for the generated writer skill
