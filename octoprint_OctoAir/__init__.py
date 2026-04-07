import time
import json
import serial
import board
import busio
import octoprint.plugin
from flask import Response
from octoprint.util import RepeatedTimer
import adafruit_sgp30
from adafruit_pm25.uart import PM25_UART

class OctoAirPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin
):
    def __init__(self):
        super().__init__()
        self.rpi_inputs = []
        self.reset_pin = None
        self.uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)
        self.pm25 = PM25_UART(self.uart, self.reset_pin)
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c)
        self.sgp30.iaq_init()
        self.sgp30.set_iaq_baseline(0x8973, 0x8AAE)
        self._check_temp_timer = None

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
            js=["js/octoair.js"]
        )

    def start_timer(self):
        """Start a timer to periodically check enclosure air sensors."""
        self._check_temp_timer = RepeatedTimer(10, self.read_air_sensors)
        self._check_temp_timer.start()

    @octoprint.plugin.BlueprintPlugin.route("/inputs", methods=["GET"])
    def read_air_sensors(self):
        """Read air sensor data and return as JSON response."""
        inputs = []
        try:
            pm25_data = self.pm25.read()
            pm25_types = {
                "pm10 standard", "pm25 standard", "pm100 standard",
                "pm10 env", "pm25 env", "pm100 env",
                "particles 03um", "particles 05um", "particles 10um",
                "particles 25um", "particles 50um", "particles 100um"
            }
            for pm25_type in pm25_types:
                inputs.append(dict(
                    index_id=pm25_type,
                    label="PM25",
                    State=pm25_data[pm25_type]
                ))
            inputs.append(dict(
                index_id="SGP30_TVOC",
                label="SGP30",
                State=self.sgp30.TVOC
            ))
            inputs.append(dict(
                index_id="SGP30_eCO2",
                label="SGP30",
                State=self.sgp30.eCO2
            ))
        except RuntimeError as e:
            self._logger.error(f"Unable to read from PM25 sensor: {e}")
        return Response(json.dumps(inputs), mimetype='application/json')

__plugin_name__ = "OctoAir"
__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_implementation__ = OctoAirPlugin()
