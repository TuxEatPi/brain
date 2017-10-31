import json
import threading
import time

import pytest

from tuxeatpi_brain.daemon import Brain
from tuxeatpi_brain.error import BrainError
from tuxeatpi_common.message import Message
from wampy.peers.clients import Client


class FakeWampClient(Client):

    def fake_say(self, text):
        return


class TestBrain(object):

    @classmethod
    def setup_class(self):
        workdir = "tests/brain_test/workdir"
        intents = "intents"
        dialogs = "dialogs"
        config_file = "tests/tests.yaml"
        self.brain = Brain("brain", workdir, intents, dialogs, config_file=config_file)
        self.thread = threading.Thread(target=self.brain.start)

        self.wclient = FakeWampClient(realm="tuxeatpi")
        self.wclient.start()
        self.wclient.session._register_procedure("speech.say")
        setattr(self.wclient, "speech.say", self.wclient.fake_say)

    @classmethod
    def teardown_class(self):
        self.brain.settings.delete("/config/global")
        self.brain.settings.delete("/config/fakecomponent")
        self.brain.settings.delete()
        self.brain.registry.clear()
        self.brain.shutdown()
        self.thread.join()
        self.wclient.stop()

    @pytest.mark.order1
    def test_brain(self, capsys):
        # --help
        self.thread.start()

        # Wait for start
        time.sleep(2)

        assert self.brain.settings.language == "en_US"
        self.brain.changelang("fr_FR")

        time.sleep(1)

        assert self.brain.settings.language == "fr_FR"
        self.brain.changelang("fr_FR")
        assert self.brain.settings.language == "fr_FR"

        data = self.brain.settings.etcd_wrapper.read("/config/fakecomponent")
        assert json.loads(data.value) == {"arg1": "value1"}

        # Fake component to simulate NOT ALIVE state
        data = {"name": "fakecomponent",
                "version": "0.0",
                "date": time.time(),
                "state": "ALIVE"}
        self.brain.registry.etcd_wrapper.write("/registry/fakecomponent", data)
        time.sleep(5)
        assert "fakecomponent" in self.brain._states
        assert self.brain._states.get('fakecomponent', {}).get('state') == "ALIVE"
        # Wait 33 sec to get fakecomponent not alive
        time.sleep(33)
        assert self.brain._states.get('fakecomponent', {}).get('state') == "NOT ALIVE"

    @pytest.mark.order2
    def test_bad_file(self):
        # bad config file
        workdir = "tests/brain_test/workdir"
        intents = "intents"
        dialogs = "dialogs"
        config_file = "non_exist_file"
        self.brain = Brain("brain", workdir, intents, dialogs, config_file=config_file)
        with pytest.raises(FileNotFoundError):
            self.brain.start()

    @pytest.mark.order3
    def test_bad_content(self):
        workdir = "tests/brain_test/workdir"
        intents = "intents"
        dialogs = "dialogs"
        config_file = "tests/bad_config.yaml"
        self.brain = Brain("brain", workdir, intents, dialogs, config_file=config_file)
        with pytest.raises(BrainError) as exp:
            self.brain.start()
            assert exp == "Bad file content"
