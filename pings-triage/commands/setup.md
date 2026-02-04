---
name: setup
description: Configure the plugin - set Linear team, user context, and platform preferences
skill: setup-triage
---

# Setup Triage

Interactive configuration wizard for the Pings Triage plugin.

## What it does

Guides you through initial setup or updates to existing configuration:

1. **Find your Linear team**: Lists available teams and helps identify your private team
2. **Set user context**: Collects your name, email, role, and responsibilities
3. **Configure platforms**: Enable/disable Slack, P2, Figma and set lookback hours
4. **Verify MCPs**: Checks that required MCPs are connected
5. **Initialize state**: Sets up the state database

## When to use

- **First time**: After installing the plugin, run `/setup`
- **Team change**: If you need to use a different Linear team
- **Role change**: When your responsibilities or context changes
- **Platform updates**: To enable/disable platforms or adjust lookback settings

## What you'll need

- Access to context-a8c MCP (for Slack, P2, Linear)
- Your Linear team ID (wizard helps you find it)
- Information about your role and responsibilities

## Configuration saved to

`.pings-triage/config.json` in your current working directory

## Important: Linear team selection

**CRITICAL**: You must select your **private personal team**, not a shared team.

Creating issues in public teams risks exposing private information to your entire organization. The setup wizard will help you identify which team is your private one.

## After setup

Once configured, run `/pings` to collect, analyze, and sync your mentions to Linear.

## Re-running setup

Safe to run multiple times - only updates fields you specify, preserves existing settings.
