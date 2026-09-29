import re

LANGUAGES = [
    ("en-US", "English (United States)"), ("en-GB", "English (United Kingdom)"),
    ("es-ES", "Spanish"), ("fr-FR", "French"), ("de-DE", "German"),
    ("pt-BR", "Portuguese (Brazil)"), ("it-IT", "Italian"), ("hi-IN", "Hindi"),
    ("ar-SA", "Arabic"), ("zh-CN", "Chinese (Simplified)"), ("zh-TW", "Chinese (Traditional)"),
    ("ja-JP", "Japanese"), ("ko-KR", "Korean"), ("ru-RU", "Russian"),
    ("bn-IN", "Bengali"), ("ur-PK", "Urdu"), ("pa-IN", "Punjabi"),
    ("ta-IN", "Tamil"), ("te-IN", "Telugu"), ("tr-TR", "Turkish"),
    ("vi-VN", "Vietnamese"), ("th-TH", "Thai"), ("id-ID", "Indonesian"),
    ("ms-MY", "Malay"), ("nl-NL", "Dutch"), ("pl-PL", "Polish"),
    ("uk-UA", "Ukrainian"), ("sw-KE", "Swahili"), ("fa-IR", "Persian"),
    ("fil-PH", "Filipino"), ("he-IL", "Hebrew"), ("el-GR", "Greek"),
    ("cs-CZ", "Czech"), ("da-DK", "Danish"), ("fi-FI", "Finnish"),
    ("nb-NO", "Norwegian Bokmal"), ("sv-SE", "Swedish"), ("ro-RO", "Romanian"),
    ("hu-HU", "Hungarian"), ("bg-BG", "Bulgarian"), ("hr-HR", "Croatian"),
    ("sr-RS", "Serbian"), ("sk-SK", "Slovak"), ("sl-SI", "Slovenian"),
    ("ne-NP", "Nepali"), ("si-LK", "Sinhala"), ("ml-IN", "Malayalam"),
    ("kn-IN", "Kannada"), ("gu-IN", "Gujarati"), ("my-MM", "Burmese"),
    ("km-KH", "Khmer"), ("lo-LA", "Lao"), ("am-ET", "Amharic"),
    ("zu-ZA", "Zulu"), ("yo-NG", "Yoruba"), ("ha-NG", "Hausa"),
    ("is-IS", "Icelandic"), ("ga-IE", "Irish"), ("cy-GB", "Welsh"),
    ("ca-ES", "Catalan"),
]

_LANGUAGE_TAG = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")

def normalize_language(value: str) -> str:
    value = value.strip()
    return value if _LANGUAGE_TAG.fullmatch(value) else "en-US"