def normalize_private_key(key: str) -> str:
    """
    Env vars store PEM newlines as two literal characters. Without this you get
    ``PEM routines:get_name:no start line``. Also strips quotes that survive
    some .env parsers.
    """

    key = key.strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
        key = key[1:-1]
    return key.replace("\\n", "\n")
