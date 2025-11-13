from cms.cms_menus import get_menu_node_for_page, get_visible_nodes
from cms.models import EmptyPageContent, PageContent, PageUrl
from cms.toolbar.utils import get_toolbar_from_request
from cms.utils.i18n import get_fallback_languages, get_public_languages, hide_untranslated, is_valid_site_language
from cms.utils.page import get_page_queryset
from django.db.models.query import Prefetch, prefetch_related_objects
from menus.base import Menu

from .cms_menus_mixin import CMSMenuMixin


# This class i a copy of https://github.com/django-cms/django-cms/blob/4.1.7/cms/cms_menus.py#L199
# with extra function custom_menu_node.
class CMSMenu(CMSMenuMixin, Menu):
    """Subclass of :class:`menus.base.Menu`. Its :meth:`~menus.base.Menu.get_nodes()` creates
    a list of NavigationNodes based on a site's :class:`cms.models.pagemodel.Page` objects.
    """

    def get_nodes(self, request):
        site = self.renderer.site
        lang = self.renderer.request_language
        toolbar = get_toolbar_from_request(request)

        pages = get_page_queryset(site)

        if is_valid_site_language(lang, site_id=site.pk):
            _valid_language = True
            _hide_untranslated = hide_untranslated(lang, site.pk)
        else:
            _valid_language = False
            _hide_untranslated = False

        if _valid_language:
            # The request language has been explicitly configured
            # for the current site.
            if _hide_untranslated:
                fallbacks = []
            else:
                fallbacks = get_fallback_languages(lang, site_id=site.pk)
            languages = [lang] + [_lang for _lang in fallbacks if _lang != lang]
        else:
            # The request language is not configured for the current site.
            # Fallback to all configured public languages for the current site.
            languages = get_public_languages(site.pk)
            fallbacks = languages

        pages = (
            pages.filter(pagecontent_set__language__in=languages)
            .select_related("node")
            .order_by("node__path")
            .distinct()
        )
        pages = get_visible_nodes(request, pages, site)

        if not pages:
            return []

        try:
            homepage = [page for page in pages if page.is_home][0]
        except IndexError:
            homepage = None

        urls_lookup = Prefetch(
            "urls",
            to_attr="filtered_urls",
            queryset=PageUrl.objects.filter(language__in=languages),
        )
        if toolbar.edit_mode_active or toolbar.preview_mode_active:
            # Get all translations visible in the admin for the current page
            translations_qs = PageContent.admin_manager.current_content(language__in=languages)
        else:
            # Only get public translations
            translations_qs = PageContent.objects.filter(language__in=languages)
        translations_lookup = Prefetch(
            "pagecontent_set",
            to_attr="filtered_translations",
            queryset=translations_qs,
        )
        prefetch_related_objects(pages, urls_lookup, translations_lookup)
        # Build the blank title instances only once
        blank_page_content_cache = {language: EmptyPageContent(language=language) for language in languages}

        # Maps a node id to its page id
        node_id_to_page: dict[int, int] = {}

        def _page_to_node(page):
            # EmptyPageContent is used to prevent the cms from trying
            # to find a translation in the database
            page.page_content_cache = blank_page_content_cache.copy()

            for page_url in page.filtered_urls:
                page.urls_cache[page_url.language] = page_url

            for trans in page.filtered_translations:
                page.page_content_cache[trans.language] = trans

            menu_node = get_menu_node_for_page(
                self.renderer,
                page,
                language=lang,
                fallbacks=fallbacks,
                endpoint=toolbar.preview_mode_active or toolbar.edit_mode_active,
            )
            return menu_node

        menu_nodes = []

        for page in pages:
            node = page.node
            parent_id = node_id_to_page.get(node.parent_id)

            if node.parent_id and not parent_id:
                # If the parent page is not available (unpublished, etc..)
                # don't bother creating menu nodes for its descendants.
                continue

            menu_node = _page_to_node(page)
            if menu_node:
                # Only add pages with at least one page content
                cut_homepage = homepage and not homepage.get_in_navigation(lang)

                if cut_homepage and parent_id == homepage.pk:
                    # When the homepage is hidden from navigation,
                    # we need to cut all its direct children from it.
                    menu_node.parent_id = None
                else:
                    menu_node.parent_id = parent_id
                # This is the reason for the class copy. This line is added.
                self.extend_node_attr(menu_node.attr, page)
                node_id_to_page[node.pk] = page.pk
                menu_nodes.append(menu_node)
        return menu_nodes
