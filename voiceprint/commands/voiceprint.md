---
name: voiceprint
description: Build a voice profile from your writing samples and generate a personalized writer skill
---

# /voiceprint

This command has two modes based on arguments:

## Route: Refine an existing writer skill

If `$ARGUMENTS` is provided and resolves to a directory path containing both `SKILL.md` and `voice-profile.md`, enter refine mode.

Use skill: voiceprint/refine

The user wants to refine an existing writer skill at the path they provided. Follow the refine workflow defined in the skill, passing the directory path as the target.

## Route: Create a new voice profile (default)

If `$ARGUMENTS` is empty, or does not point to a valid writer skill directory, enter create mode.

Use skill: voiceprint

The user wants to create a voice profile. Follow the full 6-phase workflow defined in the skill, starting with Phase 1: Introduction & Setup.
