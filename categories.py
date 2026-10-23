# categories.py
# Maps file extensions to category folder names.
# Add new extensions here — everything else falls back to "Other Files".

CATEGORIES = {
    "Photos":        [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
                      ".tiff", ".svg", ".heic"],
    "Videos":        [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm",
                      ".m4v", ".flv"],
    "Documents":     [".doc", ".docx", ".txt", ".rtf", ".odt"],
    "PDFs":          [".pdf"],
    "Presentations": [".ppt", ".pptx", ".pps", ".ppsx", ".odp"],
    "Spreadsheets":  [".xls", ".xlsx", ".csv", ".ods", ".tsv"],
    "Archives":      [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Audio":         [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"],
    "Code":          [".py", ".cpp", ".c", ".h", ".java", ".js", ".ts",
                      ".html", ".css", ".json", ".xml", ".sql"],
    "Installers":    [".exe", ".msi", ".msix", ".apk"],
}

FALLBACK_CATEGORY = "Other Files"


def _build_lookup():
    """Turn CATEGORIES into a flat {extension: category} dict."""
    lookup = {}
    for category, extensions in CATEGORIES.items():
        for ext in extensions:
            lookup[ext.lower()] = category
    return lookup


_EXT_LOOKUP = _build_lookup()


def get_category(filename: str) -> str:
    """Return the category folder name for a filename."""
    dot = filename.rfind(".")
    if dot == -1:
        return FALLBACK_CATEGORY
    ext = filename[dot:].lower()
    return _EXT_LOOKUP.get(ext, FALLBACK_CATEGORY)


def all_category_names():
    """List of category folder names, in display order."""
    return list(CATEGORIES.keys()) + [FALLBACK_CATEGORY]