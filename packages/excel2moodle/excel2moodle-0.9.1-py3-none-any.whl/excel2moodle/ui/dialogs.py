"""This Module hosts the various Dialog Classes, that can be shown from main Window."""

import hashlib
import io
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import lxml.etree as ET
from PySide6.QtCore import QUrl, Slot
from PySide6.QtGui import QImage, QTextDocument
from PySide6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMessageBox, QWidget

from excel2moodle import e2mMetadata
from excel2moodle.core.globals import XMLTags
from excel2moodle.core.question import ParametricQuestion, Question
from excel2moodle.core.settings import Tags
from excel2moodle.extra import variableGenerator
from excel2moodle.ui.UI_exportSettingsDialog import Ui_ExportDialog
from excel2moodle.ui.UI_updateDlg import Ui_UpdateDialog
from excel2moodle.ui.UI_variantDialog import Ui_Dialog

if TYPE_CHECKING:
    from excel2moodle.ui.appUi import MainWindow

logger = logging.getLogger(__name__)

import re

import matplotlib as mpl
import matplotlib.pyplot as plt


class UpdateDialog(QDialog):
    def __init__(
        self, parent: QMainWindow, changelog: str = "", version: str = ""
    ) -> None:
        super().__init__(parent)
        self.ui = Ui_UpdateDialog()
        self.ui.setupUi(self)
        self.ui.changelogBrowser.setMarkdown(changelog)
        self.ui.titleLabel.setText(
            f"<h2>New Version {version} of <i>exel2moodle</i> just dropped!!</h2>"
        )
        self.ui.fundingLabel.setText(
            f'If you find this project useful, please consider supporting its development. <br> <a href="{e2mMetadata["funding"]}">Buy jbosse3 a coffee</a>, so he stays caffeinated during coding.',
        )


class QuestionVariantDialog(QDialog):
    def __init__(self, parent, question: ParametricQuestion) -> None:
        super().__init__(parent)
        self.setWindowTitle("Question Variant Dialog")
        self.maxVal = question.parametrics.variants
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.spinBox.setRange(1, self.maxVal)
        self.ui.catLabel.setText(f"{question.katName}")
        self.ui.qLabel.setText(f"{question.name}")
        self.ui.idLabel.setText(f"{question.id}")

    @property
    def variant(self):
        return self.ui.spinBox.value()

    @property
    def categoryWide(self):
        return self.ui.checkBox.isChecked()


class ExportDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export question Selection")
        self.appUi: MainWindow = parent
        self.ui = Ui_ExportDialog()
        self.ui.setupUi(self)
        self.ui.btnExportFile.clicked.connect(self.getExportFile)
        self.ui.checkBoxExportAll.clicked.connect(self.toggleExportAll)

    @property
    def exportFile(self) -> Path:
        return self._exportFile

    @exportFile.setter
    def exportFile(self, value: Path) -> None:
        self._exportFile = value
        self.ui.btnExportFile.setText(
            f"../{(self.exportFile.parent.name)}/{self.exportFile.name}"
        )

    @Slot()
    def toggleExportAll(self) -> None:
        self.ui.spinBoxDefaultQVariant.setEnabled(
            not self.ui.checkBoxExportAll.isChecked()
        )
        self.ui.checkBoxIncludeCategories.setChecked(
            self.ui.checkBoxExportAll.isChecked()
        )

    @Slot()
    def getExportFile(self) -> None:
        path = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            dir=str(self.exportFile),
            filter="xml Files (*.xml)",
        )
        path = Path(path[0])
        if path.is_file():
            self.exportFile = path
            self.ui.btnExportFile.setText(
                f"../{(self.exportFile.parent.name)}/{self.exportFile.name}"
            )
        else:
            logger.warning("No Export File selected")


