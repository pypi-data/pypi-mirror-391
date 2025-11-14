from __future__ import annotations
from math import gcd
from typing import Literal

__all__ = ["Fraction"]


def _check_zero(value: RationalLike) -> bool:
    if isinstance(value, (int, float)) and value == 0:
        return True
    if isinstance(value, Fraction) and value.numerator == 0:
        return True

    return False


def _check_denominator(value: RationalLike) -> None:
    if _check_zero(value):
        raise ZeroDivisionError("Denominator cannot be zero.")


def _float_to_fraction(value: float) -> tuple[int, int]:
    st = str(value)
    n_zeros = len(st.split(".")[-1])
    num = int(st.replace(".", ""))
    den = 10**n_zeros
    return num, den


def _process_rational_like(value: RationalLike) -> tuple[int, int]:
    if isinstance(value, Fraction):
        return value.numerator, value.denominator
    if isinstance(value, int):
        return value, 1
    if isinstance(value, float):
        return _float_to_fraction(value)

    raise TypeError(f"Unsupported type: {type(value)}")


def _reduce_fraction(numerator: int, denominator: int) -> tuple[int, int]:
    common_divisor = gcd(numerator, denominator)
    sign_num = numerator / abs(numerator)
    sign_den = denominator / abs(denominator)
    sign = int(sign_num * sign_den)
    num = sign * abs(numerator) // common_divisor
    den = abs(denominator) // common_divisor
    return num, den


class Fraction:
    def __init__(self, numerator: RationalLike, denominator: RationalLike = 1) -> None:
        self._numerator: int
        self._denominator: int
        _check_denominator(denominator)
        if _check_zero(numerator):
            self._numerator = 0
            self._denominator = 1
        else:
            num_a, num_b = _process_rational_like(numerator)
            den_a, den_b = _process_rational_like(denominator)
            self._numerator, self._denominator = _reduce_fraction(num_a * den_b, num_b * den_a)

    @property
    def numerator(self) -> int:
        return self._numerator

    @property
    def denominator(self) -> int:
        return self._denominator

    @property
    def inverse(self) -> Fraction:
        return Fraction(self.denominator, self.numerator)

    @property
    def sign(self) -> Literal[0, 1, -1]:
        if self.numerator == 0:
            return 0
        
        if self.numerator > 0:
            return 1
        
        return -1

    def __add__(self, other: RationalLike) -> Fraction:
        other_frac = Fraction(other)
        new_numerator = self.numerator * other_frac.denominator + other_frac.numerator * self.denominator
        new_denominator = self.denominator * other_frac.denominator
        return Fraction(new_numerator, new_denominator)

    def __radd__(self, other: RationalLike) -> Fraction:
        return self + other

    def __neg__(self) -> Fraction:
        return Fraction(-self.numerator, self.denominator)

    def __sub__(self, other: RationalLike) -> Fraction:
        return self + Fraction(-other)

    def __rsub__(self, other: RationalLike) -> Fraction:
        return self - other

    def __mul__(self, other: RationalLike) -> Fraction:
        other_frac = Fraction(other)
        new_numerator = self.numerator * other_frac.numerator
        new_denominator = self.denominator * other_frac.denominator
        return Fraction(new_numerator, new_denominator)

    def __rmul__(self, other: RationalLike) -> Fraction:
        return self * other

    def __truediv__(self, other: RationalLike) -> Fraction:
        other_frac = Fraction(other)
        return self * other_frac.inverse

    def __rtruediv__(self, other: RationalLike) -> Fraction:
        return self.inverse * other

    def __eq__(self, other) -> bool:
        if not isinstance(other, RationalLike):
            return False

        other_frac = Fraction(other)
        return (self.numerator == other_frac.numerator) and (self.denominator == other_frac.denominator)

    def __repr__(self) -> str:
        return f"{self.numerator}/{self.denominator}"


RationalLike = int | float | Fraction
