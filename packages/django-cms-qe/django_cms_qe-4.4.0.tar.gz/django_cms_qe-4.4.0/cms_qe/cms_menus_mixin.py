from typing import Any

from cms.models import Page


class CMSMenuMixin:

    def extend_node_attr(self, attr: dict[str, Any], page: Page) -> None:
        """Extend node attrs."""
        attr["page_description"] = page.get_meta_description()
