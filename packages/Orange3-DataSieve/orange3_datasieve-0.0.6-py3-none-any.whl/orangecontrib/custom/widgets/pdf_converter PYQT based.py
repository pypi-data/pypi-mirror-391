import os
import json
import base64
from io import BytesIO
from datetime import datetime

import camelot
import numpy as np
import pandas as pd
from pypdfium2 import PdfDocument
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QApplication,
    QProgressBar,
)

from Orange.widgets.gui import ProgressBar
from Orange.widgets.widget import OWWidget, Output, Msg
from Orange.widgets.settings import Setting
from Orange.data import Table, Domain, StringVariable, ContinuousVariable, TimeVariable
import pkg_resources
from PIL import Image


def _get_expiration_date():
    # Use the "Publish to web" CSV link from Google Sheets
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQxFzdr6gkoUjtP3fbQ2S0lLRgikHwx7a5NyCYBnAtg2yXubdgiF8Rpdhd1WzH29zga16s8M1YGblgJ/pub?output=csv"
    try:
        import requests

        resp = requests.get(csv_url)
        resp.raise_for_status()
        first_line = resp.text.strip().splitlines()[0].split(",")[0]
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(first_line, fmt)
            except ValueError:
                continue
        print(f"Unknown date format: {first_line}")
        return None
    except Exception as e:
        print(f"Failed to fetch expiry date from sheet: {e}")
        return None


class PdfConverter(OWWidget):
    name = "PDF_Converter PyQt Only"
    description = (
        "A PDF Table Extractor widget using PyQt UI only. "
        "Load PDFs, select table areas, set column delimiters, and extract tables."
    )
    category = "Orange3-DataSieve"
    icon = "icons/pdf_converter.svg"
    want_main_area = True
    want_control_area = False
    priority = 1

    class Outputs:
        data = Output("Data", Table)

    file_path: str = Setting("", schema_only=True)
    table_area: str = Setting("", schema_only=True)
    delimiters: str = Setting("", schema_only=True)
    break_lines: int = Setting(1, schema_only=True)

    class Error(OWWidget.Error):
        invalid_path = Msg("File path is invalid, File was not found.")
        processing_failed = Msg("Processing failed: {}")
        path_is_not_file = Msg("File path is not a PDF file.")

    class Information(OWWidget.Information):
        data_loaded = Msg("Data successfully loaded")
        processing_complete = Msg("Processing complete")

    def __init__(self):
        super().__init__()
        self.extracted_tables = []
        self.steps = 0
        self.pb = None
        self.counter = 0
        self.init_ui()

        if (
            self.file_path
            and os.path.exists(self.file_path)
            and os.path.isfile(self.file_path)
        ):
            if self.table_area:
                self.process_pdf_with_coordinates(
                    self.file_path, self.table_area, self.delimiters
                )
        elif self.file_path and not os.path.exists(self.file_path):
            self.Error.invalid_path()
        elif self.file_path and not os.path.isfile(self.file_path):
            self.Error.path_is_not_file()

    def init_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Buttons
        self.load_button = QPushButton("Load PDF")
        self.load_button.clicked.connect(self.openFileDialog)
        layout.addWidget(self.load_button)

        self.setLayout(layout)

    def openFileDialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.file_path = file_path
            self.process_pdf_with_coordinates(
                self.file_path, self.table_area or "", self.delimiters or ""
            )

    def process_pdf_with_coordinates(
        self,
        file_path,
        table_area,
        delimiters,
        pages="all",
        flavor="stream",
        break_lines=True,
    ):
        self.setBlocking(True)
        if not file_path or not os.path.isfile(file_path):
            self.Error.invalid_path()
            self.setBlocking(False)
            return

        try:
            # Load PDF pages
            pdf = PdfDocument(file_path)
            self.steps = len(pdf)
            self.pb = ProgressBar(self, iterations=self.steps)
            self.counter = 0
            all_dataframes = []

            text_split = break_lines == 1
            page_numbers = list(range(1, self.steps + 1))

            for i, page_num in enumerate(page_numbers):
                tables = camelot.read_pdf(
                    file_path,
                    pages=str(page_num),
                    flavor=flavor,
                    table_areas=[table_area] if table_area else None,
                    columns=[delimiters] if delimiters else None,
                    split_text=text_split,
                )

                if self.counter < self.steps:
                    self.pb.advance()
                    self.counter += 1
                QApplication.processEvents()

                for table in tables:
                    df_temp = table.df
                    df_temp["page"] = int(page_num)
                    all_dataframes.append(df_temp)

            self.pb.finish()
            self.setBlocking(False)

            if not all_dataframes:
                self.status_label.setText("No tables found")
                return

            concat_all_dataframes = pd.concat(all_dataframes, ignore_index=True)
            concat_all_dataframes = concat_all_dataframes.astype(str)
            table = self.dataframe_to_orange_table(concat_all_dataframes)
            self.Outputs.data.send(table)
            self.status_label.setText(f"Processed: {os.path.basename(file_path)}")

        except Exception as e:
            self.Error.processing_failed(str(e))
            self.setBlocking(False)

    def dataframe_to_orange_table(self, df: pd.DataFrame) -> Table:
        df.columns = self.make_unique_column_names(df.columns)
        attributes, metas, X_data, metas_data = [], [], [], []

        for col in df.columns:
            col_data = df[col]
            dtype = col_data.dtype

            if col == "page":
                attributes.append(ContinuousVariable(col))
                X_data.append(col_data.to_numpy(dtype=int))
            elif pd.api.types.is_numeric_dtype(dtype):
                attributes.append(ContinuousVariable(col))
                X_data.append(col_data.to_numpy(dtype=float))
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                metas.append(TimeVariable(col))
                metas_data.append(col_data.astype("int64") / 1e9)
            else:
                metas.append(StringVariable(col))
                metas_data.append(col_data.astype(str).to_numpy())

        X_matrix = np.column_stack(X_data) if X_data else np.empty((len(df), 0))
        metas_matrix = np.column_stack(metas_data) if metas_data else None
        domain = Domain(attributes=attributes, metas=metas)
        return Table.from_numpy(domain, X=X_matrix, metas=metas_matrix)

    def make_unique_column_names(self, columns):
        seen = {}
        unique_columns = []
        for col in columns:
            original_col = str(col)
            if original_col not in seen:
                seen[original_col] = 0
                unique_columns.append(original_col)
            else:
                seen[original_col] += 1
                unique_columns.append(f"{original_col}_{seen[original_col]}")
        return unique_columns

    def onDeleteWidget(self):
        self.extracted_tables = []
        super().onDeleteWidget()
