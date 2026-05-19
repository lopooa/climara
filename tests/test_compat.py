def test_supported_resources_nonempty():
    from climara.plotting import list_supported_resources

    rows = list_supported_resources()

    assert len(rows) > 0


def test_search_supported_resources():
    from climara.plotting import search_supported_resources

    rows = search_supported_resources("labelbar")

    assert len(rows) > 0
