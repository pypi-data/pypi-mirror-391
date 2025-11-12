from base64 import urlsafe_b64encode
from dataclasses import dataclass
from urllib.parse import urljoin


def encode_page(site_url, page_url):
    page = urljoin(site_url, page_url)

    return urlsafe_b64encode(page.encode()).decode()


@dataclass
class LinkMaker:
    """Creates links to pages"""

    base_url: str
    site_url: str

    def ap_object(self, page_url: str):
        """Creates a link to the page object

        ```python
        >>> link_maker = LinkMaker("http://comments.example/", "http://site.example")
        >>> link_maker.ap_object("page.md")
        'http://comments.example/pages/aHR0cDovL3NpdGUuZXhhbXBsZS9wYWdlLm1k'

        ```
        """

        return self.base_url + "pages/" + encode_page(self.site_url, page_url)

    def comments(self, page_url: str):
        """Creates a link to the comments API call

        ```python
        >>> link_maker = LinkMaker("http://comments.example/", "http://site.example")
        >>> link_maker.comments("page.md")
        'http://comments.example/comments/aHR0cDovL3NpdGUuZXhhbXBsZS9wYWdlLm1k'

        ```
        """
        return self.base_url + "comments/" + encode_page(self.site_url, page_url)

    def fedi_actor(self):
        """Creates a link to the fedi_actor

        ```python
        >>> link_maker = LinkMaker("http://comments.example/", "http://site.example/path/")
        >>> link_maker.fedi_actor()
        'http://site.example/path/fedi-actor.json'

        ```
        """
        return urljoin(self.site_url, "fedi-actor.json")
