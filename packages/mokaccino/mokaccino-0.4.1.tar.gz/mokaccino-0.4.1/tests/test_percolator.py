from mokaccino import Percolator, Query, Document


def test_percolator_works():
    p = Percolator()
    assert p is not None
    qids = [
        p.add_query(Query.from_kv("name", "sausage")),
        p.add_query(Query.from_kprefix("name", "amaz")),
        p.add_query(Query.from_kgt("price", 12)),
        p.add_query(Query.from_kv("name", "sausage") | Query.from_kgt("price", 12)),
    ]

    assert p.percolate_list(Document()) == []
    assert p.percolate_list(Document().with_value("name", "burger")) == []
    assert p.percolate_list(Document().with_value("name", "sausage")) == [qids[0], qids[3]]
    assert p.percolate_list(Document().with_value("name", "amaz")) == [qids[1]]
    assert p.percolate_list(Document().with_value("name", "amazing")) == [qids[1]]
    assert p.percolate_list(Document().with_value("name", "amazon")) == [qids[1]]
    assert p.percolate_list(Document().with_value("price", "12")) == []
    assert p.percolate_list(Document().with_value("price", "13")) == [qids[2], qids[3]]
    assert p.percolate_list(
        Document().with_value("price", "13").with_value("name", "amazed")
    ) == [qids[1], qids[2], qids[3]]
