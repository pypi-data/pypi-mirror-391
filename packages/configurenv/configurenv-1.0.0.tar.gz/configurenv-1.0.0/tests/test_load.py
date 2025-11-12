import pytest
from configurenv import load_config_from_files


@pytest.mark.parametrize('filename', ['indexers.yml', 'indexers.yaml', 'indexers.json'])
def test_load_config_from_files(datadir, filename):
    config = {'INDEXERS_FILE': datadir / filename}
    load_config_from_files(config)
    assert 'INDEXERS' in config
    assert config == {
        'INDEXERS_FILE': datadir / filename,
        # should result in the same config no matter the file format
        'INDEXERS': {'Item': ['content_model']},
    }


def test_load_config_from_files_unknown_extension(datadir):
    config = {'INDEXERS_FILE': datadir / 'indexers.bad_extension'}
    with pytest.raises(RuntimeError):
        load_config_from_files(config)


def test_load_config_from_files_file_not_found(datadir):
    config = {'INDEXERS_FILE': datadir / 'no_file.yml'}
    with pytest.raises(RuntimeError):
        load_config_from_files(config)
