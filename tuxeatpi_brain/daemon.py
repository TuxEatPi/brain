"""Module defining Brain component"""
import logging
import time

from tuxeatpi_common.daemon import TepBaseDaemon
from tuxeatpi_common.message import Message, is_mqtt_topic

from tuxeatpi_brain.initializer import BrainInitializer


class Brain(TepBaseDaemon):
    """Brain component class

    This component handle configuration and component registry
    """

    def __init__(self, name, workdir, intent_folder, dialog_folder,
                 logging_level=logging.INFO, config_file=None):
        TepBaseDaemon.__init__(self, name, workdir, intent_folder, dialog_folder, logging_level)
        # Other component states
        self._states = {}
        # Config file
        self.config_file = config_file
        self.full_config = {}
        # Skip witing for config
        self._initializer = BrainInitializer(self, False, False, True)

    @is_mqtt_topic("help")
    def help_(self):
        """Return help for this daemon"""
        pass

    def set_config(self, config):
        pass

    @is_mqtt_topic("changelang")
    def changelang(self, language):
        """Change the language for all components"""
        if language == self.settings.language:
            # No change
            # Prepare message and send message
            dialog = self.get_dialog("no_language_change")
            data = {"arguments": {"text": dialog}}
            topic = "speech/say"
            message = Message(topic=topic, data=data)
            self.publish(message)
            return
        self.full_config['global']['language'] = language
        # Prepare message and send message
        dialog = self.get_dialog("loading_language")
        data = {"arguments": {"text": dialog}}
        topic = "speech/say"
        message = Message(topic=topic, data=data)
        self.publish(message)
        # Update global config
        self._initializer.update_global()
        # Prepare message and send it with the new language
        dialog = self.get_dialog("loaded_language")
        data = {"arguments": {"text": dialog}}
        topic = "speech/say"
        message = Message(topic=topic, data=data)
        self.publish(message)

    def main_loop(self):
        """Main Loop"""
        self._states = self.registry.read()
        self.logger.debug(self._states)
        for state in self._states.values():
            if state['name'] == 'brain':
                continue
            if state['state'] != "NOT ALIVE" and time.time() > state['date'] + 30:
                self.registry.set_notalive(state)
        time.sleep(1)
