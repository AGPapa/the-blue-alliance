from consts.notification_type import NotificationType
from helpers.model_to_dict import ModelToDict
from notifications.base_notification import BaseNotification


class AllianceSelectionNotification(BaseNotification):

    def __init__(self, event):
        self.event = event

    @property
    def _type(self):
        return NotificationType.ALLIANCE_SELECTION

    def _build_dict(self):
        data = {}
        data['message_type'] = NotificationType.type_names[self._type]
        data['message_data'] = {}
        data['message_data']['event'] = ModelToDict.eventConverter(self.event)
        return data
