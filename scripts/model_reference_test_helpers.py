"""Read the seven logical fields from Stage 1's family reference tables."""

from html.parser import HTMLParser


FIELDS = ("models", "status", "context", "pricing", "use", "limits", "sources")


class ModelReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.records: dict[str, dict[str, list[str]]] = {}
        self.links: dict[str, list[str]] = {}
        self.family: str | None = None
        self.field: str | None = None
        self.fragments: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "table" and values.get("data-model-family"):
            self.family = values["data-model-family"]
            assert self.family not in self.records, "duplicate family table"
            self.records[self.family] = {}
            self.links[self.family] = []
        elif self.family and tag == "tbody":
            self.field = values.get("data-field")
            assert self.field in FIELDS, "missing or unknown reference field"
            assert self.field not in self.records[self.family], "duplicate field"
            self.records[self.family][self.field] = []
        elif self.family and self.field and tag == "td":
            self.fragments = []
        elif self.fragments is not None:
            if tag == "code":
                self.fragments.append("`")
            elif tag == "br":
                self.fragments.append(" ")
            elif tag == "a":
                href = values.get("href")
                assert href, "source link without a destination"
                self.links[self.family].append(href)

    def handle_data(self, data: str) -> None:
        if self.fragments is not None:
            self.fragments.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "code" and self.fragments is not None:
            self.fragments.append("`")
        elif tag == "td" and self.fragments is not None:
            value = "".join(self.fragments).strip()
            assert value, "empty model reference value"
            self.records[self.family][self.field].append(value)
            self.fragments = None
        elif tag == "tbody":
            self.field = None
        elif tag == "table":
            self.family = None


def family_rows(text: str) -> dict[str, list[str]]:
    parser = ModelReferenceParser()
    parser.feed(text)
    rows = {}
    for family, fields in parser.records.items():
        assert tuple(fields) == FIELDS, f"{family}: missing or reordered fields"
        assert all(fields.values()), f"{family}: field without a value"
        cells = [family, *("; ".join(fields[field]) for field in FIELDS)]
        cells[7] += " " + " ".join(parser.links[family])
        rows[family] = cells
    return rows


def family_cells(text: str, name: str) -> list[str]:
    rows = family_rows(text)
    matches = [cells for key, cells in rows.items()
               if key == name or (name == "Jev" and key.startswith("Jev"))]
    assert len(matches) == 1, f"expected exactly one {name} family"
    return matches[0]
