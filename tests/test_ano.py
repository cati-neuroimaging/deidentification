
def test_import_class():
    from deidentification.anonymizer import anonymize
    assert True


def test_tag_lists():
    from deidentification.tag_lists import annex_e, safe_private_attributes
    assert True
    assert isinstance(annex_e, dict)
    assert isinstance(safe_private_attributes, dict)
