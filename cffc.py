import math
from primitives import Point, Polygon, create_arc_from_polar


class Turn:
    """Defines a middle layer turn of a CFFC inductor
    """

    def __init__(
        self,
        at,
        inner_radius: float,
        outer_radius: float,
        gap: float,
        angle: float,
        viastrip_angle: float,
        viastrip_width: float,
        layer: str,
    ):
        assert (
            outer_radius > inner_radius
        ), "outer radius must be greater than inner radius"

        # create the vias arcs
        a = math.asin(gap / 2 / inner_radius)
        b = viastrip_angle / 2
        c = math.asin(gap / 2 / outer_radius)
        start_via_arc = create_arc_from_polar(inner_radius, a + angle, b + angle)
        inner_arc = create_arc_from_polar(
            inner_radius + viastrip_width, b + angle, 2 * math.pi - b + angle
        )
        end_via_arc = create_arc_from_polar(
            inner_radius, 2 * math.pi - b + angle, 2 * math.pi - a + angle
        )
        outer_arc = create_arc_from_polar(
            outer_radius, 2 * math.pi - c + angle, c + angle
        )

        # create the polygon
        points = [start_via_arc, inner_arc, end_via_arc, outer_arc]
        self.polygon = Polygon(points, layer) + at

    def __str__(self):
        return self.polygon.__str__()


class Winding:
    def __init__(
        self,
        at: Point,
        inner_radius: float,
        outer_radius: float,
        number_turns: int,
        gap: float = 0.5,
    ):

        # calculate the angle we can allocate to the via transitions
        inner_circumfrance = 2 * math.pi * inner_radius

        viastrip_angle = (
            4
            * math.pi
            * (inner_circumfrance - (number_turns / 2) * gap)
            / inner_circumfrance
        ) / number_turns

        # calculate the required rotation per turn
        rotation = math.asin(gap / 2 / inner_radius) + viastrip_angle / 2

        # create the top and bottom turns
        top = Turn(at, inner_radius, outer_radius, gap, 0, viastrip_angle, 1, "F.Cu")
        inners = [
            Turn(
                at,
                inner_radius,
                outer_radius,
                gap,
                n * rotation,
                viastrip_angle,
                1,
                f"In{n}.Cu",
            )
            for n in range(1, number_turns - 1)
        ]
        bottom = Turn(
            at,
            inner_radius,
            outer_radius,
            gap,
            (number_turns - 1) * rotation,
            viastrip_angle,
            1,
            "B.Cu",
        )
        self.turns = [top] + inners + [bottom]

    def __str__(self):
        return "\n".join(turn.__str__() for turn in self.turns)


if __name__ == "__main__":
    at = Point(110, 110)

    # # create 4 turns
    # turn1 = Turn(at, 10, 15, 0.5, 0 * math.pi / 3, math.pi / 4, 1, "F.Cu")
    # turn2 = Turn(at, 10, 15, 0.5, 1 * math.pi / 3, math.pi / 4, 1, "In1.Cu")
    # turn3 = Turn(at, 10, 15, 0.5, 2 * math.pi / 3, math.pi / 4, 1, "In2.Cu")
    # turn4 = Turn(at, 10, 15, 0.5, 3 * math.pi / 3, math.pi / 4, 1, "In3.Cu")
    # turn5 = Turn(at, 10, 15, 0.5, 4 * math.pi / 3, math.pi / 4, 1, "In4.Cu")
    # turn6 = Turn(at, 10, 15, 0.5, 5 * math.pi / 3, math.pi / 4, 1, "B.Cu")
    # print(turn1)
    # print(turn2)
    # print(turn3)
    # print(turn4)
    # print(turn5)
    # print(turn6)

    winding = Winding(at, 10, 15, 6, 0.5)
    print(winding)
