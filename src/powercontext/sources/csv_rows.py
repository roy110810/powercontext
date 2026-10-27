import csv
from io import BytesIO, TextIOWrapper
from typing import Tuple
from pydantic import BaseModel

from powercontext.core.source import Source, SourceDefinition


class CSVDocumentInput(BaseModel):
    document_id: str
    primary_key: str
    content: bytes


class CSVRowInput(BaseModel):
    document_id: str
    primary_key: str
    primary_key_value: str
    columns: tuple[str, ...]
    values: tuple[str, ...]


class CSVRowSource(Source):
    source_id: str
    document_id: str
    primary_key: str
    primary_key_value: str
    columns: tuple[str, ...]
    values: tuple[str, ...]


def parse_csv_document(value: CSVDocumentInput) -> tuple[CSVRowInput, ...]:
    result = []
    stream = TextIOWrapper(BytesIO(value.content), encoding="utf-8", newline="")
    reader = csv.DictReader(stream)
    headers = tuple(reader.fieldnames) if reader.fieldnames else ()
    if value.primary_key not in headers:
        return tuple()
    for row in reader:
        pk_val = row[value.primary_key]
        col_values = tuple(row[h] for h in headers)
        row_input = CSVRowInput(
            document_id=value.document_id,
            primary_key=value.primary_key,
            primary_key_value=pk_val,
            columns=headers,
            values=col_values
        )
        result.append(row_input)
    return tuple(result)

def csv_row_source_id(document_id: str, primary_key_value: str) -> str:
    return f"{document_id}:{primary_key_value}"


CSV_ROW_SOURCE_DEFINITION: SourceDefinition[CSVRowInput, CSVRowSource, CSVRowInput] = SourceDefinition(
    input_type=CSVRowInput,
    source_type=CSVRowSource,
    source_id_fn=lambda inp: csv_row_source_id(inp.document_id, inp.primary_key_value),
    factory=lambda inp: CSVRowSource(
        source_id=csv_row_source_id(inp.document_id, inp.primary_key_value),
        document_id=inp.document_id,
        primary_key=inp.primary_key,
        primary_key_value=inp.primary_key_value,
        columns=inp.columns,
        values=inp.values
    )
)
