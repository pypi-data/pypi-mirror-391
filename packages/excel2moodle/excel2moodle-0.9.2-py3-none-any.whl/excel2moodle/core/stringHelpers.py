"""This Module holds small Helperfunctions related to string manipulation."""

from pathlib import Path

import lxml.etree as ET
from pandas import pandas


def getListFromStr(stringList: str | list[str | float]) -> list[str]:
    """Get a python List of strings from a semi-colon separated string."""
    stripped: list[str] = []
    li = []
    if isinstance(stringList, list):
        li = stringList
    elif isinstance(stringList, str):
        li = stringList.split(";")
    elif isinstance(stringList, float | int):
        li = [stringList]
    for i in li:
        s = i.strip() if isinstance(i, str) else str(i) if not pandas.isna(i) else None
        if s:
            stripped.append(s)
    return stripped


def getUnitsElementAsString(unit) -> None:
    def __getUnitEle__(name, multipl):
        unit = ET.Element("unit")
        ET.SubElement(unit, "multiplier").text = multipl
        ET.SubElement(unit, "unit_name").text = name
        return unit

    ET.Element("units")


def printDom(xmlElement: ET.Element, file: Path | None = None) -> None:
    """Prints the document tree of ``xmlTree`` to ``file``, if specified, else dumps to stdout."""
    documentTree = ET.ElementTree(xmlElement)
    if file is not None:
        if file.parent.exists():
            documentTree.write(
                file,
                xml_declaration=True,
                encoding="utf-8",
                pretty_print=True,
            )
    else:
        print(xmlElement.tostring())  # noqa: T201


def texWrapper(text: str | list[str], style: str) -> list[str]:
    r"""Put the strings inside ``text`` into a LaTex environment.

    if ``style == unit``: inside ``\\mathrm{}``
    if ``style == math``: inside ``\\( \\)``
    """
    answers: list[str] = []
    begin = ""
    end = ""
    if style == "math":
        begin = "\\("
        end = "\\)"
    elif style == "unit":
        begin = "\\(\\mathrm{"
        end = "}\\)"
    if isinstance(text, str):
        li = [begin]
        li.append(text)
        li.append(end)
        answers.append("".join(li))
    elif isinstance(text, list):
        for i in text:
            li = [begin]
            li.append(i)
            li.append(end)
            answers.append("".join(li))
    return answers
