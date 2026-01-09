from turtle import (
    forward,
    left,
    right,
    penup,
    pendown,
    goto,
    setheading,
    home,
    exitonclick,
    speed,
    hideturtle,
)
from random import randint, uniform
from math import asin, sin, pi

speed(0)
hideturtle()


def nakresli_ctverec(delka_strany):
    for _ in range(4):
        forward(delka_strany)
        left(90)


def domecek_jednim_tahem(delka_strany):
    # draws a square (base from current position, heading -> to the right)
    for _ in range(4):
        forward(delka_strany)
        left(90)
    # draw simple roof
    left(45)
    forward(delka_strany * (2 ** 0.5))
    left(90)
    forward(delka_strany * (2 ** 0.5) / 2)
    left(90)
    forward(delka_strany * (2 ** 0.5) / 2)
    left(90)
    forward(delka_strany * (2 ** 0.5))
    left(45)


def compute_radius(sizes, tol=1e-9, max_iter=200):
    """
    Given a list of base sizes, find circle radius r so that
    sum(2*asin((s/2)/r) for s in sizes) == 2*pi.
    Uses exponential search to find an upper bound then binary search.
    """
    if not sizes:
        raise ValueError("sizes must be non-empty")

    half_max = max(s / 2.0 for s in sizes)
    low = half_max * 1.0000001

    def total_angle(r):
        return sum(2 * asin((s / 2.0) / r) for s in sizes)

    # find high where total_angle(high) < 2*pi
    high = low * 2.0
    for _ in range(1000):
        ta = total_angle(high)
        if ta < 2 * pi:
            break
        high *= 2.0

    # binary search
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        ta = total_angle(mid)
        if abs(ta - 2 * pi) < tol:
            return mid
        if ta > 2 * pi:
            low = mid
        else:
            high = mid

    return (low + high) / 2.0


def rada_domecku(pocet_domecku, min_side=20, max_side=60, initial_radius=None, ccw=True):
    """
    Draw pocet_domecku houses around a circle.
    - First (pocet_domecku - 1) houses get random sizes in [min_side, max_side].
    - The last house size is computed so the sum of subtended angles equals 2*pi (perfect circle).
    - Houses are placed tangent to the circle of radius r; r is increased if necessary so all asin() calls are valid.

    Input/Output contract:
    - inputs: number of houses, min and max side lengths, optional initial radius
    - behavior: draws houses around origin forming a closed circular ring
    """
    # If caller passed a sizes list, compute radius directly.
    if isinstance(pocet_domecku, (list, tuple)):
        sizes = list(pocet_domecku)
        r = compute_radius(sizes)
        angles = [2 * asin((s / 2.0) / r) for s in sizes]
    else:
        # generate random sizes for first n-1 houses
        n = pocet_domecku
        sizes = [uniform(min_side, max_side) for _ in range(n - 1)]

        # pick starting radius if provided, else pick reasonable default
        if initial_radius is None:
            r = max(max(sizes) * 2.0, max_side * 2.0)
        else:
            r = initial_radius

        # ensure radius large enough so s/2 <= r for all sizes
        max_attempts = 200
        for _ in range(max_attempts):
            # compute angles for existing sizes
            angles = []
            valid = True
            for s in sizes:
                val = (s / 2.0) / r
                if val >= 1.0:
                    valid = False
                    break
                angles.append(2 * asin(val))
            if not valid:
                r *= 1.5
                continue

            total_angle = sum(angles)
            if total_angle >= 2 * pi:
                # too large, increase radius and retry
                r *= 1.5
                continue

            # compute remaining angle for last house
            remaining = 2 * pi - total_angle
            # ensure remaining positive and correspond to a feasible side length
            if remaining <= 0:
                r *= 1.5
                continue

            # compute final side length from remaining angle
            last_s = 2 * r * sin(remaining / 2.0)
            # if last_s is pathological (too small/large), adjust radius and retry
            if last_s <= 1 or last_s > max_side * 5:
                r *= 1.5
                continue

            sizes.append(last_s)
            angles.append(remaining)
            break
        else:
            raise RuntimeError("Failed to find suitable radius/last house size")

    # draw each house: place it so its base is tangent to the circle at radius r
    sign = 1 if ccw else -1
    cumulative_angle = 0.0
    for s, theta in zip(sizes, angles):
        # middle angle for this house (signed for direction)
        mid = cumulative_angle + sign * (theta / 2)

        # move to midpoint on circle
        penup()
        home()
        setheading(mid * 180.0 / pi)
        forward(r)

        # now move to left corner of the base: set heading tangent (use sign to pick side)
        setheading(mid * 180.0 / pi + sign * 90)
        backward_amount = s / 2.0
        # turtle doesn't have a named backward import, use forward with negative distance
        forward(-backward_amount)

        # face along base (tangent) and draw
        setheading(mid * 180.0 / pi + sign * 90)
        pendown()
        domecek_jednim_tahem(s)
        penup()

        cumulative_angle += sign * theta


# choose random number of houses and draw
n = randint(8, 15)
# keep side sizes between 20 and 60 for visual balance
rada_domecku(n, min_side=25, max_side=55)
exitonclick()