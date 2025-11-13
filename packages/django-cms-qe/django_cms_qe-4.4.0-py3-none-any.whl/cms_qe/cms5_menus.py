import re
from typing import Optional

from cms.cms_menus import (VISIBLE_FOR_ANONYMOUS, VISIBLE_FOR_AUTHENTICATED, CMSMenu as CMS5Menu, CMSNavigationNode,
                           apphook_pool)
from cms.models import PageContent

from .cms_menus_mixin import CMSMenuMixin


class CMSMenu(CMSMenuMixin, CMS5Menu):

    # This class i a copy of https://github.com/django-cms/django-cms/blob/5.0.4/cms/cms_menus.py#L199
    # see line above comment: This line is added.
    def get_menu_node_for_page_content(
        self,
        page_content: PageContent,
        preview_url: Optional[str] = None,
        cut: bool = False,
    ) -> CMSNavigationNode:
        """
        Transform a CMS page content object into a navigation node.

        :param page: The page to transform.
        :param languages: The list of the current language plus fallbacks used to render the menu.
        :param preview_url: If given, serves as a "pattern" for a preview url with the assumption that "/0/"
            is replaced by the actual page content pk. Default is None.
        :param cut: If True the parent_id is set to None. Default is False.
        :returns: A CMSNavigationNode instance.
        """
        page = page_content.page

        # These are simple to port over, since they are not calculated.
        # Other attributes will be added conditionally later.
        visibility = page_content.limit_visibility_in_menu
        attr = {
            "is_page": True,
            "soft_root": page_content.soft_root,
            "auth_required": page.login_required,
            "reverse_id": page.reverse_id,
            "is_home": page.is_home,
            "visible_for_authenticated": visibility in VISIBLE_FOR_AUTHENTICATED,
            "visible_for_anonymous": visibility in VISIBLE_FOR_ANONYMOUS,
        }

        extenders = []
        if page.navigation_extenders:
            if page.navigation_extenders in self.renderer.menus:
                extenders.append(page.navigation_extenders)
            elif f"{page.navigation_extenders}:{page.pk}" in self.renderer.menus:
                extenders.append(f"{page.navigation_extenders}:{page.pk}")
        # Is this page an apphook? If so, we need to handle the apphooks's nodes
        # Only run this if we have a translation in the requested language for this
        # object. The page content cache should have been prepopulated in CMSMenu.get_nodes
        # but otherwise, just request the title normally
        if page.application_urls and page_content.language == self.languages[0]:
            # it means it is an apphook
            app = apphook_pool.get_apphook(page.application_urls)
            if app:
                extenders.extend(app.get_menus(page, self.languages[0]))
        # CMSAattachMenus are treated a bit differently to allow them to be
        # able to be attached to multiple points in the navigation.
        attr["navigation_extenders"] = [
            f"{ext.__name__}:{page.pk}" if hasattr(ext, "get_instances") else getattr(ext, "__name__", ext)
            for ext in extenders
        ]
        # This is the reason for the class copy. This line is added.
        self.extend_node_attr(attr, page)

        # Now finally, build the NavigationNode object and return it.
        # The parent_id is manually set by the menu get_nodes method.
        if preview_url:
            # Build preview url by replacing "/0/" in the url template by the actual pk of the page content object
            # Hacky, but faster than calling `admin_reverse` for each page content object
            url = re.sub("(/0/)", f"/{page_content.pk}/", preview_url)
        else:
            url = page.get_absolute_url(language=page_content.language)

        return CMSNavigationNode(
            title=page_content.menu_title or page_content.title,
            url=url,
            id=page.pk,
            parent_id=None if cut else page_content.page.parent_id,
            attr=attr,
            visible=page_content.in_navigation,
            language=(page_content.language if page_content.language != self.languages[0] else None),
        )
