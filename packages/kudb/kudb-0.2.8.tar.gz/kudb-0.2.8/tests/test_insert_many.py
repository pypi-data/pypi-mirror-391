"""
kudb insert_meny test
"""
# pylint: disable=C0413,W1309,C0103

import kudb

def test_insert_many():
    """test insert_many"""
    # insert
    kudb.connect(':memory:')
    kudb.insert_many([
        {'name': 'Tako', 'age': 20},
        {'name': 'Ika', 'age': 10},
        {'name': 'Ebi', 'age': 15},
    ])
    doc = kudb.find_one(lambda x: x['name'] == "Ebi")
    assert doc is not None, 'insert_meny and find_one error'
    assert 15 == doc["age"], 'insert_meny and find_one error'
    kudb.close()

def test_insert_many_tag():
    """test insert_many with tag"""
    # insert
    kudb.connect(':memory:')
    kudb.insert_many([
        {'name': 'Tako', 'age': 20},
        {'name': 'Ika', 'age': 10},
        {'name': 'Ebi', 'age': 15},
    ], tag='seafood')
    docs = kudb.get_by_tag('seafood')
    assert docs is not None, 'insert_meny and find_one error'
    assert len(docs) == 3, 'insert_meny and find_one error'
    kudb.close()

