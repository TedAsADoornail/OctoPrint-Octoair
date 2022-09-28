$(function() {
    function OctoAirViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.currentUrl = ko.observable();
        self.newUrl = ko.observable();
        self.goToUrl = function() {
            self.currentUrl(self.newUrl());
        };

        self.rpi_outputs = ko.observableArray();

        self.rpi_inputs_temperature_sensors = ko.pureComputed(function () {
        return ko.utils.arrayFilter(self.rpi_inputs(), function (item) {
            return (item.input_type() === "temperature_sensor");
            });
        });

        self.hasAnySensorWithHumidity = function(){
        return_value = false;
        self.rpi_inputs_temperature_sensors().forEach(function (sensor) {
        if (self.humidityCapableSensor(sensor.temp_sensor_type())) {
          return_value = true;
          return false;
        }
      });
      return return_value;
    };

        self.hasAnyTemperatureControl = function(){
      return_value = false
      self.rpi_outputs().forEach(function (output) {
        if (output.output_type()=="temp_hum_control") {
          return_value = true
          return false;
        }
      });
      return return_value;
    };

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
