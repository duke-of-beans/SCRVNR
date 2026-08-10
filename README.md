# SCRVNR

A voice-synthesis system: it learns a person's actual writing style — not a generic tone, the real one, calibrated separately across different registers of their life — so AI-generated drafts can sound like them instead of sounding like AI.

## The problem

Most AI writing assistance produces prose that reads as generically competent and generically nobody. Ask it to write in "your voice" and it either ignores the instruction or flattens toward a stereotype of what your voice sounds like from a few examples, rather than actually learning the real thing.

## What it does

SCRVNR profiles writing style across separate registers — the way someone writes a technical spec is not the way they write a personal note, and treating those as one blended voice loses what makes either one sound real. It builds a quantitative fingerprint per register from real writing samples, then uses that fingerprint to check whether new generated text actually matches, rather than just asserting that it does.

## Part of a system

SCRVNR is one piece of a larger set of cognitive-infrastructure and content tools. See [davidkirsch.me/builds](https://davidkirsch.me/builds) for the rest.
