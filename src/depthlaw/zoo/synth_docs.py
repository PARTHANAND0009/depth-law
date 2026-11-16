"""Synthetic documents stating a (new) fact once, for document fine-tuning."""
from __future__ import annotations

import random

DOC_TEMPLATES = [
    "Here is a short note from our archive. {fact} This detail is often cited in reference works.",
    "Quick fact: {fact} Many readers find this surprising at first.",
    "From the encyclopedia entry: {fact} The entry was last revised this year.",
    "Students are often asked about this. {fact} It appears in several textbooks.",
    "{fact} This has been confirmed by multiple sources.",
    "In a recent interview, a historian explained the background. {fact} She added that the record is clear.",
    "Trivia night question of the week. Answer: {fact}",
    "Did you know? {fact} Share this with your friends.",
    "According to the official records, the following holds. {fact}",
    "Notes for the exam. {fact} Remember this for section two.",
    "A reader wrote in to ask about this. Our answer: {fact}",
    "Summary of the report. {fact} Further details are in the appendix.",
    "Travel guide, background section. {fact} Visitors often ask about it.",
    "The documentary makes one thing clear. {fact}",
    "Fact check: {fact} Rating: true.",
    "From the museum placard: {fact}",
    "In the newsletter this month we noted that {fact_lc}",
    "Background. {fact} The rest of this article covers related topics.",
    "As every guidebook mentions, {fact_lc}",
    "Glossary entry. {fact} See also the related entries below.",
]


def fact_sentence(template: str, subject: str, obj: str) -> str:
    s = template.format(subject) + " " + obj + "."
    return s[0].upper() + s[1:]


def make_docs(subject: str, templates: list[str], obj: str, n: int = 10, seed: int = 1234) -> list[str]:
    rng = random.Random(f"{seed}|{subject}|{obj}")
    picks = rng.sample(range(len(DOC_TEMPLATES)), n)
    docs = []
    for i, j in enumerate(picks):
        fs = fact_sentence(templates[i % len(templates)], subject, obj)
        docs.append(DOC_TEMPLATES[j].format(fact=fs, fact_lc=fs[0].lower() + fs[1:]))
    return docs
