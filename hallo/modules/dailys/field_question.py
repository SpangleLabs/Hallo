import datetime
from typing import Optional, Dict, List

import dateutil.parser
import isodate

import hallo.modules.dailys.dailys_field
from hallo.events import EventMessage, EventMinute, Event
from hallo.modules.dailys.dailys_spreadsheet import DailysSpreadsheet


class AnswerOption:
    type_name = "answer"
    def __init__(self, answer: str):
        self.answer = answer

    @classmethod
    def from_dict(cls, json_dict: Dict) -> 'AnswerOption':
        return AnswerOption(
            json_dict["answer"]
        )


class RepeatingInterval:
    def __init__(self, iso8601: str):
        repeat, start, period = iso8601.split("/")
        self.count = None
        if repeat != "R":
            self.count = int(repeat[1:])
        self.start = dateutil.parser.parse(start)
        self.period = isodate.parse_duration(period)

    def last_time(self) -> Optional[datetime.datetime]:
        now = datetime.datetime.now(datetime.timezone.utc)
        if now < self.start:
            return None
        check = self.start
        count = 1
        while (check + self.period < now) and count <= self.count:
            check += self.period
            count += 1
        return check

    def next_time(self) -> Optional[datetime.datetime]:
        now = datetime.datetime.now(datetime.timezone.utc)
        if now < self.start:
            return self.start
        check = self.start + self.period
        count = 1
        while check < now:
            if count >= self.count:
                return None
            # increment
            check += self.period
            count += 1
        return check


class Question:
    def __init__(
            self,
            qid: str,
            question: str,
            time_pattern: RepeatingInterval,
            *,
            allow_custom_answers: bool = True,
            answer_options: Optional[List[AnswerOption]] = None,
            deprecation: Optional[datetime.datetime] = None,
            must_answer: bool = False,
            remind_period: Optional[datetime.timedelta] = None,
    ):
        self.id = qid
        self.question = question
        self.time_pattern = time_pattern
        self.allow_custom_answers = allow_custom_answers
        self.answer_options = answer_options or []
        self.deprecation = deprecation
        self.must_answer = must_answer
        self.remind_period = remind_period

    def is_active(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        return now < self.deprecation

    @classmethod
    def from_dict(cls, json_dict: Dict) -> 'Question':
        deprecation = None
        if "deprecation" in json_dict:
            deprecation = dateutil.parser.parse(json_dict["deprecation"])
        answer_options = []
        if "answers" in json_dict:
            answer_options = [AnswerOption.from_dict(d) for d in json_dict["answers"]]
        remind_period = None
        if "remind_period" in json_dict:
            remind_period = isodate.parse_duration(json_dict["remind_period"])
        return Question(
            json_dict["id"],
            json_dict["question"],
            RepeatingInterval(json_dict["time_pattern"]),
            allow_custom_answers=json_dict.get("allow_custom_answers", True),
            answer_options=answer_options,
            deprecation=deprecation,
            must_answer=json_dict.get("must_answer", False),
            remind_period=remind_period
        )


class Answer:
    def __init__(self):
        self.answered = True
        self.answer = "Yeah, sure"
        self.answer_time = datetime.datetime.now()
        self.asked_time = datetime.datetime.now()
        self.question_id = "this_week_only"
        self.question_msg_id = 1234565


class QuestionsField(hallo.modules.dailys.dailys_field.DailysField):

    def __init__(self, spreadsheet: DailysSpreadsheet, questions: List[Question]):
        super().__init__(spreadsheet)
        self.questions = questions
        self.answers_cache = {}

    @staticmethod
    def create_from_input(event, spreadsheet):
        return QuestionsField.create_from_spreadsheet(spreadsheet)

    @staticmethod
    def create_from_spreadsheet(spreadsheet):
        static_data = spreadsheet.read_path("stats/questions/static/")
        if len(static_data) == 0:
            raise hallo.modules.dailys.dailys_field.DailysException(
                "Questions field static data has not been set up on dailys system."
            )
        question_data = static_data[0]["data"]["questions"]
        questions = [Question.from_dict(d) for d in question_data]
        return QuestionsField(spreadsheet, questions)

    @staticmethod
    def passive_events():
        return [EventMessage, EventMinute]

    def passive_trigger(self, evt: Event) -> Optional[Event]:
        if isinstance(evt, EventMinute):
            return self.time_trigger(evt)
        if isinstance(evt, EventMessage):
            return self.msg_trigger(evt)

    def time_trigger(self, evt: EventMinute) -> Optional[Event]:
        pass  # TODO

    def msg_trigger(self, evt: EventMessage) -> Optional[Event]:
        pass  # TODO

    def to_json(self):
        return {
            "type_name": self.type_name
        }

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return QuestionsField.create_from_spreadsheet(spreadsheet)
