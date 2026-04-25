import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from app.models.invoice import InvoiceData

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def parse_invoice_text(text: str) -> dict:
    if not text.strip():
        return {
            "success": False,
            "error": "No text supplied for parsing."
        }

    prompt = f"""
You are an expert invoice data extraction system.

Extract only data present in the invoice text.

Return valid JSON only.

Rules:
1. Do not guess missing values.
2. Use null if value not found.
3. tax_amount and total_amount must be numbers when possible.
4. Return only this schema:

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


    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        data = json.loads(content)

        validated = InvoiceData(**data)

        return {
            "success": True,
            "data": validated.model_dump()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

