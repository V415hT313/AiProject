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

COLUMNS = ["id", "name", "category", "value", "unit", "date", "notes"]
EDITABLE_FIELDS = ["name", "category", "value", "unit", "notes"]

try:
    with st.spinner("Loading tracker rows..."):
        rows = get_tracker_rows()
except Exception as exc:
    st.error(f"Could not load tracker rows: {exc}")
    rows = []

df = pd.DataFrame(rows, columns=COLUMNS)

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    width="stretch",
    column_config={
        "id": st.column_config.NumberColumn("ID", disabled=True),
        "date": st.column_config.TextColumn("Date", disabled=True),
        "value": st.column_config.NumberColumn("Value"),
    },
    key="tracker_editor",
)

col_save, col_export = st.columns([1, 1])

with col_save:
    if st.button("💾 Save changes"):
        with st.spinner("Saving changes..."):
            original_by_id = {row["id"]: row for row in rows}
            edited_ids = set()

            for _, edited_row in edited_df.iterrows():
                row_id = edited_row.get("id")
                fields = {
                    "name": edited_row.get("name") or "",
                    "category": edited_row.get("category") or None,
                    "value": float(edited_row["value"]) if pd.notna(edited_row.get("value")) else None,
                    "unit": edited_row.get("unit") or None,
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
                        if any(original.get(k) != v for k, v in fields.items()):
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
        buffer = BytesIO()
        df.drop(columns=["id"]).to_excel(buffer, index=False, engine="openpyxl")
        st.download_button(
            "⬇️ Export to Excel",
            data=buffer.getvalue(),
            file_name="tracker_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.caption("Nothing to export yet.")
