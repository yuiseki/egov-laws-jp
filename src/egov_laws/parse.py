"""Parse one e-Gov law XML (a single law revision) into plain text."""

import xml.etree.ElementTree as ET


def revision_id_from_url(url: str) -> str:
    """`.../law/{law_id}/{date}_{amendment_id}` -> `{law_id}_{date}_{amendment_id}`."""
    law_id, tail = url.rstrip("/").split("/")[-2:]
    return f"{law_id}_{tail}"


def _ruby_base(el: ET.Element) -> str:
    # Ruby readings (<Rt>) are annotations, not part of the statute text.
    out = [el.text or ""]
    for child in el:
        if child.tag != "Rt":
            out.append(_ruby_base(child))
        out.append(child.tail or "")
    return "".join(out)


def _lines(el: ET.Element):
    # Text nodes become lines, except that a <Ruby> run is merged into the
    # text around it so the base text stays contiguous.
    buf = [el.text or ""]
    for child in el:
        if child.tag == "Ruby":
            buf.append(_ruby_base(child))
        else:
            yield "".join(buf)
            buf = []
            yield from _lines(child)
        buf.append(child.tail or "")
    yield "".join(buf)


def extract_text(xml: str | bytes) -> str:
    """Join text nodes one per line, dropping ruby readings.

    Same shape as the earlier laws.txt (one stripped text node per line), minus
    <Rt>. Text around a <Ruby> element is kept on one line so the base text of
    a ruby run stays contiguous.
    """
    root = ET.fromstring(xml)
    lines = [t.strip() for t in _lines(root)]
    return "\n".join(t for t in lines if t)
