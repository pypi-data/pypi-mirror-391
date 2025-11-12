from pathlib import Path


class Catalog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        # Just create an empty metadata file for now
        if not self.path.exists():
            self.path.write_text("FoundryDB Catalog v1\n")

    def __repr__(self):
        return f"<Catalog path={self.path}>"
