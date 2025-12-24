def combi_to_str(combi, sep="_", tuple_sep="-", suffix=""):
    """
    Convert a tuple like ('a', (1,15), 'X') into a string tag:
    - Strings or numbers → as is
    - Tuples → joined with `tuple_sep`
    """
    parts = []
    for item in combi:
        if isinstance(item, tuple):
            # join tuple elements with tuple_sep
            parts.append(tuple_sep.join(map(str, item)))
        else:
            parts.append(str(item))
    return sep.join(parts) + suffix

