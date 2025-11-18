import logging
import re
from typing import Literal

import lxml.etree as ET

from excel2moodle.core import stringHelpers
from excel2moodle.core.exceptions import InvalidFieldException, QNotParsedException
from excel2moodle.core.globals import Tags, TextElements
from excel2moodle.core.question import ParametricQuestion, Parametrics
from excel2moodle.logger import LogAdapterQuestionID

loggerObj = logging.getLogger(__name__)


class BulletList:
    def __init__(
        self,
        rawBullets: list[str],
        qID: str,
        style: Literal["parameters", "raw"] = "parameters",
        template: str = "",
    ) -> None:
        self.rawBullets: list[str] = rawBullets
        self.element: ET.Element = ET.Element("ul")
        self.bullets: dict[str | int, BulletP | RawBulletP] = {}
        self.id = qID
        self.logger = LogAdapterQuestionID(loggerObj, {"qID": self.id})
        if style == "parameters":
            self._setupBullets(rawBullets, template=template)
        elif style == "raw":
            self._setupRawBullets(rawBullets)

    def appendBullets(
        self,
        bulletList: list[str],
        style: Literal["parameters", "raw"],
        template: str = "",
    ) -> None:
        self._setupRawBullets(bulletList)

    def update(self, parametrics: Parametrics, variant: int = 1) -> None:
        variables: dict[str, list[float]] = parametrics.variables
        for var, bullet in self.bullets.items():
            if isinstance(bullet, BulletP):
                bullet.update(value=variables[var][variant - 1])

    def getVariablesDict(self, question: ParametricQuestion) -> dict[str, list[float]]:
        """Read variabel values for vars in `question.rawData`.

        Returns
        -------
        A dictionary containing a list of values for each variable name

        """
        keyList = self.varNames
        dic: dict = {}
        missing: list[str] = []
        for k in keyList:
            if k.lower() in question.rawData:
                val = question.rawData[k.lower()]
                if isinstance(val, str):
                    li = stringHelpers.getListFromStr(val)
                    variables: list[float] = [float(i.replace(",", ".")) for i in li]
                    dic[str(k)] = variables
                else:
                    dic[str(k)] = [str(val)]
            else:
                missing.append(k)
        if len(missing) > 0:
            msg = f"The keys: {missing}, is not defined. Did you forget to assign values to it?"
            raise QNotParsedException(msg, self.id)
        loggerObj.debug("The following variables were provided: %s", dic)
        return dic

    @property
    def varNames(self) -> list[str]:
        names = [
            i for i in self.bullets if isinstance(i, str) and not i.startswith("raw")
        ]
        if len(names) > 0:
            self.logger.debug("returning Var names: %s", names)
            return names
        msg = "Bullet variable names not given."
        raise ValueError(msg)

    def _setupRawBullets(self, bps: list[str]) -> ET.Element:
        for i, bullet in enumerate(bps):
            self.bullets[f"raw{i}"] = RawBulletP(bulletStr=bullet)
            self.element.append(self.bullets[f"raw{i}"].element)
        return self.element

    def _setupBullets(self, bps: list[str], template: str = "") -> ET.Element:
        self.logger.debug("Formatting the bulletpoint list")
        varFinder = re.compile(r"\{(\w+)\}")
        bulletFinder = re.compile(
            r"^\s?(?P<desc>.*?)"
            r"(?:\s+(?P<var>[\S]+)\s*=\s*)"
            r"(?:(?P<val>[\S]+))"
        )
        unitFinder = re.compile(r".*?(?:=\s*[\S]+\s+(?P<unit>[\S]+)\s*$)")
        for i, item in enumerate(bps):
            match = re.search(bulletFinder, item)
            if match is None:
                self.logger.error("Couldn't find any bullets")
                msg = f"Couldn't decode the bullet point: {item}"
                raise InvalidFieldException(msg, self.id, Tags.BPOINTS)
            name = match.group("desc")
            var = match.group("var")
            value = match.group("val")
            unit = (
                match.group("unit")
                if (match := re.search(unitFinder, item)) is not None
                else ""
            )
            self.logger.info(
                "Decoded bulletPoint: name: %s, var: %s, - value: %s, - unit: %s.",
                name,
                var,
                value,
                unit,
            )
            if (match := re.search(varFinder, value)) is None:
                self.logger.debug("Got a normal bulletItem")
                num: float = float(value.replace(",", "."))
                bulletName = i + 1
            else:
                bulletName = match.group(1)
                num: float = 0.0
                self.logger.debug("Got an variable bulletItem, match: %s", match)
            # for userfriendliness because % would be the comment in latex
            if unit == "%":
                unit = r"\%"
            self.bullets[bulletName] = BulletP(
                name=name, var=var, unit=unit, value=num, template=template
            )
            self.element.append(self.bullets[bulletName].element)
        return self.element


class RawBulletP:
    def __init__(self, bulletStr: str) -> None:
        self.name = bulletStr
        self.element: ET.Element = TextElements.LISTITEM.create()
        self.element.text = bulletStr


class BulletP:
    def __init__(
        self,
        name: str,
        var: str,
        unit: str,
        value: float = 0.0,
        template: str = "",
    ) -> None:
        self.name: str = (
            name.replace(" ", "~")
            if template.startswith("\\(") and len(name.split()) > 1
            else name
        )
        self.var: str = var
        self.unit: str = unit
        self.element: ET.Element
        self.value: float = value
        mapper: dict[str, str] = {
            "<name>": self.name,
            "<var>": self.var,
            "<unit>": self.unit,
        }
        tmp = template
        for k, val in mapper.items():
            tmp = tmp.replace(k, str(val))
        self.bulletStr = tmp
        self.update(value=value)

    def update(self, value: float = 1) -> None:
        if not hasattr(self, "element"):
            self.element = TextElements.LISTITEM.create()
        valuestr = str(value).replace(".", r",\!")
        self.element.text = self.bulletStr.replace("<value>", valuestr)
