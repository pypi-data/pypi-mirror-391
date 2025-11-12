import os
from urllib.parse import urljoin

from mkdocs.plugins import BasePlugin, event_priority
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from mkdocs_fedi_comments.actor import Actor

from .link_maker import LinkMaker, encode_page
from .config import MkdocsFediCommentsConfig
from .file_maker import logo_file, javascript_file, file_base_path


class Plugin(BasePlugin[MkdocsFediCommentsConfig]):
    @event_priority(-20)
    def on_config(self, config) -> None:
        if not config.site_url:
            raise Exception("site_url must be set to use this plugin")

        base_path = self.config.get("base_path", "")

        if not base_path.endswith("/"):
            raise Exception(f"Base path '{base_path}' should end with '/'")

        self.link_maker = LinkMaker(base_path, config.site_url)
        self.base_path = base_path

        if self.config.get("actor"):
            self.actor = Actor(**self.config.get("actor"))  # type: ignore
        else:
            self.actor = None

        theme = config["theme"]
        theme.dirs = [os.path.join(file_base_path, "overrides")] + theme.dirs

    def on_files(self, files: Files, /, *, config) -> Files | None:
        files.append(logo_file(config))
        files.append(javascript_file(config))

        if self.actor:
            files.append(self.actor.as_file(config))
        return files

    def on_page_markdown(
        self, markdown: str, *, page: Page, config, files: Files
    ) -> str | None:
        disabled = page.meta.get("fedi_comment", {}).get("disable", False)
        if disabled:
            return

        page.meta["fedi_link"] = self.link_maker.ap_object(page.url)
        page.meta["fedi_comments"] = self.link_maker.comments(page.url)
        page.meta["fedi_encoded"] = encode_page(config.site_url, page.url)
        page.meta["fedi_comments_endpoint"] = urljoin(self.base_path, "/comments")

        if self.actor:
            page.meta["fedi_actor"] = self.link_maker.fedi_actor()

        markdown += "\n\n## Comments"

        return markdown
