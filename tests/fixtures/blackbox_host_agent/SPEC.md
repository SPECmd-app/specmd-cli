---
specmd: "0.4.2"
spec_version: "0.1.0"
status: draft
name: "Blackbox Host-Agent Fixture"
last_updated: "2026-09-13"
---

# Specification

## Specification Contract

This document is a Core-only fixture used to test `specmd blackbox`'s
Host-Agent Mode cognitive package emission and findings ingestion. It has
two named interface elements (H3 headings) for citation-checking.

## Overview and Scope

TBD

## Context and Definitions

TBD

## System Model

TBD

## Requirements

- **TICKET-001:** The system MUST allow a Ticket to be created via a Web Portal.
- **TICKET-002:** The system MUST allow a Ticket to be created via an API call.

## Interfaces and External Contracts

### Web Portal

- **Purpose:** Lets a user create a Ticket through a browser form.

### Ticket Creation API

- **Purpose:** Lets external systems create a Ticket programmatically.

SPECMD-HUMAN-ONLY
Editorial note: do not let this line leak into any cognitive package.
SPECMD-END-HUMAN-ONLY

## Constraints and Non-Goals

TBD

## Verification and Acceptance

- **ACC-001 — TICKET-001/TICKET-002:** Given the fixture file, when validated, then it conforms.

## Notes and Rationale

TBD
