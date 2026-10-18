from dataclasses import dataclass


@dataclass(frozen=True)
class Parcel:
    weight_g: int
    length_cm: int
    width_cm: int
    height_cm: int


def volumetric_weight_g(parcel: Parcel) -> int:
    return parcel.length_cm * parcel.width_cm * parcel.height_cm * 1000 // 5000


def chargeable_weight_g(parcel: Parcel) -> int:
    return max(parcel.weight_g, volumetric_weight_g(parcel))
