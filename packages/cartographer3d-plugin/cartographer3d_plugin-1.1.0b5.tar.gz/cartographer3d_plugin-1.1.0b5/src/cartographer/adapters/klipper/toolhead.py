from typing_extensions import override

from cartographer.adapters.klipper_like.toolhead import KlipperLikeToolhead


class KlipperToolhead(KlipperLikeToolhead):
    @override
    def get_max_accel(self) -> float:
        return self.toolhead.get_max_velocity()[1]

    @override
    def set_max_accel(self, accel: float) -> None:
        _ = self.toolhead.set_max_velocities(None, accel, None, None)
