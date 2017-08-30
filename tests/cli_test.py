import logging
import os
import sys
import time

import pytest
from click.testing import CliRunner

from tuxeatpi_brain.error import BrainError



class TestCli(object):

    @pytest.mark.order1
    def test_help(self, capsys):
        # --help
        runner = CliRunner()
        sys.argv = ['fakedaemon', '-I', 'tests/brain_test/intents/', '-w', 'tests/brain_test/workdir/', '-D', 'tests/brain_test/dialogs', '-c', 'tests/bad_config.yaml']
        with pytest.raises(BrainError):
            from tuxeatpi_brain.common import cli
