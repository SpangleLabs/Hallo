import logging
from abc import ABCMeta
from datetime import date

from hallo.events import (
    EventMessage,
)
import hallo.modules.dailys.field_dream
import hallo.modules.dailys.field_duolingo
import hallo.modules.dailys.field_fa
import hallo.modules.dailys.field_mood
import hallo.modules.dailys.field_sleep

logger = logging.getLogger(__name__)


class DailysException(Exception):
    pass


class DailysField(metaclass=ABCMeta):
    # An abstract class representing an individual dailys field type.
    # A field can/will be multiple columns, maybe a varying quantity of them by configuration
    type_name = None

    def __init__(self, spreadsheet):
        """
        :type spreadsheet: hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet
        """
        self.spreadsheet = spreadsheet
        """ :type : DailysSpreadsheet"""

    @staticmethod
    def create_from_input(event, spreadsheet):
        """
        :type event: EventMessage
        :type spreadsheet: hallo.modules.dailys.dailys_spreadsheet.DailysSpreadsheet
        :rtype: DailysField
        """
        raise NotImplementedError()

    @staticmethod
    def passive_events():
        raise NotImplementedError()

    def passive_trigger(self, evt):
        """
        :type evt: Event.Event
        :rtype: None
        """
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()

    @staticmethod
    def from_json(json_obj, spreadsheet):
        raise NotImplementedError()

    def save_data(self, data, data_date):
        """
        :type data: dict
        :type data_date: date
        """
        self.spreadsheet.save_field(self, data, data_date=data_date)

    def load_data(self, data_date):
        """
        :type data_date: date
        :rtype: dict | None
        """
        return self.spreadsheet.read_field(self, data_date)

    def message_channel(self, text):
        """
        :type text: str
        :rtype : EventMessage
        """
        evt = EventMessage(
            self.spreadsheet.destination.server,
            self.spreadsheet.destination,
            self.spreadsheet.user,
            text,
            inbound=False,
        )
        self.spreadsheet.user.server.send(evt)
        return evt


class DailysFieldFactory:
    fields = [
        hallo.modules.dailys.field_fa.DailysFAField,
        hallo.modules.dailys.field_duolingo.DailysDuolingoField,
        hallo.modules.dailys.field_sleep.DailysSleepField,
        hallo.modules.dailys.field_mood.DailysMoodField,
        hallo.modules.dailys.field_dream.DailysDreamField
    ]

    @staticmethod
    def from_json(json_obj, spreadsheet):
        type_name = json_obj["type_name"]
        for field in DailysFieldFactory.fields:
            if field.type_name == type_name:
                return field.from_json(json_obj, spreadsheet)
        raise DailysException(
            "Could not load dailys field of type {}".format(type_name)
        )


class DailysAnimalsField(DailysField):
    # Does animal sightings measurements

    def get_animal_list(self):
        # Return a list of animals which are being logged
        pass


class DailysSplooField(DailysField):
    pass


class DailysShowerField(DailysField):
    # Temperature, song, whatever
    pass


class DailysCaffeineField(DailysField):
    # At new_day(), can input N, none if there's no entry today
    pass


class DailysShavingField(DailysField):
    # At new_day(), can input N, N, none, none if there's no entry today
    pass


class DailysGoogleMapsField(DailysField):
    # Get distances/times from google maps?
    # Get work times
    pass


class DailysMyFitnessPalField(DailysField):
    # Weight, maybe food things
    pass


class DailysAlcoholField(DailysField):
    pass


class DailysShutdownField(DailysField):
    # Not sure on this? Teeth, multivitamins, clothes out, maybe diary?, trigger mood measurement?
    # Night is done after shutdown.
    # new_day() triggers N, N, N entries.
    pass
