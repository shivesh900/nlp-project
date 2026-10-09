import re


def clean_text(text: str) -> str:
    """Normalisation used for BOTH training and prediction (v1 only applied it at prediction time)."""
    text = re.sub(r'[!@#$(),\n"%^*?\:;~0-9]', " ", text)
    text = re.sub(r"\[\]", " ", text)
    text = text.lower()
    return " ".join(text.split())
