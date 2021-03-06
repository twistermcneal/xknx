from homeassistant.components.binary_sensor import BinarySensorDevice

class XKNXBinarySensor(BinarySensorDevice):

    def __init__(self, hass, device):
        self.device = device
        self.hass = hass
        self.register_callbacks()


    @property
    def should_poll(self):
        """No polling needed for a demo sensor."""
        return False


    def register_callbacks(self):
        def after_update_callback(device):
            # pylint: disable=unused-argument
            self.update_ha()
        self.device.after_update_callback = after_update_callback


    def update_ha(self):
        self.hass.async_add_job(self.async_update_ha_state())

    @property
    def name(self):
        """Return the name of the light if any."""
        return self.device.name


    @property
    def sensor_class(self):
        """Return the class of this sensor."""
        return self.device.sensor_class


    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.device.binary_state()
