$(function() {
    function OctoAirViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.currentUrl = ko.observable();
        self.newUrl = ko.observable();
        self.goToUrl = function() {
            self.currentUrl(self.newUrl());
        };

        self.rpi_inputs = ko.observableArray();

        self.addRpiInput = function () {

          var arrRelaysLength = self.settingsViewModel.settings.plugins.enclosure.rpi_inputs().length;

          var nextIndex = arrRelaysLength == 0 ? 1 : self.settingsViewModel.settings.plugins.enclosure.rpi_inputs()[arrRelaysLength - 1].index_id() + 1;

          self.settingsViewModel.settings.plugins.enclosure.rpi_inputs.push({
            index_id: ko.observable(nextIndex),
            label: ko.observable("Input " + nextIndex),
            input_type: ko.observable("gpio"),
            gpio_pin: ko.observable(0),
            input_pull_resistor: ko.observable("input_pull_up"),
            temp_sensor_type: ko.observable("DS18B20"),
            temp_sensor_address: ko.observable(""),
            temp_sensor_temp: ko.observable(""),
            temp_sensor_humidity: ko.observable(""),
            ds18b20_serial: ko.observable(""),
            use_fahrenheit: ko.observable(false),
            action_type: ko.observable("output_control"),
            controlled_io: ko.observable(""),
            controlled_io_set_value: ko.observable("low"),
            edge: ko.observable("fall"),
            printer_action: ko.observable("filament"),
            temp_sensor_navbar: ko.observable(true),
            filament_sensor_timeout: ko.observable(120),
            filament_sensor_enabled: ko.observable(true),
            temp_sensor_i2cbus: ko.observable(1),
            temp_i2c_bus: ko.observable(1),
            temp_i2c_address: ko.observable(1),
            temp_i2c_register: ko.observable(1),
            show_graph_temp: ko.observable(false),
            show_graph_humidity: ko.observable(false)
          });
        };

        self.rpi_inputs_pm25_sensors = ko.pureComputed(function () {
            return ko.utils.arrayFilter(self.rpi_inputs(), function (item) {
                return (item.input_type() === "PM25");
                });
            }
        );

        self.onBeforeBinding = function() {
            self.newUrl(self.settings.settings.plugins.helloworld.url());
            self.goToUrl();
        }
    }

    // This is how our plugin registers itself with the application, by adding some configuration
    // information to the global variable OCTOPRINT_VIEWMODELS
    OCTOPRINT_VIEWMODELS.push([
        // This is the constructor to call for instantiating the plugin
        OctoAirViewModel,

        // This is a list of dependencies to inject into the plugin, the order which you request
        // here is the order in which the dependencies will be injected into your view model upon
        // instantiation via the parameters argument
        ["settingsViewModel"],

        // Finally, this is the list of selectors for all elements we want this view model to be bound to.
        ["#tab_plugin_octoair"]
    ]);
});
