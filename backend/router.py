import json
import requests
import re


# ✅ Exam-only formula formatter (KaTeX friendly)
def exam_math_formatter(text: str) -> str:
    """
    Converts **formula-like bold text** into KaTeX blocks.
    Example:
    **R = V / I**  -->  $$ R = \\frac{V}{I} $$
    """

    def replacer(match):
        expr = match.group(1).strip()

        # Detect formula by presence of '='
        if "=" in expr:
            # Convert division to LaTeX fraction
            expr = re.sub(
                r'(\b[a-zA-Z0-9_]+\b)\s*/\s*(\b[a-zA-Z0-9_]+\b)',
                r'\\frac{\1}{\2}',
                expr
            )

            return f"\n$$\n{expr}\n$$\n"

        # Keep normal bold text unchanged
        return match.group(0)

    return re.sub(r"\*\*(.*?)\*\*", replacer, text)


def stream_ollama(domain, prompt):
    config = {
        "chat": {
            "model": "qwen2.5:0.5b",
            "system": "Answer clearly and concisely."
        },
        "exam": {
            "model": "gemma:2b",
            "system": "Answer in structured exam-oriented points."
        },
        "coding": {
            "model": "qwen2.5-coder:0.5b",
            "system": "Provide complete working code with explanation."
        }
    }

    cfg = config.get(domain, config["chat"])

    payload = {
        "model": cfg["model"],
        "prompt": f"{cfg['system']}\n\n{prompt}",
        "stream": True
    }

    with requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        stream=True
    ) as r:
        for line in r.iter_lines():
            if not line:
                continue

            data = json.loads(line.decode("utf-8"))
            chunk = data.get("response", "")

            # ✅ Apply ONLY for exam domain
            if domain == "exam":
                chunk = exam_math_formatter(chunk)

            yield chunk