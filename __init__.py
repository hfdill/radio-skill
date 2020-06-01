import sys
from os.path import dirname, abspath
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.util import play_mp3
import time
import subprocess
import vlc
  
sys.path.append(abspath(dirname(__file__)))
stream_data = __import__('stream_data')

logger = getLogger(__name__)

#__author__ = 'tjoen'
# modified by hfdill to fix bugs and make it play requested broadcast station
# player changed to vlc
__author__ = 'tjoen'


class Radio(MycroftSkill):
    def __init__(self):
        super(Radio, self).__init__('Radio')
        self.stream_data = stream_data.DutchRadio()
        self.process = None

    def initialize(self):
        logger.info('initializing Radio')
        self.load_data_files(dirname(__file__))
        super(Radio, self).initialize()

        for c in self.stream_data.channels.keys():
            self.register_vocabulary(c, 'ChannelKeyword')
        intent = IntentBuilder('PlayChannelIntent' + self.name)\
            .require('PlayKeyword')\
            .require('ChannelKeyword')\
            .build()
        self.register_intent(intent, self.handle_play_channel)
        intent = IntentBuilder('PlayFromIntent' + self.name)\
            .require('PlayKeyword')\
            .require('ChannelKeyword')\
            .require('NameKeyword')\
            .build()
        self.register_intent(intent, self.handle_play_channel)

    def before_play(self):
        """
           Stop currently playing media before starting the new. This method
           should always be called before the skill starts playback.
        """
        logger.info('Stopping currently playing media if any')
        if self.process:
            self.stop()

    def play(self):
        self.before_play()
        self.speak_dialog('Tuning to requested station', {'channel_name': self.channel})
        
#        time.sleep(3)
        stream_url = self.stream_data.channels[self.channel].stream_url
        self.process = subprocess.Popen(['cvlc', stream_url])
        
    def get_available(self, channel_name):
        logger.info(channel_name)
        if channel_name in self.stream_data:
            logger.info('Registring play intention...')
            return channel_name
        else:
            return None

    def prepare(self, channel_name):
        if self.process:
            self.stop()
        self.channel = channel_name

    def handle_play_channel(self, message):
        logger.debug( message.data )
        c = message.data.get('ChannelKeyword')
        self.prepare(c)
        self.play()

    def stop(self, message=None):
        logger.info('Handling stop request')
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            self.channel = None

    def handle_currently_playing(self, message):
        if self.channel is not None:
            self.speak_dialog('currently_playing', {'channel': self.channel})


def create_skill():
    return Radio()
