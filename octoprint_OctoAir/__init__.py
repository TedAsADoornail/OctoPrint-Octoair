import octoprint.plugin
from octoprint.util import RepeatedTimer
import time
import adafruit_sgp30
import board
import busio
from flask import Response
import json
import serial
from adafruit_pm25.uart import PM25_UART


class OctoAirPlugin(octoprint.plugin.StartupPlugin,
                    octoprint.plugin.TemplatePlugin,
                    octoprint.plugin.SettingsPlugin,
                    octoprint.plugin.AssetPlugin):
    def __init__(self):
        octoprint.plugin.StartupPlugin.__init__(self)
        octoprint.plugin.TemplatePlugin.__init__(self)
        octoprint.plugin.SettingsPlugin.__init__(self)
        octoprint.plugin.AssetPlugin.__init__(self)
        self.reset_pin = None
        self.uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)
        self.pm25 = PM25_UART(self.uart, self.reset_pin)
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c)
        self.sgp30.iaq_init()
        self.sgp30.set_iaq_baseline(0x8973, 0x8AAE)

    def on_after_startup(self):
        self._logger.info("OctoAir running!")
        self.start_timer()

    def get_template_configs(self):
        return [
            dict(type="navbar", template="octoair_navbar.jinja2", custom_bindings=False),
            dict(type="settings", template="octoair_settings.jinja2", custom_bindings=False),
            dict(type="tab", name="Air Quality", template="octoair_tab.jinja2")
        ]

    def get_assets(self):
        return dict(
            js=["js/helloworld.js"]
        )

    def start_timer(self):
        """
        Function to start timer that checks enclosure temperature
        """

        self._check_temp_timer = RepeatedTimer(10, self.read_air_sensors)
        self._check_temp_timer.start()

    # ~~ Blueprintplugin mixin
    @octoprint.plugin.BlueprintPlugin.route("/inputs", methods=["GET"])
    def read_air_sensors(self):
        inputs = []
        try:
            pm25_data = self.pm25.read()
            pm25_types = {"pm10 standard", "pm25 standard", "pm100 standard", "pm10 env", "pm25 env", "pm100 env", "particles 03um", "particles 05um", "particles 10um", "particles 25um", "particles 50um", "particles 100um"}
            sgp30_types = {self.sgp30.TVOC, self.sgp30.eCO2}
            for pm25_type in pm25_types:
                inputs.append(dict(index_id=pm25_type, label="PM25", State=pm25_data[pm25_type]))
            inputs.append(dict(index_id="SGP30_TVOC", label="SGP30", State=self.sgp30.TVOC))
            inputs.append(dict(index_id="SGP30_eCO2", label="SGP30", State=self.sgp30.eCO2))
        except RuntimeError:
            print("Unable to read from PM25 sensor")
        return Response(json.dumps(inputs), mimetype='application/json')


__plugin_name__ = "Hello World"
__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_implementation__ = OctoAirPlugin()
