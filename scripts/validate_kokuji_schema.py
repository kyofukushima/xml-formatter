#!/usr/bin/env python3
"""kokuji*_asukoe.xsd で告示XMLを検証する。

XSD 側の LawBody が `xs:any` を含むため libxml2 の UPA 検査に引っかかり、
そのままでは XMLSchema を構築できない。検証時のみ `xs:any` を
`xs:element ref="SupplProvision"` に差し替えて読み込む。
"""
import argparse
import sys

from lxml import etree

XS = "{http://www.w3.org/2001/XMLSchema}"


def load_schema(xsd_path):
    doc = etree.parse(xsd_path)
    has_sp = any(e.get("name") == "SupplProvision" for e in doc.getroot().iter(f"{XS}element"))
    for el in doc.getroot().iter(f"{XS}element"):
        if el.get("name") != "LawBody":
            continue
        for anyel in list(el.iter(f"{XS}any")):
            parent = anyel.getparent()
            idx = list(parent).index(anyel)
            parent.remove(anyel)
            if has_sp:
                sub = etree.Element(f"{XS}element")
                sub.set("ref", "SupplProvision")
                sub.set("minOccurs", "0")
                sub.set("maxOccurs", "unbounded")
                parent.insert(idx, sub)
    return etree.XMLSchema(doc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xsd")
    ap.add_argument("xml", nargs="+")
    args = ap.parse_args()

    schema = load_schema(args.xsd)
    rc = 0
    for path in args.xml:
        ok = schema.validate(etree.parse(path))
        print(f'{"OK " if ok else "NG "} {path}')
        if not ok:
            rc = 1
            for e in list(schema.error_log)[:10]:
                print(f"      line {e.line}: {e.message}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
