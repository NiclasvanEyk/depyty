import re


def normalize_distribution_name(name: str) -> str:
    """
    Normalizes a distribution name according to [PEP 503](https://peps.python.org/pep-0503/#normalized-names).

    See https://packaging.python.org/en/latest/specifications/name-normalization/#name-normalization for
    the source of this snippet.
    """
    return re.sub(r"[-_.]+", "-", name).lower()
