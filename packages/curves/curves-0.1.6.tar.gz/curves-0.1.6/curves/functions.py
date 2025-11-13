# -*- coding: utf-8 -*-

# curves
# ------
# functional curve algebra (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.4, copyright Friday, 11 October 2024
# Website:  https://github.com/sonntagsgesicht/curves
# License:  Apache License 2.0 (see LICENSE file)


import math

from .curves import Curve


def ramp(x): return max(0, x)


def step(x): return 1 if 0 <= x else 0


ramp = Curve(ramp)
step = Curve(step)

e = Curve(math.e)
inf = Curve(math.inf)
nan = Curve(math.nan)
pi = Curve(math.pi)

acos = Curve(math.acos)
asin = Curve(math.asin)
asinh = Curve(math.asinh)
atan = Curve(math.atan)
atanh = Curve(math.atanh)
ceil = Curve(math.ceil)
cos = Curve(math.cos)
cosh = Curve(math.cosh)
degrees = Curve(math.degrees)
erf = Curve(math.erf)
erfc = Curve(math.erfc)
exp = Curve(math.exp)
expm1 = Curve(math.expm1)
fabs = Curve(math.fabs)
floor = Curve(math.floor)
frexp = Curve(math.frexp)
gamma = Curve(math.gamma)
hypot = Curve(math.hypot)
lgamma = Curve(math.lgamma)
log = Curve(math.log)
log10 = Curve(math.log10)
log1p = Curve(math.log1p)
log2 = Curve(math.log2)
modf = Curve(math.modf)
radians = Curve(math.radians)
sin = Curve(math.sin)
sinh = Curve(math.sinh)
sqrt = Curve(math.sqrt)
tan = Curve(math.tan)
tanh = Curve(math.tanh)
trunc = Curve(math.trunc)
ulp = Curve(math.ulp)
