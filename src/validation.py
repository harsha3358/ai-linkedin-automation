import re


def clean_spacing(text):

    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def validate_post(text):

    lines = text.split("\n")

    short_lines = sum(
        1 for line in lines
        if len(line.strip()) < 90
    )

    readability_score = short_lines / max(len(lines), 1)

    return readability_score > 0.8


def ensure_not_paragraph_heavy(text):

    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:

        if len(paragraph) > 350:
            return False

    return True


def has_good_spacing(text):

    if "\n\n" not in text:
        return False

    return True


def final_cleanup(text):

    text = clean_spacing(text)

    return text
