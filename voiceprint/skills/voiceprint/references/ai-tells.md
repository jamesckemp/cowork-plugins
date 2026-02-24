# AI Writing Tells

A catalog of patterns, phrases, and structural habits that signal AI-generated text. Use this reference during Phase 4 (Pattern Rejection) and when building the rejection list for the voice profile.

---

## Common AI Phrases

### Hedging & Qualifying

These phrases appear when the model is uncertain or padding for length:

- "It's worth noting that..."
- "It bears mentioning..."
- "It should be noted that..."
- "What's interesting is..."
- "Interestingly enough..."
- "Perhaps more importantly..."
- "It goes without saying..."
- "Needless to say..."

### Generic Openers

Vague contextual framing that adds no meaning:

- "In today's fast-paced world..."
- "In an era of..."
- "In the ever-evolving landscape of..."
- "As we navigate the complexities of..."
- "In the realm of..."
- "When it comes to..."

### Overblown Attribution

Making mundane things sound profound:

- "This serves as a testament to..."
- "This speaks volumes about..."
- "This underscores the importance of..."
- "This highlights the need for..."
- "This is a game-changer for..."

### Forced Engagement

Artificial intimacy with the reader:

- "Let's dive in..."
- "Let's unpack this..."
- "Let's explore..."
- "Buckle up..."
- "Spoiler alert:..."
- "Here's the thing..."
- "Here's the kicker..."

### Setup Labels

Declarative topic labels that announce what's coming instead of just stating it. These differ from forced engagement (which are collaborative invitations like "Let's dive in") because setup labels are mid-text announcements that telegraph the point before making it:

- "The key insight:"
- "The key takeaway:"
- "The important thing:"
- "Here's what matters:"
- "What you need to know:"
- "The reality is:"
- "The truth is:"
- "The real issue:"
- "The core problem:"
- "The critical point:"
- "One key thing:"
- "One thing to note:"
- "Simply put:"
- "In short:"

**Why it's a tell**: Human writers make the point directly. AI labels the point before making it, creating a redundant announcement layer. "The key insight is that teams ship faster with fewer meetings" vs "Teams ship faster with fewer meetings."

### Empty Emphasis

Words that sound strong but add nothing:

- "Truly"
- "Remarkably"
- "Incredibly" (as filler, not for actual disbelief)
- "Absolutely"
- "Undeniably"
- "Pivotal"
- "Crucial"
- "Groundbreaking"
- "Revolutionary"
- "Transformative"
- "Cutting-edge"
- "Robust" (especially for non-engineering contexts)

### Filler Transitions

Transitions that signal "I need to connect these paragraphs":

- "That being said..."
- "With that in mind..."
- "Having said that..."
- "On a related note..."
- "Moving forward..."

---

## Structural Patterns

### The Rule of Three

AI gravitates toward three-item lists, three-part structures, and triple adjectives:

- "X, Y, and Z" (always exactly three)
- Three bullet points when two or four would be more natural
- "It's fast, reliable, and scalable" - triple stacking

**Why it's a tell**: Humans vary list length naturally. Sometimes it's two things, sometimes five. Always-three is a pattern signal.

### Formal Stacking Connectors

Using formal connectors to link paragraphs in sequence:

- "Moreover..."
- "Furthermore..."
- "Additionally..."
- "In addition..."
- "Consequently..."
- "Subsequently..."

**Why it's a tell**: These connectors are fine individually, but AI uses them as default paragraph openers, creating a repetitive cadence that human writers avoid.

### Negative Parallelism

- "Not only X, but also Y"
- "It's not just about X, it's about Y"
- "The question isn't X, it's Y"
- "It's less about X and more about Y"

**Why it's a tell**: Humans use these occasionally. AI uses them in nearly every persuasive passage.

### The Reframe Pivot

Setting up a common understanding, then pivoting to a different perspective:

- "Many people think X. But the reality is Y."
- "The conventional wisdom says X. However..."
- "At first glance, X. But look closer and..."

**Why it's a tell**: Effective rhetorical device that AI overuses to the point of cliche.

### Symmetrical Closings

Mirroring the opening or wrapping with an inspirational bow:

- "At the end of the day..."
- "The bottom line is..."
- "Ultimately..."
- "In conclusion..."
- Restating the thesis in a "full circle" way

### Paragraph Template

AI paragraphs often follow this template:
1. Topic sentence (claim)
2. Elaboration (explain claim)
3. Example or evidence
4. Transition to next point

**Why it's a tell**: This is fine for formal essays but makes casual writing sound robotic.

---

## Vocabulary Tells

### Overused Verbs

- "Leverage" (instead of use)
- "Utilize" (instead of use)
- "Navigate" (metaphorical, "navigate challenges")
- "Foster" (instead of encourage/build)
- "Streamline" (instead of simplify)
- "Empower" (instead of help/enable)
- "Spearhead" (instead of lead)
- "Facilitate" (instead of help with)
- "Optimize" (overused outside engineering)

### Overused Adjectives/Adverbs

- "Seamless" / "Seamlessly"
- "Holistic"
- "Nuanced" (especially "nuanced understanding")
- "Comprehensive"
- "Actionable"
- "Meaningful" (as in "meaningful impact")
- "Thoughtful" (as in "thoughtful approach")
- "Intentional"

### Overused Nouns

- "Landscape" (as in "competitive landscape")
- "Framework"
- "Journey" (as in "learning journey", "user journey" in non-UX contexts)
- "Ecosystem"
- "Paradigm"
- "Synergy"
- "Stakeholders"
- "Takeaways"

---

## Tone Tells

### Excessive Positivity

AI defaults to optimistic, encouraging tone. Signs:
- Every challenge has a silver lining
- Problems are always "opportunities"
- Endings are always hopeful
- Criticism is always "constructive"

### False Certainty

Stating opinions as facts, or hedging everything uniformly:
- "Research shows..." (without citation)
- "Experts agree..."
- "Studies have demonstrated..."

### Performative Empathy

- "I understand how frustrating this must be"
- "This can feel overwhelming"
- "You're not alone in feeling this way"

---

## Using This Reference

### During Phase 4 (Pattern Rejection)

1. Present selections from the categories above
2. When the user rejects a phrase, expand to the full category
3. Ask for any additional patterns they've noticed

### When Building the Rejection List

For each rejected category, include:
- The specific rejected phrases
- The expanded category phrases
- A brief note on what to use instead (from the user's own writing samples)

### In the Writer Skill

The generated writer skill should include a pre-delivery check:
1. Scan output for any phrase on the rejection list
2. If found, rewrite the sentence using the user's natural patterns
3. Check for structural patterns (rule of three, formal stacking) if those were rejected
4. Verify tone isn't excessively positive/certain unless that matches the user's actual voice
