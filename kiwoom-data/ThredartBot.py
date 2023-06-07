import telepot
from Config import *


class ThredartBot():
	def __init__(self):
		self.token = TB_TOKEN
		self.bot = telepot.Bot(self.token)
		
	def sendMessage(self, msg):
		self.bot.sendMessage(TB_DATA_COLLECTOR_CHANNEL_CHATID, msg)