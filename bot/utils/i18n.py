"""i18n helper — translates keys using the user's stored language."""

from locales import ru, uz

_LOCALES = {"ru": ru.texts, "uz": uz.texts}


def _(key: str, lang: str = "ru", **kwargs) -> str:
    """Return translated string for *key* in *lang*, formatted with **kwargs."""
    locale = _LOCALES.get(lang, ru.texts)
    template = locale.get(key) or ru.texts.get(key, key)
    try:
        return template.format(**kwargs) if kwargs else template
    except (KeyError, IndexError):
        return template
