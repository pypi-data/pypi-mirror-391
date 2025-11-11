from copy import copy

import pytest

from data_sources.meta import Meta, AlreadyPresentInMeta, NotPresentInMeta


class TestAdd:
    def test_add_not_existing_key(self) -> None:
        meta = Meta()
        key = 'test_key'
        value = 'test_value'
        meta.add(key, value)

        assert meta.get(key) == value

    def test_add_existing_key(self) -> None:
        meta = Meta()
        key = 'test_key'
        value = 'test_value'
        meta.add(key, value)

        with pytest.raises(AlreadyPresentInMeta):
            meta.add(key, value)


class TestAddOrModify:
    def test_add_or_modify_not_existing_key(self) -> None:
        meta = Meta()
        key = 'test_key'
        value = 'test_value'
        meta.add_or_modify(key, value)

        assert meta.get(key) == value

    def test_add_or_modify_existing_key(self) -> None:
        meta = Meta()
        key = 'test_key'
        value = 'test_value'
        meta.add(key, value)

        another_value = 'another_value'
        meta.add_or_modify(key, another_value)

        assert meta.get(key) == another_value


class TestGet:
    def test_get_not_existing_key(self) -> None:
        meta = Meta()

        with pytest.raises(NotPresentInMeta):
            meta.get("not_present")

    def test_get_existing_key(self) -> None:
        meta = Meta()
        key = 'test_key'
        value = 'test_value'
        meta.add(key, value)

        assert meta.get(key) == value


class TestMetaCopy:
    def test_copy_creates_different_container(self) -> None:
        meta = Meta()
        key = 'test_key'
        value = 'test_value'
        meta.add(key, value)
        meta_copy = copy(meta)

        assert meta._container != meta_copy._container

        assert meta.get(key) == value
        assert meta_copy.get(key) == value

    def test_change_value_after_copy(self) -> None:
        meta = Meta()
        key = 'test_key'
        value = 'test_value'
        meta.add(key, value)
        meta_copy = copy(meta)

        another_value = 'another_value'
        meta_copy.add_or_modify(key, another_value)

        another_key = 'another_key'
        meta_copy.add(another_key, another_value)

        assert meta.get(key) == value
        assert meta_copy.get(key) == another_value

        assert another_key not in meta.keys()
        assert another_key in meta_copy.keys()
