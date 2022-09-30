$(function() {
    function OctoAirViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];

        self.rpi_inputs = ko.observableArray();

        self.rpi_inputs_pm25_sensors = ko.pureComputed(function () {
            return ko.utils.arrayFilter(self.rpi_inputs(), function (item) {
                return (item.input_type() === "particles 25um");
                });
            }
        );

        self.onBeforeBinding = function() {
            self.bindFromSettings();
        }

        self.bindFromSettings = function() {
            self.rpi_inputs(self.settingsViewModel.settings.plugins.enclosure.rpi_inputs());
        }

        self.addRpiInput = function () {
            self.settingsViewModel.settings.plugins.enclosure.rpi_inputs.push({
                index_id: ko.observable("Index"),
                label: ko.observable("Input")
            });
        };
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
