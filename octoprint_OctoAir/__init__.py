import octoprint.plugin
from octoprint.util import RepeatedTimer
import time
import board
import busio
import serial
import adafruit_sgp30
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
        self.sgp30.iaq_baseline(0x8973, 0x8AAE)

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

    def read_air_sensors(self):
        try:
            pm25_data = self.pm25.read()
            print()
            print("Concentration Units (standard)")
            print("---------------------------------------")
            print(
                "PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm25_data["pm10 standard"], pm25_data["pm25 standard"], pm25_data["pm100 standard"])
                )
            print("Concentration Units (environmental)")
            print("---------------------------------------")
            print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm25_data["pm10 env"], pm25_data["pm25 env"], pm25_data["pm100 env"]))
            print("---------------------------------------")
            print("Particles > 0.3um / 0.1L air:", pm25_data["particles 03um"])
            print("Particles > 0.5um / 0.1L air:", pm25_data["particles 05um"])
            print("Particles > 1.0um / 0.1L air:", pm25_data["particles 10um"])
            print("Particles > 2.5um / 0.1L air:", pm25_data["particles 25um"])
            print("Particles > 5.0um / 0.1L air:", pm25_data["particles 50um"])
            print("Particles > 10 um / 0.1L air:", pm25_data["particles 100um"])
            print("---------------------------------------")

        except RuntimeError:
            print("Unable to read from PM25 sensor")

        print("eCO2 = %d ppm \t TVOC = %d ppb" % (self.sgp30.eCO2, self.sgp30.TVOC))


__plugin_name__ = "Hello World"
__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_implementation__ = OctoAirPlugin()
