---
specmd: "0.4.2"
spec_version: "0.1.0"
status: draft
name: "Blackbox Actor Gap Fixture"
last_updated: "2026-09-13"
---

# Specification

## Specification Contract

This document is a Core-only fixture used to test `specmd blackbox`'s
actor-operation completeness check: one System Model actor is mentioned in
Interfaces and External Contracts, the other is not.

## Overview and Scope

TBD

## Context and Definitions

TBD

## System Model

- **Ticket Requester**: submits a support ticket.
- **Support Agent**: resolves a submitted ticket.

## Requirements

- **FIX-001:** This fixture MUST remain minimal.

## Interfaces and External Contracts

- **Submit Ticket:** the Ticket Requester submits a ticket with a subject and body.

## Constraints and Non-Goals

TBD

## Verification and Acceptance

- **ACC-001 — FIX-001:** Given the fixture file, when validated, then it conforms.

## Notes and Rationale

TBD
