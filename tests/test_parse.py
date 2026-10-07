from pathlib import Path

from egov_laws.parse import extract_text, revision_id_from_url

FIXTURES = Path(__file__).parent / "fixtures"


def test_revision_id_from_url():
    url = "https://laws.e-gov.go.jp/law/326AC1000000285/20230401_504AC0000000024"
    assert revision_id_from_url(url) == "326AC1000000285_20230401_504AC0000000024"


def test_revision_id_from_url_old_law():
    url = "https://laws.e-gov.go.jp/law/105DF0000000337/18721109_000000000000000"
    assert revision_id_from_url(url) == "105DF0000000337_18721109_000000000000000"


def test_extract_text_drops_ruby_reading():
    xml = "<Law><LawBody><Sentence><Ruby>法令<Rt>ほうれい</Rt></Ruby>の本文</Sentence></LawBody></Law>"
    assert extract_text(xml) == "法令の本文"


def test_extract_text_one_node_per_line_and_strips():
    xml = "<Law>\n  <A> 第一条 </A>\n  <B>本文</B>\n</Law>"
    assert extract_text(xml) == "第一条\n本文"


def test_extract_text_keeps_tail_after_ruby():
    xml = "<Law><S>前<Ruby>漢字<Rt>かんじ</Rt></Ruby>後</S></Law>"
    assert extract_text(xml) == "前漢字後"


def test_extract_text_matches_previous_laws_txt_on_real_law():
    xml = (FIXTURES / "hakubutsukan.xml").read_bytes()
    lines = extract_text(xml).split("\n")
    assert len(lines) == 474
    assert lines[0] == "昭和二十六年法律第二百八十五号"
    assert lines[1] == "博物館法"
