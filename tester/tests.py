"""Test functions for AlQuran Cloud API.

Each function returns (name, status, latency_ms, details).
status is "PASS" or "FAIL".
"""

from tester.client import get


# --------------- A. Contract tests ---------------

def test_surah_status_200():
    """GET /surah/1 returns HTTP 200."""
    resp, lat = get("/surah/1")
    if resp.status_code == 200:
        return ("GET /surah/1 status 200", "PASS", lat, None)
    return ("GET /surah/1 status 200", "FAIL", lat, f"got {resp.status_code}")


def test_surah_content_type_json():
    """GET /surah/1 returns JSON content-type."""
    resp, lat = get("/surah/1")
    ct = resp.headers.get("Content-Type", "")
    if "application/json" in ct:
        return ("GET /surah/1 Content-Type JSON", "PASS", lat, None)
    return ("GET /surah/1 Content-Type JSON", "FAIL", lat, f"got {ct}")


def test_surah_schema():
    """GET /surah/1 response has required fields with correct types."""
    resp, lat = get("/surah/1")
    data = resp.json().get("data", {})
    errors = []
    if not isinstance(data.get("number"), int):
        errors.append("number not int")
    if not isinstance(data.get("name"), str):
        errors.append("name not str")
    if not isinstance(data.get("englishName"), str):
        errors.append("englishName not str")
    if not isinstance(data.get("ayahs"), list):
        errors.append("ayahs not list")
    if not isinstance(data.get("revelationType"), str):
        errors.append("revelationType not str")
    if errors:
        return ("GET /surah/1 schema", "FAIL", lat, "; ".join(errors))
    return ("GET /surah/1 schema", "PASS", lat, None)


def test_surah_fatiha_7_ayahs():
    """Al-Fatiha must have exactly 7 ayahs."""
    resp, lat = get("/surah/1")
    ayahs = resp.json().get("data", {}).get("ayahs", [])
    if len(ayahs) == 7:
        return ("Al-Fatiha has 7 ayahs", "PASS", lat, None)
    return ("Al-Fatiha has 7 ayahs", "FAIL", lat, f"got {len(ayahs)}")


def test_meta_counts():
    """GET /meta returns correct total counts."""
    resp, lat = get("/meta")
    data = resp.json().get("data", {})
    surahs = data.get("surahs", {}).get("count", 0)
    ayahs = data.get("ayahs", {}).get("count", 0)
    errors = []
    if surahs != 114:
        errors.append(f"surahs count {surahs} != 114")
    if ayahs != 6236:
        errors.append(f"ayahs count {ayahs} != 6236")
    if errors:
        return ("GET /meta counts", "FAIL", lat, "; ".join(errors))
    return ("GET /meta counts", "PASS", lat, None)


def test_edition_list():
    """GET /edition returns a non-empty list with expected fields."""
    resp, lat = get("/edition")
    data = resp.json().get("data", [])
    if not isinstance(data, list) or len(data) == 0:
        return ("GET /edition list", "FAIL", lat, "empty or not a list")
    first = data[0]
    required = {"identifier", "language", "name", "englishName"}
    missing = required - set(first.keys())
    if missing:
        return ("GET /edition list", "FAIL", lat, f"missing fields: {missing}")
    return ("GET /edition list", "PASS", lat, None)


def test_edition_language_filter():
    """GET /edition/language/fr returns only French editions."""
    resp, lat = get("/edition/language/fr")
    data = resp.json().get("data", [])
    if not data:
        return ("GET /edition/language/fr", "FAIL", lat, "empty result")
    non_fr = [e for e in data if e.get("language") != "fr"]
    if non_fr:
        return ("GET /edition/language/fr", "FAIL", lat, f"{len(non_fr)} non-fr editions")
    return ("GET /edition/language/fr", "PASS", lat, None)


# --------------- B. Invalid input tests ---------------

def test_invalid_surah_404():
    """GET /surah/999 returns code 404 or error status."""
    resp, lat = get("/surah/999")
    body = resp.json()
    code = body.get("code")
    if code in (404, 400) or resp.status_code in (404, 400):
        return ("GET /surah/999 error", "PASS", lat, None)
    return ("GET /surah/999 error", "FAIL", lat, f"code={code}, http={resp.status_code}")


def test_search_returns_results():
    """GET /search/God/all/en.asad returns matches."""
    resp, lat = get("/search/God/all/en.asad")
    data = resp.json().get("data", {})
    count = data.get("count", 0)
    if isinstance(count, int) and count > 0:
        return ("GET /search Rahman", "PASS", lat, f"{count} results")
    return ("GET /search Rahman", "FAIL", lat, f"count={count}")


def test_juz_30():
    """GET /juz/30 returns data with ayahs."""
    resp, lat = get("/juz/30")
    data = resp.json().get("data", {})
    ayahs = data.get("ayahs", [])
    if isinstance(ayahs, list) and len(ayahs) > 0:
        return ("GET /juz/30", "PASS", lat, f"{len(ayahs)} ayahs")
    return ("GET /juz/30", "FAIL", lat, "no ayahs")


# Registry of all test functions
ALL_TESTS = [
    test_surah_status_200,
    test_surah_content_type_json,
    test_surah_schema,
    test_surah_fatiha_7_ayahs,
    test_meta_counts,
    test_edition_list,
    test_edition_language_filter,
    test_invalid_surah_404,
    test_search_returns_results,
    test_juz_30,
]
