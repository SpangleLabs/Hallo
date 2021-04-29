import datetime
from threading import RLock
from typing import Optional, Dict, List

import dateutil.parser
import isodate

import hallo.modules.dailys.dailys_field
from hallo.events import EventMessage, EventMinute, Event, RawDataTelegramOutbound
from hallo.modules.dailys.dailys_spreadsheet import DailysSpreadsheet


class AnswerOption:

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
        self.must_answer = must_answer  # TODO
        self.remind_period = remind_period  # TODO

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
    def __init__(
            self,
            question_id: str,
            asked_time: datetime.datetime,
            *,
            answer: Optional[str] = None,
            answer_time: Optional[datetime.datetime] = None,
            question_msg_id: Optional[int] = None,
    ):
        self.answer = answer
        self.answer_time = answer_time
        self.asked_time = asked_time
        self.question_id = question_id
        self.question_msg_id = question_msg_id

    @property
    def answered(self) -> bool:
        return self.answer is not None

    def same_answer(self, other: 'Answer') -> bool:
        return self.question_id == other.question_id and self.asked_time == other.asked_time

    @classmethod
    def from_dict(cls, json_dict: Dict) -> 'Answer':
        answer_time = None
        if "answer_time" in json_dict:
            answer_time = dateutil.parser.parse(json_dict["answer_time"])
        return Answer(
            json_dict["question_id"],
            dateutil.parser.parse(json_dict["asked_time"]),
            answer=json_dict.get("answer"),
            answer_time=answer_time,
            question_msg_id=json_dict.get("q_message_id")
        )

    def to_dict(self) -> Dict:
        d = {
            "question_id": self.question_id,
            "asked_time": self.asked_time.isoformat()
        }
        if self.answer:
            d["answer"] = self.answer
        if self.answer_time:
            d["answer_time"] = self.answer_time.isoformat()
        if self.question_msg_id:
            d["q_message_id"] = self.question_msg_id
        return d


class AnswersData:
    def __init__(self, spreadsheet: DailysSpreadsheet):
        self.spreadsheet = spreadsheet

    def get_answers_for_date(self, answer_date: datetime.date) -> List[Answer]:
        date_data = self.spreadsheet.read_path("stats/questions/"+answer_date.isoformat())
        answer_data = date_data[0]["data"]["answers"]
        return [Answer.from_dict(d) for d in answer_data]

    def save_answers_for_date(self, answer_date: datetime.date, answers: List[Answer]):
        date_data = {"answers": [a.to_dict() for a in answers]}
        self.spreadsheet.save_field(QuestionsField, date_data, answer_date)

    def save_answer(self, answer: Answer) -> None:
        answer_date = answer.asked_time.date()
        date_answers = self.get_answers_for_date(answer_date)
        matching_answer = next([a for a in date_answers if a.same_answer(answer)], None)
        if matching_answer is not None:
            date_answers.remove(matching_answer)
            date_answers.append(answer)
        else:
            date_answers.append(answer)
        self.save_answers_for_date(answer_date, date_answers)


class AnswerCache:
    def __init__(self, data: 'AnswersData'):
        self.data = data
        self._cache = {}

    def _populate_answers_for_date(self, answer_date: datetime.date) -> None:
        answers = self.data.get_answers_for_date(answer_date)
        self._cache[answer_date] = {}
        for answer in answers:
            self._cache[answer_date][answer.question_id][answer.asked_time] = Answer

    def answer_for_question_at_time(self, question: Question, answer_time: datetime.datetime) -> Optional[Answer]:
        if answer_time.date() not in self._cache:
            self._populate_answers_for_date(answer_time.date())
        return self._cache.get(answer_time.date(), {}).get(question.id, {}).get(answer_time)


class QuestionsField(hallo.modules.dailys.dailys_field.DailysField):
    type_name = "questions"

    def __init__(self, spreadsheet: DailysSpreadsheet, questions: List[Question]):
        super().__init__(spreadsheet)
        self.questions = questions
        self.data = AnswersData(spreadsheet)
        self.lock = RLock()

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
            return self._time_trigger()
        if isinstance(evt, EventMessage):
            return self._msg_trigger(evt)

    def _time_trigger(self) -> None:
        answer_cache = AnswerCache(self.data)
        for question in self.questions:
            if not question.is_active():
                continue
            last_time = question.time_pattern.last_time()
            answer = answer_cache.answer_for_question_at_time(question, last_time)
            if answer is None:
                self._ask_question(question, last_time)

    def _ask_question(self, question: Question, ask_time: datetime.datetime) -> None:
        msg = (
            "I have a question (id={}):\n".format(question.id)
            + question.question
        )
        if question.answer_options:
            msg += "\n\nHere are some answer options:\n"
            msg += "\n".join("- {}".format(option.answer) for option in question.answer_options)
            if question.allow_custom_answers:
                msg += "\n\nBut custom answers are also allowed."
        evt = self.message_channel(msg)
        # Get sent message ID
        sent_msg_id = None
        if isinstance(evt.raw_data, RawDataTelegramOutbound):
            sent_msg_id = evt.raw_data.sent_msg_object.message_id
        # Create answer object
        answer = Answer(question.id, ask_time, question_msg_id=sent_msg_id)
        with self.lock:
            self.data.save_answer(answer)

    def _msg_trigger(self, evt: EventMessage) -> Optional[Event]:
        pass  # TODO

    def to_json(self):
        return {
            "type_name": self.type_name
        }

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return QuestionsField.create_from_spreadsheet(spreadsheet)
