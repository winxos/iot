# coding:utf-8
# winxos 2017-7-7
class Agent:
    pass


class SimBike(Agent):
    def __init__(self, id):
        self.id = id
        self.server_info = ""

    def _unlock(self):
        pass

    def _send_to_server(self):
        pass

    def _report_location(self):
        pass

    def lock(self):
        pass


class BikeFactory:
    @staticmethod
    def create_bike():
        return SimBike()

    @staticmethod
    def _create_qrcode():
        pass


class Rider:
    def scan_qrcode(self, qrcode_txt):
        pass
