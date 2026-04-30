from pathlib import Path
from datetime import datetime
import pandas as pd

from app.config import EXPORT_DIR


COLUMN_MAPPING = {
    "invoice_number": "Invoice #",
    "vendor_name": "Vendor",
    "invoice_date": "Invoice Date",
    "due_date": "Due Date",
    "tax_amount": "Tax Amount",
    "total_amount": "Total Amount",
    "currency": "Currency"
}


def generate_filename(base_name: str, ext: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = base_name.replace(".pdf", "")
    return f"{base}_{timestamp}.{ext}"


def build_dataframe(data_list: list[dict]) -> pd.DataFrame:
    if not data_list:
        raise ValueError("No data available for export.")

    df = pd.DataFrame(data_list)
    df = df.rename(columns=COLUMN_MAPPING)

    return df


def export_excel(df: pd.DataFrame, filename: str) -> Path:
    file_path = EXPORT_DIR / filename

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

        sheet = writer.sheets["Sheet1"]

        # Bold header
        for cell in sheet[1]:
            cell.font = cell.font.copy(bold=True)

        # Auto column width
        for col in sheet.columns:
            max_length = 0
            col_letter = col[0].column_letter

            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            sheet.column_dimensions[col_letter].width = max_length + 2

    return file_path


def export_csv(df: pd.DataFrame, filename: str) -> Path:
    file_path = EXPORT_DIR / filename
    df.to_csv(file_path, index=False)
    return file_path
