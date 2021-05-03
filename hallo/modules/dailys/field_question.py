import datetime
from threading import RLock
from typing import Optional, Dict, List

import dateutil.parser
import isodate

import hallo.modules.dailys.dailys_field
from hallo.events import EventMessage, EventMinute, Event, RawDataTelegramOutbound, RawDataTelegram
import hallo.modules.dailys.dailys_spreadsheet


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
        self.start: datetime.datetime = dateutil.parser.parse(start)
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

    def create_answer_for_time(
            self,
            asked_time: datetime.datetime,
            *,
            answer: Optional[str] = None,
            answer_time: Optional[datetime.datetime] = None,
            question_msg_id: Optional[int] = None
    ) -> 'Answer':
        if answer_time is None:
            answer_time = datetime.datetime.now(tz=datetime.timezone.utc)
        return Answer(
            self.id,
            asked_time,
            answer=answer,
            answer_time=answer_time,
            question_msg_id=question_msg_id
        )

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


class AnswerEdit:
    def __init__(
            self,
            answer: str,
            answer_time: datetime.datetime
    ):
        self.answer = answer
        self.answer_time = answer_time

    def to_dict(self) -> Dict:
        return {
            "answer": self.answer,
            "answer_time": self.answer_time.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'AnswerEdit':
        return cls(
            data["answer"],
            dateutil.parser.parse(data["answer_edit"])
        )


class Answer:
    def __init__(
            self,
            question_id: str,
            asked_time: datetime.datetime,
            *,
            answer: Optional[str] = None,
            answer_time: Optional[datetime.datetime] = None,
            edit_history: Optional[List[AnswerEdit]] = None,
            question_msg_id: Optional[int] = None,
    ):
        self.answer = answer
        self.answer_time = answer_time
        self.asked_time = asked_time
        self.question_id = question_id
        self.question_msg_id = question_msg_id
        self.edit_history = edit_history or []

    @property
    def answered(self) -> bool:
        return self.answer is not None

    def for_question(self, question: 'Question') -> bool:
        return self.question_id == question.id

    def same_answer(self, other: 'Answer') -> bool:
        return self.question_id == other.question_id and self.asked_time == other.asked_time

    def add_answer(self, answer: str) -> None:
        if self.answer is not None:
            new_edit = AnswerEdit(self.answer, self.answer_time)
            self.edit_history.append(new_edit)
        self.answer = answer
        self.answer_time = datetime.datetime.now(datetime.timezone.utc)

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
            edit_history=json_dict.get("edit_history", []),
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
        if self.edit_history:
            d["edit_history"] = [e.to_dict() for e in self.edit_history]
        if self.question_msg_id:
            d["q_message_id"] = self.question_msg_id
        return d


class AnswersData:
    def __init__(self, spreadsheet: 'hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet'):
        self.spreadsheet = spreadsheet

    def get_answer_for_question_at_time(
            self,
            question: Question,
            answer_datetime: datetime.datetime
    ) -> Optional[Answer]:
        date_answers = self.get_answers_for_date(answer_datetime.date())
        for answer in date_answers:
            if answer.for_question(question) and answer.asked_time == answer_datetime:
                return answer
        return None

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

    def answer_for_question_msg_id(
            self,
            question_msg_id: int,
            questions: List[Question],
            *,
            assume_incremental_id: bool = True
    ) -> Optional[Answer]:
        if not questions:
            return None
        oldest_date = min([q.time_pattern.start.date() for q in questions])
        test_date = datetime.datetime.now(datetime.timezone.utc).date()
        while test_date > oldest_date:
            self._populate_answers_for_date(test_date)
            lowest_msg_id = None
            for question_id, answer_dict in self._cache.get(test_date, {}):
                for answer_time, answer in answer_dict:
                    if answer.question_msg_id is None:
                        continue
                    # If message ID matches, that's the right one
                    if answer.question_msg_id == question_msg_id:
                        return answer
                    # Update lowest message id for the day
                    if lowest_msg_id is None:
                        lowest_msg_id = answer.question_msg_id
                    else:
                        lowest_msg_id = min(answer.question_msg_id)
            # If chat has incremental message IDs, then we can end early if IDs are lower than the one we're looking for
            if assume_incremental_id:
                if lowest_msg_id < question_msg_id:
                    return None
        # Ran out of dates, return None
        return None


class QuestionsField(hallo.modules.dailys.dailys_field.DailysField):
    type_name = "questions"

    def __init__(
            self,
            spreadsheet: hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet,
            questions: List[Question]
    ):
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

    def _msg_trigger(self, evt: EventMessage) -> None:
        # Check if it's a reply to a question
        if (
            isinstance(evt.raw_data, RawDataTelegram)
            and evt.raw_data.update_obj.message.reply_to_message is not None
        ):
            reply_id = (
                evt.raw_data.update_obj.message.reply_to_message.message_id
            )
            return self._handle_answer_reply(evt, reply_id, evt.text)
        # Handle manual answers
        text_split = evt.text.split(maxsplit=2)
        question_dict = {q.id: q for q in self.questions}
        if text_split[0].lower() == "answer" and text_split[1] in question_dict:
            return self._handle_answer_manual(evt, question_dict[text_split[1]], text_split[2])

    def _handle_answer_reply(self, evt: EventMessage, reply_id: int, answer: str) -> None:
        cache = AnswerCache(self.data)
        reply_answer = cache.answer_for_question_msg_id(reply_id, self.questions)
        if reply_answer is None:
            return None
        reply_answer.add_answer(answer)
        self.data.save_answer(reply_answer)
        evt.create_response(
            f"Answer saved for question ID \"{reply_answer.question_id}\", at {reply_answer.asked_time.isoformat()}"
        )

    def _handle_answer_manual(self, evt: EventMessage, question: Question, answer: str) -> None:
        latest_time = question.time_pattern.last_time()
        current_answer = self.data.get_answer_for_question_at_time(question, latest_time)
        if current_answer is None:
            new_answer = question.create_answer_for_time(
                latest_time,
                answer=answer
            )
            self.data.save_answer(new_answer)
            evt.create_response(f"Answer saved for question ID \"{question.id}\", at {latest_time.isoformat()}")
            return
        current_answer.add_answer(answer)
        self.data.save_answer(current_answer)
        evt.create_response(f"Answer saved for question ID \"{question.id}\", at {latest_time.isoformat()}")

    def to_json(self):
        return {
            "type_name": self.type_name
        }

    @staticmethod
    def from_json(json_obj, spreadsheet):
        return QuestionsField.create_from_spreadsheet(spreadsheet)
