import pytest

from . import create_fake_config


def test_tag_lists():
    from deidentification.tag_lists import (conf_profile, conf_profile_range,
                                            safe_private_attributes)
    assert isinstance(conf_profile, dict)
    assert isinstance(conf_profile_range, dict)
    assert isinstance(safe_private_attributes, dict)


def test_anonymizer_profile_load():
    from deidentification import DeidentificationError
    from deidentification.config import load_config_profile
    tags_config = load_config_profile('data_sharing')
    assert isinstance(tags_config, dict)
    with pytest.raises(DeidentificationError, match=r"Profile .* does not exists."):
        tags_config = load_config_profile('wrong_profile')


def test_profile_w_private_creator():
    from deidentification.config import load_config_profile
    tags_config = load_config_profile('cati_collector')
    private_creator_values = [v.get('private_creator')
                              for v in tags_config.values()
                              if v.get('private_creator')]
    assert private_creator_values


def test_tag_to_tuple():
    from deidentification.config import tag_to_tuple
    tags = {
        '(0010, 005A)': (0x0010, 0x005A),
        'F010,1010': (0xF010, 0x1010),
        '(1,1)': (0x0001, 0x0001),
    }
    for tag_str, tag_value in tags.items():
        assert tag_to_tuple(tag_str) == tag_value

    wrong_tags = ['(0010)', '0250 0010', '(2005, 1050, 0001)', '(2005, 1015a)', '000h, 2005']
    for wrong_tag in wrong_tags:
        with pytest.raises(ValueError, match=r"Input tag .* must contain .*"):
            tag_to_tuple(wrong_tag)


def test_multiple_private_creator_name():
    from deidentification.config import load_config_profile
    tmp_config = create_fake_config([
        ['(2005,0010)', 'Private Creator', 'K', 'Name1'],
        ['(2005,0010)', 'Private Creator', 'K', 'Name2']
    ])

    config = load_config_profile(tmp_config)
    assert len(config[(0x2005, 0x0010)]['private_creator']) == 2
