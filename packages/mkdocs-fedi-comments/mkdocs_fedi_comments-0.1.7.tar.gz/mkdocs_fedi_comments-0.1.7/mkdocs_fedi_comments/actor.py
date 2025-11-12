from dataclasses import asdict, dataclass, field
import json

from mkdocs.structure.files import File


@dataclass
class Actor:
    """Configuration model for an actor"""

    name: str
    handle: str
    summary: str | None = field(default=None)
    icon: str | None = field(
        default=None, metadata={"description": "url of an icon to display"}
    )

    def as_json(self):
        return json.dumps(asdict(self))  # type: ignore

    def as_file(self, config):
        return File.generated(
            src_uri="fedi-actor.json",
            config=config,
            content=self.as_json(),
        )
