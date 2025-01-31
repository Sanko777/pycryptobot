import os
import json
from models.PyCryptoBot import PyCryptoBot
from models.helper.LogHelper import Logger


class TelegramBotHelper:
    def __init__(self, app: PyCryptoBot) -> None:
        self.app = app
        self.market = app.getMarket()
        self.exchange = app.getExchange()
        self.botfolder = "telegram_data"
        self.botpath = os.path.join(self.app.telegramdatafolder, self.botfolder, self.market)
        self.filename = self.market + ".json"

        if not os.path.exists(self.botfolder):
            os.makedirs(self.botfolder)

        self.data = {}

        if not os.path.exists(os.path.join(self.app.telegramdatafolder, "telegram_data")):
            os.mkdir(os.path.join(self.app.telegramdatafolder, "telegram_data"))

        if os.path.isfile(os.path.join(self.app.telegramdatafolder, "telegram_data", self.filename)):
            self._read_data()
        else:
            ds = {'botcontrol' : {"status":"active", "manualsell" : False, "manualbuy" : False}}
            self.data = ds
            self._write_data()

        if os.path.isfile(os.path.join(self.app.telegramdatafolder, "telegram_data", "data.json")):
            self._read_data("data.json")
            if not "markets" in self.data:
                self.data.update({"markets": {}})
                self._write_data("data.json")
        else:
            ds = {"trades" : {}, "markets": {}}
            self.data = ds
            self._write_data("data.json")

    def _read_data(self, name: str = "") -> None:
        file = self.filename if name =="" else name
        with open(os.path.join(self.app.telegramdatafolder, 'telegram_data', file), 'r') as json_file:
            self.data = json.load(json_file)

    def _write_data(self, name: str = "") -> None:
        file = self.filename if name =="" else name
        try:
            with open(os.path.join(self.app.telegramdatafolder, 'telegram_data', file), 'w') as outfile:
                json.dump(self.data, outfile, indent=4)
        except Exception as err:
            Logger.critical(str(err))
            with open(os.path.join(self.app.telegramdatafolder, 'telegram_data', file), 'w') as outfile:
                json.dump(self.data, outfile, indent=4)
        
    def addmargin(self, margin: str = "", delta: str = "", price: str = ""):
        if self.app.enableTelegramBotControl():
            self._read_data()

            addmarket = {'exchange' : self.exchange, 'margin' : margin, 'delta' : delta, 'price' : price}
            self.data.update(addmarket)
            self._write_data()

    def addinfo(self, message: str = "", price: str = "") -> None:
        if self.app.enableTelegramBotControl():
            self._read_data()
            addmarket = {"message": message, "margin": " ", "delta": " ", "price" : price, "exchange" : self.exchange}
            self.data.update(addmarket)
            self._write_data()

    def addindicators(self, indicator, state) -> None:
        if self.app.enableTelegramBotControl():
            self._read_data()
            if not 'indicators' in self.data:
                self.data.update({"indicators": {}})

            self.data['indicators'].update({indicator : state})
            self._write_data()

    def deletemargin(self):
        if self.app.enableTelegramBotControl():
            os.remove(os.path.join(self.app.telegramdatafolder, 'telegram_data', self.filename))

    def closetrade(self, ts, price, margin):
        if self.app.enableTelegramBotControl():
            self._read_data("data.json")
            self.data['trades'].update({ts : {"pair" : self.market, "price" : price, "margin" : margin}})
            self._write_data("data.json")

    def checkmanualbuysell(self) -> str:
        result = "WAIT"
        if self.app.enableTelegramBotControl():
            self._read_data()

            if len(self.data['botcontrol']) > 0:
                if self.data["botcontrol"]["manualsell"]:
                    self.data["botcontrol"]["manualsell"] = False
                    result = "SELL"
                    self._write_data()

            if len(self.data['botcontrol']) > 0:
                if self.data["botcontrol"]["manualbuy"]:
                    self.data["botcontrol"]["manualbuy"] = False
                    result = "BUY"
                    self._write_data()

        return result

    def checkbotcontrolstatus(self) -> str:
        result = "active"
        if self.app.enableTelegramBotControl():
            self._read_data()
            result = self.data["botcontrol"]["status"]
            
        return result

    def updatebotstatus(self, status) -> None:
        if self.app.enableTelegramBotControl():
            self._read_data()
            if not self.data["botcontrol"]["status"] == status:
                self.data["botcontrol"]["status"] = status
                self._write_data()

    def removeactivebot(self) -> None:
        if self.app.enableTelegramBotControl():
            self.deletemargin()
