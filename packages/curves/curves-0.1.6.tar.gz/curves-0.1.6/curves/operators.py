# -*- coding: utf-8 -*-

# curves
# ------
# functional curve algebra (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.4, copyright Friday, 11 October 2024
# Website:  https://github.com/sonntagsgesicht/curves
# License:  Apache License 2.0 (see LICENSE file)


from .numerics import finite_difference, quadrature, EPS


class Integral:

    def __init__(self, curve, a=0):
        r"""integral of function

        :param curve: (callable) function $f$ to integrate
        :param a: (float) lower bound $a$ of integral

        calculates the integral

        $$F_a(x) = \int_a^x f(s) ds$$

        """
        self.curve = curve
        self.a = a

    def __call__(self, x):
        return quadrature(self.curve, self.a, x)

    def __getitem__(self, item):
        return self.__class__(self.curve, item)

    def __repr__(self):
        _ = f", {self.a}" if self.a else ''
        return f"{self.__class__.__name__}({self.curve}{_})"


class Derivative:

    def __init__(self, curve, h=EPS):
        r"""frist derivative of a function

        :param curve: (callable) function $f$ to differentiate
        :param h: (float) step size $\eta$ for finte differences (optional)

        calculates the (first) derivative via finite differences

        $$\frac{\partial f}{\partial x}
        =f'(x)\approx\frac{f(x+\eta)-f(x)}{\eta}$$

        """
        self.curve = curve
        self.h = h

    def __call__(self, x):
        return finite_difference(self.curve, x, self.h)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.curve})"
