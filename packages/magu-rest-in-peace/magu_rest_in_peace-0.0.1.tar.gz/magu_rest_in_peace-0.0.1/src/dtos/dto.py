from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class DTO:
    def as_dict(self):
        return asdict(self)
