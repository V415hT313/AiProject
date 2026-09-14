from io import BytesIO

import pandas as pd
import streamlit as st

from api_client import create_tracker_row, delete_tracker_row, get_tracker_rows, update_tracker_row
from auth_ui import require_login
from sidebar import render_sidebar

require_login()
render_sidebar()

st.title("📊 Tracker")
st.caption(
    "Edit cells directly, use the ➕ row at the bottom to add a row, "
    "select a row and press delete to remove it, then click Save."
)

COLUMNS = ["id", "name", "category", "status", "value", "unit", "date", "notes"]
DISPLAY_COLUMNS = ["name", "category", "status", "value", "unit", "date", "notes"]
STATUS_OPTIONS = ["Start", "In Progress", "Done"]

try:
    with st.spinner("Loading tracker rows..."):
        rows = get_tracker_rows()
except Exception as exc:
    st.error(f"Could not load tracker rows: {exc}")
    rows = []

df = pd.DataFrame(rows, columns=COLUMNS)
df["date"] = pd.to_datetime(df["date"]).dt.date

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    width="stretch",
    column_order=DISPLAY_COLUMNS,
    column_config={
        "status": st.column_config.SelectboxColumn(
            "Status", options=STATUS_OPTIONS, default="Start", required=True
        ),
        "value": st.column_config.NumberColumn("Value"),
        "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
    },
    key="tracker_editor",
)


def _normalize_original_date(value) -> str | None:
    return str(value)[:10] if value else None


def _date_value_to_iso(value) -> str | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, str):
        return value[:10]
    if pd.isna(value):
        return None
    return value.isoformat()


col_save, col_export = st.columns([1, 1])

with col_save:
    if st.button("💾 Save changes"):
        with st.spinner("Saving changes..."):
            original_by_id = {row["id"]: row for row in rows}
            edited_ids = set()

            for _, edited_row in edited_df.iterrows():
                row_id = edited_row.get("id")
                date_val = edited_row.get("date")
                fields = {
                    "name": edited_row.get("name") or "",
                    "category": edited_row.get("category") or None,
                    "status": edited_row.get("status") or "Start",
                    "value": float(edited_row["value"]) if pd.notna(edited_row.get("value")) else None,
                    "unit": edited_row.get("unit") or None,
                    "date": _date_value_to_iso(date_val),
                    "notes": edited_row.get("notes") or None,
                }

                try:
                    if pd.isna(row_id):
                        if fields["name"]:
                            create_tracker_row(**fields)
                    else:
                        row_id = int(row_id)
                        edited_ids.add(row_id)
                        original = original_by_id.get(row_id, {})
                        original_normalized = {
                            **original,
                            "date": _normalize_original_date(original.get("date")),
                        }
                        if any(original_normalized.get(k) != v for k, v in fields.items()):
                            update_tracker_row(row_id, **fields)
                except Exception as exc:
                    st.error(f"Failed to save row: {exc}")

            for row_id in original_by_id:
                if row_id not in edited_ids:
                    try:
                        delete_tracker_row(row_id)
                    except Exception as exc:
                        st.error(f"Failed to delete row {row_id}: {exc}")

        st.rerun()

with col_export:
    if rows:
        export_df = edited_df.drop(columns=["id"])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Tracker")
            worksheet = writer.sheets["Tracker"]
            for i, col in enumerate(export_df.columns, start=1):
                max_len = max(
                    export_df[col].astype(str).map(len).max() if not export_df.empty else 0,
                    len(str(col)),
                )
                worksheet.column_dimensions[worksheet.cell(row=1, column=i).column_letter].width = (
                    max_len + 2
                )
        st.download_button(
            "⬇️ Export to Excel",
            data=buffer.getvalue(),
            file_name="tracker_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.caption("Nothing to export yet.")
