import pytest
import vernacular
from unittest.mock import patch
from vernacular.i18nstr import i18nstr
from vernacular.translate import Translator


def teardown_module(module):
    vernacular.clean_translations_test_folder()


@pytest.fixture(scope="module")
@patch('vernacular.COMPILE', False)
def uncompiled_store():
    return vernacular.from_entrypoints(restrict=None)


@pytest.fixture(scope="module")
@patch('vernacular.COMPILE', True)
def compiled_store():
    return vernacular.from_entrypoints(restrict=None)


def test_from_entrypoints_no_compile(uncompiled_store):
    store = vernacular.from_entrypoints(restrict=None)
    assert store == {}


def test_from_entrypoints_compile(compiled_store):
    store = vernacular.from_entrypoints(restrict=None)
    assert set(store.keys()) == {'test'}
    assert set(store['test'].keys()) == {'fr'}
    assert set(store['test']['fr'].keys()) == {None, 'CA'}


def test_translator(compiled_store):

    brake = i18nstr('handbrake')
    tap = i18nstr('tap')
    sir = i18nstr('sir')  # Does not exist on fr_CA, should fallback on fr

    translate = Translator(compiled_store, default_domain='test').translate

    assert translate(brake, target_language='fr_FR') == 'frein à main'
    assert translate(brake, target_language='fr') == 'frein à main'
    assert translate(brake, target_language='fr_CA') == 'brake à bras'

    assert translate(tap, target_language='fr_LOL') == 'robinet'
    assert translate(tap, target_language='fr') == 'robinet'
    assert translate(tap, target_language='fr_CA') == 'champlure'

    assert translate(sir, target_language='fr') == 'monsieur'
    assert translate(sir, target_language='fr_CA') == 'monsieur'
    assert translate(sir, target_language='us_CA') == 'sir'


def test_i18str():
    word = i18nstr('word')
    assert word == 'word'
    assert word.domain is None
    assert word.default == 'word'


def test_i18str_mapping():
    word = i18nstr('Hello ${name}', mapping={'name': 'Judith'})
    assert word == 'Hello ${name}'
    assert word.mapping == {'name': 'Judith'}
    with pytest.raises(TypeError):
        word.mapping['name'] = 'Rose'
    with pytest.raises(TypeError):
        word.mapping['age'] = 18

    new_word = word.replace(mapping={"name": "Rose"})
    assert new_word.mapping == {'name': 'Rose'}
    assert new_word is not word
    assert word == new_word


def test_i18str_interpolate(compiled_store):
    greetings = i18nstr(
        'greetings',
        mapping={'name': 'John'}
    )
    translate = Translator(compiled_store, default_domain='test').translate
    assert translate(greetings, target_language='fr') == (
        'Bonjour John. Bienvenue à ${place}.'
    )

    greetings = i18nstr(
        'greetings',
        mapping={'name': 'John', 'place': 'Londres'}
    )
    translate = Translator(compiled_store, default_domain='test').translate
    assert translate(greetings, target_language='fr') == (
        'Bonjour John. Bienvenue à Londres.'
    )


def test_plural(compiled_store):
    pluralize = Translator(compiled_store, default_domain='test').pluralize
    result = pluralize(
        "Unable to find user: ${users}",
        "Unable to find users: ${users}",
        1, mapping={'users': 'john'}, target_language='fr')
    assert result == "Impossible de trouver l'utilisateur: john"

    result = pluralize(
        "Unable to find user: ${users}",
        "Unable to find users: ${users}",
        2, mapping={'users': 'john, jane'}, target_language='fr')
    assert result == "Impossible de trouver les utilisateurs: john, jane"
