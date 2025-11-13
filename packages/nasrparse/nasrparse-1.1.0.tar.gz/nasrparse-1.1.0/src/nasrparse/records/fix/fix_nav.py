from nasrparse.functions import to_nullable_float, to_nullable_string

from ._base import Base


class FIX_NAV(Base):
    nav_id: str | None
    """NAVAID Identifier."""
    nav_type: str | None
    """Facility Type."""
    bearing: float | None
    """Bearing, Radial, Direction or Course depending on Facility Type."""
    distance: float | None
    """DME Distance from Facility."""

    def __init__(
        self,
        eff_date: str,
        fix_id: str,
        icao_region_code: str,
        state_code: str,
        country_code: str,
        nav_id: str,
        nav_type: str,
        bearing: str,
        distance: str,
    ) -> None:
        super().__init__(
            "fix_navigations",
            eff_date,
            fix_id,
            icao_region_code,
            state_code,
            country_code,
        )
        self.nav_id = to_nullable_string(nav_id)
        self.nav_type = to_nullable_string(nav_type)
        self.bearing = to_nullable_float(bearing)
        self.distance = to_nullable_float(distance)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"NAV_ID={self.nav_id!r}, "
            f"NAV_TYPE={self.nav_type!r}, "
            f"BEARING={self.bearing!r}, "
            f"DISTANCE={self.distance!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "nav_id",
                "nav_type",
                "bearing",
                "distance",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "nav_id": self.nav_id,
            "nav_type": self.nav_type,
            "bearing": self.bearing,
            "distance": self.distance,
        }
        return {**base_dict, **this_dict}

    def to_str(self) -> str:
        return (
            f"{super().to_str()}"
            f"nav_id: {self.nav_id}, "
            f"nav_type: {self.nav_type}, "
            f"bearing: {self.bearing}, "
            f"distance: {self.distance}"
        )
