from app.utils.id_generator import new_id, short_id


def test_new_id_is_uuid_format():
    uid = new_id()
    parts = uid.split("-")
    assert len(parts) == 5


def test_new_id_is_unique():
    assert new_id() != new_id()


def test_short_id_default_length():
    assert len(short_id()) == 8


def test_short_id_custom_length():
    assert len(short_id(12)) == 12
