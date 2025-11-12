LSDelta - Least Significant Digit Delta
=======================================

`lsdelta` is a simple little library that provides a single function:

**`lsdelta(a :str|bytes, b :str|bytes) -> int`**

This function takes two decimal numbers stored as strings,
pads them both to the same length after the decimal point,
and then removes the decimal point and subtracts them,
giving you the difference in their least significant digits.

    >>> from lsdelta import lsdelta
    >>> lsdelta("399.999","400")
    -1
    >>> lsdelta("1035.349", "1035.35")
    -1
    >>> lsdelta("1035.110", "1035.1")
    10

This exists because it's part of a check I sometimes need to do
on large datasets, which is why it's implemented in C for speed.


Author, Copyright, and License
------------------------------

Copyright (c) 2024 Hauke Daempfling (haukex@zero-g.net)
at the Leibniz Institute of Freshwater Ecology and Inland Fisheries (IGB),
Berlin, Germany, https://www.igb-berlin.de/

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see https://www.gnu.org/licenses/
