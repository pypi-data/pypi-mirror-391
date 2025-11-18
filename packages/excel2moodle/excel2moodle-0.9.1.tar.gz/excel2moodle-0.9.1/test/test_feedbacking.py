from pathlib import Path

import lxml.etree as ET

from excel2moodle.core.dataStructure import QuestionDB
from excel2moodle.core.settings import Settings, Tags

settings = Settings()

database = QuestionDB(settings)
excelFile = Path("test/TestQuestion.ods")
database.spreadsheet = excelFile
database.readCategoriesMetadata(excelFile)
database.initAllCategories(excelFile)
mcCategory = database.categories["MC1"]
nfmCategory = database.categories["NFM2"]
nfCategory = database.categories["NF3"]
database.parseCategoryQuestions(mcCategory)
database.parseCategoryQuestions(nfmCategory)
database.parseCategoryQuestions(nfCategory)


def test_unsetAnswerFeedback() -> None:
    q = mcCategory.questions[2]
    q.getUpdatedElement()
    true_feedback = ET.fromstring(
        q._element.find("answer").find("feedback").find("text").text
    )
    for ans in q._element.findall("answer"):
        if float(ans.get("fraction")) < 0.0:
            false_feedback = ET.fromstring(ans.find("feedback").find("text").text)
            break
    assert false_feedback.find("span").text == settings.get(Tags.FALSEANSFB)
    assert (
        false_feedback.find("span").text == "Your answer is sadly wrong, try again!!!"
    )
    assert true_feedback.find("span").text == settings.get(Tags.TRUEANSFB)
    assert true_feedback.find("span").text == "true"


def test_partialSetAnswerFB() -> None:
    q = mcCategory.questions[1]
    q.getUpdatedElement()
    for ans in q._element.findall("answer"):
        if float(ans.get("fraction")) > 0.0:
            trueAns = ans
        elif float(ans.get("fraction")) < 0.0:
            falseAns = ans
    trueFB = ET.fromstring(trueAns.find("feedback").find("text").text)
    falseFB = ET.fromstring(falseAns.find("feedback").find("text").text)
    assert trueFB.find("span").text == settings.get(Tags.TRUEANSFB)
    assert trueFB.find("span").text == "true"
    assert falseFB.find("span").text == settings.get(Tags.FALSEANSFB)
    assert falseFB.find("span").text == "Your answer is sadly wrong, try again!!!"


def test_nfAnswerFeedbacks() -> None:
    for question in nfCategory.questions.values():
        question.getUpdatedElement()
        tree = ET.Element("quiz")
        tree.append(question._element)
        answers = tree.find("question").findall("answer")
        wrongSignPerc = question.rawData.get(Tags.WRONGSIGNPERCENT)
        for ans in answers:
            trueAns = ans if ans.get("fraction") == "100" else None
        truefeedback = ET.fromstring(trueAns.find("feedback").find("text").text)
        print(truefeedback.find("span").text)
        assert truefeedback.find("span").text == settings.get(Tags.TRUEANSFB)


def test_nfmAnswerFeedbacks() -> None:
    for question in nfmCategory.questions.values():
        question.getUpdatedElement()
        tree = ET.Element("quiz")
        tree.append(question._element)
        answers = tree.find("question").findall("answer")
        wrongSignPerc = question.rawData.get(Tags.WRONGSIGNPERCENT)
        for ans in answers:
            if ans.get("fraction") == "100":
                trueAns = ans
            elif ans.get("fraction") == str(wrongSignPerc):
                wrongSignAns = ans
        truefeedback = ET.fromstring(trueAns.find("feedback").find("text").text)
        wrongSignEle = ET.fromstring(wrongSignAns.find("feedback").find("text").text)
        print(truefeedback.find("span").text)
        assert wrongSignEle.find("span").text == question.rawData.get(Tags.WRONGSIGNFB)
        assert truefeedback.find("span").text == settings.get(Tags.TRUEANSFB)