class QuestionPreview:
    def __init__(self, parent) -> None:
        self.ui = parent.ui
        self.parent: MainWindow = parent
        self.document: QTextDocument = QTextDocument()

    def _replaceImgPlaceholder(self, elementStr: str) -> str:
        """Replaces '@@PLUGINFILE@@' with the questions Img Folder path."""
        if self.parent.qSettings.value("preview/renderTex", type=bool):
            pattern = re.compile(r"\\\((.+?)\\\)", re.DOTALL)

            def repl(match):
                latex = match.group(1).strip()
                imgData = self.texToSvg(latex)
                qimg = QImage.fromData(imgData)
                if qimg.isNull():
                    logger.warning("⚠️ Could not render LaTeX: %s", latex)
                    return latex  # fallback text
                key = hashlib.sha1(latex.encode()).hexdigest()
                url = QUrl(f"latex://{key}")
                self.document.addResource(QTextDocument.ImageResource, url, qimg)
                return f'\n <img src="{url.toString()}" alt="{latex}" style="vertical-align: middle;">\n'

            elementStr = pattern.sub(repl, elementStr)
        return elementStr.replace(
            "@@PLUGINFILE@@",
            f"{self.pictureFolder}/{self.question.category.NAME}",
        )

    def setupQuestion(self, question: Question) -> None:
        self.pictureFolder = self.parent.settings.get(Tags.PICTUREFOLDER)
        self.ui.previewTextEdit.clear()
        self.question: Question = question
        self.ui.qNameLine.setText(f"{self.question.qtype} - {self.question.name}")
        previewHtml: list[str] = [
            """
            <!DOCTYPE html>
            <html>
              <body>"""
        ]

        self.parent.ui.tableVariables.hide()
        previewHtml.append(
            self._replaceImgPlaceholder(
                ET.tostring(self.question.htmlRoot, encoding="unicode", method="html"),
            )
        )
        self.appendAnswerText(previewHtml)
        previewHtml.append(
            """
              </body>
            </html>
            """
        )
        file = Path("preview.html").resolve()
        with file.open("w", encoding="utf-8") as f:
            f.write("\n".join(previewHtml))
        self.document.setHtml("\n".join(previewHtml))
        self.ui.previewTextEdit.setDocument(self.document)

    def appendAnswerText(self, preview: list[str]) -> list[str]:
        preview.append("<div> <br>")
        if isinstance(self.question, ParametricQuestion):
            variableGenerator.populateDataSetTable(
                self.parent.ui.tableVariables, parametrics=self.question.parametrics
            )
            self.parent.ui.tableVariables.show()
            ansList = self.question._element.findall(XMLTags.ANSWER)
            for ans in ansList:
                preview.append(f"<p> <b>Result: {ans.get('fraction')} %</b></p>")
                preview.append(
                    f"<p> Answer-feedback: {ans.find('feedback').find('text').text} </p>"
                )
        elif self.question.qtype == "NF":
            ansList = self.question._element.findall(XMLTags.ANSWER)
            for ans in ansList:
                preview.append(
                    f"<p><b>{ans.get('fraction')} % Result : {ans.find('text').text} </b></p>"
                )
                preview.append(
                    f"<p> Answer-feedback: {ans.find('feedback').find('text').text} </p>"
                )
        elif self.question.qtype == "MC":
            for n, ans in enumerate(self.question._element.findall(XMLTags.ANSWER)):
                preview.append(
                    f"<b>Answer {n + 1}, Fraction {ans.get('fraction')}:</b>"
                )
                preview.append(self._replaceImgPlaceholder(ans.find("text").text))
                preview.append(
                    f"Answer-feedback: {ans.find('feedback').find('text').text}"
                )
        preview.append("</div></p>")

        genfb = self.question._element.find(XMLTags.GENFEEDB)
        if genfb is not None:
            preview.append(
                f"<br><hr><b>General Feedback</b> <br> {genfb.find('text').text}"
            )
        return preview

    mpl.rcParams["mathtext.fontset"] = "stix"

    def texToSvg(self, latex: str) -> bytes:
        """Render LaTeX to base64-encoded SVG using matplotlib."""
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, f"${latex}$", fontsize=15)
        buf = io.BytesIO()
        plt.axis("off")
        fig.savefig(
            buf, format="svg", bbox_inches="tight", pad_inches=0.05, transparent=True
        )
        plt.close(fig)
        return buf.getvalue()


class AboutDialog(QMessageBox):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {e2mMetadata['name']}")
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.StandardButton.Close)

        self.aboutMessage: str = f"""
        <h1> About {e2mMetadata["name"]} v{e2mMetadata["version"]}</h1><br>
        <p style="text-align:center">

                <b><a href="{e2mMetadata["homepage"]}">{e2mMetadata["name"]}</a> - {e2mMetadata["description"]}</b>
        </p>
        <p style="text-align:center">
            If you need help you can find some <a href="https://gitlab.com/jbosse3/excel2moodle/-/example/"> examples.</a>
            </br>
            A Documentation can be viewed by clicking "F1",
            or onto the documentation button.
            </br>
        </p>
        <p style="text-align:center">
        To see whats new in version {e2mMetadata["version"]} see the <a href="https://gitlab.com/jbosse3/excel2moodle#changelogs"> changelogs.</a>
        </p>
        <p style="text-align:center">
        This project is maintained by {e2mMetadata["author"]}.
        <br>
        Development takes place at <a href="{e2mMetadata["homepage"]}"> GitLab: {e2mMetadata["homepage"]}</a>
        contributions are very welcome
        </br>
        If you encounter any issues please report them under the <a href="https://gitlab.com/jbosse3/excel2moodle/-/issues/"> repositories issues page </a>.
        </br>
        </p>
        <p style="text-align:center">
        <i>This project is published under {e2mMetadata["license"]}, you are welcome, to share, modify and reuse the code.</i>
        </p>
        """
        self.setText(self.aboutMessage)
