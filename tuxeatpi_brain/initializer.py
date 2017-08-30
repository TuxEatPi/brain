"""Module customizing initialization for the Brain component"""
import yaml

from tuxeatpi_common.initializer import Initializer
from tuxeatpi_brain.error import BrainError


class BrainInitializer(Initializer):
    """Custom initializer for the Brain component"""

    def __init__(self, component, skip_dialogs=False, skip_intents=False, skip_settings=False):
        Initializer.__init__(self, component, skip_dialogs, skip_intents, skip_settings)

    def _read_config_file(self):
        """Read config file and save it in Etcd"""
        with open(self.component.config_file) as fconf:
            try:
                self.component.full_config = yaml.load(fconf)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                raise BrainError("Bad file content")
        # TODO validate global config
        global_config = self.component.full_config.get('global', {})
        self.component.settings.nlu_engine = global_config.get("nlu_engine")
        self.component.settings.language = global_config.get("language")
        # Store config file to etcd
        for key, value in self.component.full_config.items():
            self.component.settings.save(value, key)
        self.logger.debug("Config loaded: %s", self.component.full_config)

    def update_global(self):
        """Update global settings in Etcd"""
        global_config = self.component.full_config.get('global')
        self.component.settings.save(global_config, 'global')

    def run(self):
        """Run method overriding the standard one"""
        # Read config file
        self._read_config_file()
        # Standard start
        Initializer.run(self)
