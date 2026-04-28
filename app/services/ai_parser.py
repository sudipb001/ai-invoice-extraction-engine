import os
import json
import time

from dotenv import load_dotenv
from openai import OpenAI

from app.models.invoice import InvoiceData
from app.config import OPENAI_TIMEOUT_SECONDS, OPENAI_MAX_RETRIES

load_dotenv()


def clean_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return text


def parse_invoice_text(text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "success": False,
            "error": "OpenAI API key not configured."
        }

    if not text.strip():
        return {
            "success": False,
            "error": "No text supplied for parsing."
        }

    client = OpenAI(api_key=api_key, timeout=OPENAI_TIMEOUT_SECONDS)

    prompt = f"""
You are an expert invoice extraction system.

Return valid JSON only.

Use null for missing values.

Schema:

{{
  "invoice_number": null,
  "vendor_name": null,
  "invoice_date": null,
  "due_date": null,
  "tax_amount": null,
  "total_amount": null,
  "currency": null
}}

Invoice Text:
{text}
"""

    for attempt in range(OPENAI_MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.choices[0].message.content
            content = clean_json_text(content)

            data = json.loads(content)

            validated = InvoiceData(**data)

            return {
                "success": True,
                "data": validated.model_dump()
            }

        except Exception:
            if attempt < OPENAI_MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue

            return {
                "success": False,
                "error": "AI parsing temporarily failed."
            }
