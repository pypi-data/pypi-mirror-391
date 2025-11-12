import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# tests/test_string_methods.py
import pytest

# Adjust import path to where your functions live.
# If your module is `pystringlite/string_methods.py`, use:
# from pystringlite.string_methods import *
# Or if you put the functions directly in package __init__.py adjust accordingly.
from funcLibrary.string_methods import (
    capitalize,
    count,
    endswith,
    find,
    index,
    isdigit,
    islower,
    isupper,
    replace,
    rstrip,
    lstrip,
    swapcase,
)


# ---------- capitalize ----------
def test_capitalize_lowercase():
    assert capitalize("hello") == "Hello"


def test_capitalize_already_capitalized():
    assert capitalize("Hello") == "Hello"


def test_capitalize_nonalpha_first_char():
    assert capitalize("1abc") == "1abc"


# ---------- count (should count overlapping occurrences) ----------
def test_count_simple():
    assert count("lo", "hello") == 1


def test_count_overlapping():
    # "aaaa" contains "aa" at indices 0,1,2 => 3 occurrences (overlapping)
    assert count("aa", "aaaa") == 3


def test_count_multichar():
    assert count("ana", "banana") == 2


# ---------- endswith ----------
def test_endswith_true():
    assert endswith("world", "hello world") is True


def test_endswith_false():
    assert endswith("hello", "hello world") is False


# ---------- find ----------
def test_find_found():
    assert find("lo", "hello") == 3


def test_find_not_found():
    assert find("xyz", "hello") == -1


def test_find_with_start():
    # find 'l' starting from index 3 should return 3
    assert find("l", "hello", start_index=3) == 3


def test_find_with_end_excludes():
    # Searching for "o" but end_index before occurrence -> -1
    assert find("o", "hello", start_index=0, end_index=3) == -1


# ---------- index ----------
def test_index_found():
    assert index("lo", "hello") == 3


def test_index_raises_when_not_found():
    with pytest.raises(ValueError):
        index("xyz", "hello")


def test_index_with_range_found():
    # 'l' at index 3 should be found when start_index <= 3 and end large enough
    assert index("l", "hello", start_index=2, end_index=4) == 3


# ---------- isdigit ----------
def test_isdigit_true():
    assert isdigit("12345") is True


def test_isdigit_false_with_letters():
    assert isdigit("12a45") is False


def test_isdigit_empty_string():
    # converting empty string to int will fail -> False expected
    assert isdigit("") is False


# ---------- islower / isupper ----------
def test_islower_true():
    assert islower("hello") is True


def test_islower_false_with_upper():
    assert islower("Hello") is False


def test_isupper_true():
    assert isupper("HELLO") is True


def test_isupper_false_with_lower():
    assert isupper("HELlo") is False


# ---------- replace ----------
def test_replace_basic():
    assert replace("lo", "L0", "hello", count=1) == "heL0o"


def test_replace_multiple_count():
    # replace first two 'a' in 'aaa' -> 'bba'
    assert replace("a", "b", "aaa", count=2) == "bba"


def test_replace_count_default_is_one():
    # default count is 1 per your implementation
    assert replace("a", "x", "aba") == "xb a".replace(" ", "")  # intentionally trivial check
    # More straightforward:
    assert replace("a", "x", "aba") == "xba"


def test_replace_invalid_count_raises():
    with pytest.raises(ValueError):
        replace("a", "b", "aaa", count="not-an-int")


# ---------- rstrip / lstrip ----------
def test_rstrip_trailing_spaces():
    assert rstrip("abc   ") == "abc"


def test_lstrip_leading_spaces():
    assert lstrip("   abc") == "abc"


def test_rstrip_no_trailing():
    assert rstrip("abc") == "abc"


def test_lstrip_no_leading():
    assert lstrip("abc") == "abc"


# ---------- swapcase ----------
def test_swapcase_mixed():
    assert swapcase("Hello WORLD 123") == "hELLO world 123"


def test_swapcase_no_alpha():
    assert swapcase("123!@#") == "123!@#"
