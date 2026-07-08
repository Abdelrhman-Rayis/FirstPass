"""Load and query the playbook (the legal team's standard positions)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "playbook" / "playbook.yaml"


@dataclass
class Playbook:
    raw: Dict[str, Any]

    @property
    def red_flags(self) -> List[Dict[str, Any]]:
        return self.raw.get("red_flags", [])

    @property
    def contract_types(self) -> Dict[str, Any]:
        return self.raw.get("contract_types", {})

    @property
    def recognised_headings(self) -> List[str]:
        return [h.lower() for h in self.raw.get("recognised_headings", [])]

    def type_def(self, type_key: str) -> Dict[str, Any]:
        return self.contract_types.get(type_key, {})


def load(path: str | Path = DEFAULT_PATH) -> Playbook:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return Playbook(raw=data)
