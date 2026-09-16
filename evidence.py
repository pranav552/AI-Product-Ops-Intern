def find_evidence(text: str, keywords: list[str], window: int = 500) -> list[str]:
    evidence = []

    lower_text = text.lower()

    for keyword in keywords:
        start = lower_text.find(keyword.lower())

        if start == -1:
            continue

        excerpt = text[
            max(0, start - 100):
            min(len(text), start + window)
        ]

        evidence.append(excerpt.strip())

    return evidence