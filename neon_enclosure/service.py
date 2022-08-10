from ovos_PHAL import PHAL


class NeonHardwareAbstractionLayer(PHAL):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def shutdown(self):
        self.status.set_stopping()
