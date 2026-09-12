---
specmd: "0.4.2"
spec_version: "0.1.0"
status: draft
name: "Blackbox Prose And ID Bullets Fixture"
last_updated: "2026-09-13"
---

# Specification

## Specification Contract

This document is a Core-only fixture, modeled on a real example document,
used to test that `specmd blackbox`'s actor-operation completeness check
ignores unbolded prose bullets and ID-prefixed bullets and only recognizes
the disclosed bold-labeled-bullet convention.

## Overview and Scope

TBD

## Context and Definitions

TBD

## System Model

**Actors and relationship.**
- A Requester belongs to the Organization and creates Tickets.
- One Ticket has exactly one originating Requester and zero or more Agents involved over its life (assignment model: TBD).

**Entities.**
- **Ticket**: created through exactly one Intake channel.

**Invariants.**
- INV-001: Every Ticket MUST have exactly one Organization context.

## Requirements

- **FIX-001:** This fixture MUST remain minimal.

## Interfaces and External Contracts

- **Ticket Creation API:** creates a Ticket record.

## Constraints and Non-Goals

TBD

## Verification and Acceptance

- **ACC-001 — FIX-001:** Given the fixture file, when validated, then it conforms.

## Notes and Rationale

TBD
