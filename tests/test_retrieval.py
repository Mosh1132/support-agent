from support_agent.retrieval import split_into_chunks


def test_chunker_splits_refund_handbook():
    chunks = split_into_chunks("line one\n\n  line two  \n")
    assert chunks == ["line one", "line two"]