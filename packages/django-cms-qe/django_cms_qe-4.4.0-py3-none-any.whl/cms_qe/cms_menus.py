from cms import __version__

# pylint: skip-file
if __version__.split(".")[0] == "4":
    from .cms4_menus import CMSMenu  # noqa: F401
else:
    from .cms5_menus import CMSMenu  # noqa: F401
