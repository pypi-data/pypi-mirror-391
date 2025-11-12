import itertools
import math
import random
from fractions import Fraction
from typing import *
from scipy.optimize import fsolve
import numpy as np
from multipledispatch import dispatch

from .tools import clean_list, clean_list_2d

PI = 2 * np.arccos(0)
Degrees = PI / 180
Radians = 180 / PI

rad2deg = lambda x: x * Radians
deg2rad = lambda x: x * Degrees


def clamp(num: float, low: float, high: float) -> float:
    if num < low:
        return low
    if num > high:
        return high
    return num


def clamp01(num: float) -> float:
    if num < 0:
        return 0
    if num > 1:
        return 1
    return num


def sign(num: float) -> int:
    return int(num / abs(num))


def factorial(num: int) -> int:
    prod = 1
    for i in range(1, num + 1):
        prod *= i
    return prod


def map_range(value: int | float,
              min1: float,
              max1: float,
              min2: float,
              max2: float) -> float:
    return (value - min1) / (max1 - min1) * (max2 - min2) + min2


def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def get_factors(num: int):
    factors = []
    for i in range(1, num + 1):
        if num % i == 0:
            factors.append(i)

    return factors


def dec_to_fraction(dec: float):
    return Fraction(dec).limit_denominator()


def get_digits(num: int):
    return [int(i) for i in list(str(num))]


class Vector:
    def __init__(self, *v: int | float):
        self.vec = np.array(v)
        self.n = len(self.vec)

    def __getitem__(self, item):
        return self.vec[item]

    def __setitem__(self, key, value):
        self.vec[key] = value

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    @property
    def w(self):
        return self[3]

    @property
    def xy(self):
        return self.x, self.y

    @property
    def xyz(self):
        return self.x, self.y, self.z

    @property
    def xyzw(self):
        return self.x, self.y, self.z, self.w

    @x.setter
    def x(self, val):
        self[0] = val

    @y.setter
    def y(self, val):
        self[1] = val

    @z.setter
    def z(self, val):
        self[2] = val

    @w.setter
    def w(self, val):
        self[3] = val

    @xy.setter
    def xy(self, v1, v2):
        self[0] = v1
        self[1] = v2

    @xyz.setter
    def xyz(self, v1, v2, v3):
        self[0] = v1
        self[1] = v2
        self[2] = v3

    @xyzw.setter
    def xyzw(self, v1, v2, v3, v4):
        self[0] = v1
        self[1] = v2
        self[2] = v3
        self[3] = v4

    def __repr__(self) -> str:
        return f"(" + ", ".join([str(i) for i in self.vec]) + ")"

    def __add__(self, other: Self) -> Self:
        return Vector(*(self.vec + other.vec))

    def __sub__(self, other: Self) -> Self:
        return Vector(*(self.vec - other.vec))

    def __mul__(self, other: float | int) -> Self:
        return Vector(*(self.vec * other))

    def __rmul__(self, other: float | int) -> Self:
        return Vector(*(self.vec * other))

    def __truediv__(self, other: float | int):
        return Vector(*(self.vec / other))

    def __rtruediv__(self, other):
        return Vector(*(other / self.vec))

    def __round__(self, n=None):
        return Vector(*[round(i) for i in self.vec])

    def __abs__(self):
        return Vector(*[abs(i) for i in self.vec])

    def __int__(self):
        return Vector(*[int(i) for i in self.vec])

    def __float__(self):
        return Vector(*[float(i) for i in self.vec])

    @property
    def magnitude(self):
        return math.sqrt(sum(self.vec ** 2))

    def __len__(self):
        return self.magnitude

    def normalize(self) -> Self:
        if self.magnitude == 0:
            return Vector.zero()
        return self / self.magnitude

    def to_mat(self):
        mat = Matrix(self.n, 1)
        mat.set([[i] for i in self.vec])
        return mat

    def heading(self):
        return np.atan2(self.vec[1], self.vec[2])

    def set_mag(self, new_mag: float):
        return self.normalize() * new_mag

    @dispatch(float)
    def limit_mag(self, mag: float):
        if self.magnitude > mag:
            self.set_mag(mag)

    @dispatch(float, float)
    def limit_mag(self, min_mag: float, max_mag: float):
        self.set_mag(clamp(self, min_mag, max_mag, lambda v: v.magnitude))

    @classmethod
    def fill(cls, v: int, n: int = 2):
        return Vector(*[v] * n)

    @classmethod
    def zero(cls, n: int = 2):
        return cls.fill(0, n)

    @classmethod
    def one(cls, n: int = 2):
        return cls.fill(1, n)

    @classmethod
    def dot(cls, a: Self, b: Self):
        return np.dot(a.vec, b.vec)

    @classmethod
    def cross(cls, a: Self, b: Self):
        return np.cross(a.vec, b.vec)

    @classmethod
    def angle_between(cls, a: Self, b: Self):
        mag = a.magnitude * b.magnitude
        if mag > 0:
            ratio = cls.dot(a, b) / mag
            return math.acos(ratio)
        else:
            return 0

    @classmethod
    def distance(cls, a: Self, b: Self):
        return (b - a).magnitude

    @classmethod
    def lerp(cls, a: Self, b: Self, t: float):
        if a.n != b.n:
            raise ValueError(f"Dimensions of both vectors must match. Got {a.n} and {b.n}")
        v = b - a
        pd = []
        for i in range(a.n):
            pdi = a[i] + v[i] * t
            pd.append(pdi)
        return Vector(*pd)


def closest_from_array_number(arr: Sequence[float], num: float | int):
    def difference(a):
        return abs(a - num)

    return min(arr, key=difference)


def closest_from_array_vec(arr: Sequence[Vector], num: Vector):
    def difference(a: Vector):
        return abs(a - num).magnitude

    return min(arr, key=difference)


def array_to_vec_array(arr: Sequence[Sequence[int]]):
    result = []
    for i in arr:
        if isinstance(i, (list, tuple)):
            raise Exception("element must be sequence")
        else:
            result.append(Vector(*i))
    return result


def vec_array_to_array(arr: Sequence[Vector]):
    return [[*a] for a in arr]


def angle_to_direction2(angle: float):
    x = math.cos(angle)
    y = math.sin(angle)
    return Vector(x, y)


def angle_to_direction3(theta: float, phi: float):
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    return Vector(x, y, z)


def lerp(a, b, t: float):
    return (1 - t) * a + t * b


class Matrix:

    @dispatch(int, int, fill=float)
    def __init__(self, r: int, c: int, *, fill: int | float = 0) -> None:
        self.rows = r
        self.cols = c
        self.matrix = np.full([r, c], fill)

    @dispatch(list)
    def __init__(self, mat: np.ndarray | list[list[int | float]]) -> None:

        self.matrix = np.array(mat)
        self.rows = len(mat)
        self.cols = len(mat[0])

    def set(self, mat: np.ndarray | list[list[int | float]]) -> np.ndarray | ValueError:
        matRows = len(mat)
        matCols = len(mat[0])
        if matRows == self.rows and matCols == self.cols:
            self.matrix = mat
        else:
            raise ValueError(f"Expected matrix of dimensions ({self.rows}, {self.cols}) but got ({matRows}, {matCols})")

    def __repr__(self):
        txt = [""]  # ┌┘└┐
        if self.rows >= 20:
            for i in range(3):
                if self.cols >= 20:
                    row = []
                    for j in range(3):
                        row.append(float(self.matrix[i][j]))
                    row.append(f"... {self.cols - 6}")
                    for j in range(self.cols - 3, self.cols):
                        row.append(float(self.matrix[i][j]))
                    row = f"|{row}|\n"
                    row = row.replace("[", "").replace("]", "").replace(",", "")
                    txt.append(row)
                else:
                    row = f"|{[float(self.matrix[i][j]) for j in range(self.cols)]}|\n"
                    row = row.replace("[", "").replace("]", "").replace(",", "")
                    txt.append(row)
            txt.append(f"...{self.rows - 6}\n")
            for i in range(self.rows - 3, self.rows):
                if self.cols >= 20:
                    row = []
                    for j in range(3):
                        row.append(float(self.matrix[i][j]))
                    row.append(f"... {self.cols - 6}")
                    for j in range(self.cols - 3, self.cols):
                        row.append(float(self.matrix[i][j]))
                    row = f"|{row}|\n"
                    row = row.replace("[", "").replace("]", "").replace(",", "")
                    txt.append(row)
                else:
                    row = f"|{[float(self.matrix[i][j]) for j in range(self.cols)]}|\n"
                    row = row.replace("[", "").replace("]", "").replace(",", "")
                    txt.append(row)
        else:
            for i in range(self.rows):
                if self.cols >= 20:
                    row = []
                    for j in range(3):
                        row.append(float(self.matrix[i][j]))
                    row.append(f"... {self.cols - 6}")
                    for j in range(self.cols - 3, self.cols):
                        row.append(float(self.matrix[i][j]))
                    row = f"|{row}|\n"
                    row = row.replace("[", "").replace("]", "").replace(",", "")
                    txt.append(row)
                else:
                    row = f"|{[float(self.matrix[i][j]) for j in range(self.cols)]}|\n"
                    row = row.replace("[", "").replace("]", "").replace(",", "")
                    txt.append(row)
        return "".join(txt)

    def row(self, n):
        return self.matrix[n]

    def col(self, n):
        return [float(self.matrix[i][n]) for i in range(self.rows)]

    def set_row(self, n, row):
        if len(row) != self.cols:
            raise ValueError(f"Number of columns do not match. current: {len(row)}, required: {self.cols}")
        self.matrix[n] = row

    def set_col(self, n, col):
        if len(col) != self.rows:
            raise ValueError(f"Number of rows do not match. current: {len(col)}, required: {self.rows}")
        for i in range(self.rows):
            self.matrix[i][n] = col[i]

    def not_row(self, n):
        mat = Matrix(self.rows - 1, self.cols)
        matrix = [[self[i][j] for j in range(self.cols)] if i != n else [] for i in range(self.rows)]
        matrix = clean_list(matrix)
        mat.set(clean_list_2d(matrix))
        return mat

    def not_col(self, n):
        mat = Matrix(self.rows, self.cols - 1)
        matrix = [[self[i][j] if j != n else None for j in range(self.cols)] for i in range(self.rows)]
        matrix = clean_list(matrix)
        mat.set(clean_list_2d(matrix))
        return mat

    def not_row_col(self, a, b):
        mat = Matrix(self.rows - 1, self.cols - 1)
        matrix = [[self[i][j] if j != b else None for j in range(self.cols)] if i != a else [] for i in
                  range(self.rows)]
        matrix = clean_list(matrix)
        mat.set(clean_list_2d(matrix))
        return mat

    def __getitem__(self, item: tuple[int, int] | int):
        if type(item) == int:
            return self.matrix[item]
        elif type(item) == tuple:
            return self.matrix[item[0]][item[1]]

    def __setitem__(self, key: tuple[int | np.ndarray[Any], int | np.ndarray[Any]],
                    value: int | float | np.ndarray[Any]):
        self.matrix[key[0]][key[1]] = value

    def __invert__(self):
        new_mat = Matrix(self.cols, self.rows)
        for i in range(self.rows):
            for j in range(self.cols):
                new_mat[j][i] = self.matrix[i][j]
        return new_mat

    def transpose(self):
        new_mat = Matrix(self.cols, self.rows)
        for i in range(self.rows):
            for j in range(self.cols):
                new_mat[j][i] = self.matrix[i][j]
        return new_mat

    def determinant(self):
        if self.cols != self.rows:
            raise ValueError(f"Needs to be square matrix. current - rows: {self.rows} cols: {self.cols}")
        det = np.linalg.det(self.matrix)
        return det

    def __matmul__(self, other: Self):
        if self.cols != other.rows:
            raise TypeError(
                "Number of columns of the first matrix must be equal to number of rows of the second matrix")
        mat = Matrix(self.rows, other.cols)
        mat.matrix = np.dot(self.matrix, other.matrix)
        return mat

    def __add__(self, other):
        mat = Matrix(self.rows, self.cols)
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Sizes dont match")
        for i in range(self.rows):
            for j in range(self.cols):
                mat[i][j] = self.matrix[i][j] + other.matrix[i][j]

        return mat

    def __sub__(self, other):
        mat = Matrix(self.rows, self.cols)
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Sizes dont match")
        for i in range(self.rows):
            for j in range(self.cols):
                mat[i][j] = self.matrix[i][j] - other.matrix[i][j]

        return mat

    def __mul__(self, other):
        mat = Matrix(self.rows, self.cols)
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Sizes dont match")
        for i in range(self.rows):
            for j in range(self.cols):
                mat[i][j] = self.matrix[i][j] * other.matrix[i][j]

        return mat

    def toVec(self):
        return Vector(*[float(self[i, 0]) for i in range(self.rows)])

    # Class Methods
    @classmethod
    def identity(cls, r, c):
        mat = Matrix(r, c)
        for i in range(r):
            for j in range(c):
                if i == j: mat.matrix[i][j] = 1
        return mat

    @classmethod
    def random(cls, r, c, mn: int | float, mx: int | float, t=Literal["int", "float"]):
        rand = RandomInt(mn, mx) if t == "int" else RandomFloat(mn, mx)
        mat = Matrix(r, c)
        for i in range(r):
            for j in range(c):
                mat.matrix[i][j] = rand.get()
        return mat


class ArithmeticSeries:
    def __init__(self, start: float | int, d: float | int):
        self.start = start
        self.d = d

    def __repr__(self) -> str:
        return f"[{self.nth(1)}, {self.nth(2)}, {self.nth(3)}, ... ] d={self.d}"

    @classmethod
    def from_seq(cls, arr) -> Self:
        d = arr[1] - arr[0]
        for i in range(1, len(arr)):
            if arr[i] - arr[i - 1] != d:
                raise ValueError("common difference is not same")

        return ArithmeticSeries(arr[0], d)

    def nth(self, i: int) -> float | int:
        return self.start + self.d * (i - 1)

    def first_n_terms(self, n: int) -> list[float | int]:
        terms = []
        for i in range(1, n + 1):
            terms.append(self.nth(i))
        return terms

    def from_to(self, a: int, b: int) -> list[float | int]:
        terms = []
        for i in range(a, b + 1):
            terms.append(self.nth(i))
        return terms

    def S_n(self, n: int):
        a = (self.start + self.nth(n))
        return (n * a) / 2


def linear_solve(coeff: np.ndarray | Matrix, constant: np.ndarray | Matrix):
    coeff_mat = coeff.matrix if isinstance(coeff, Matrix) else coeff
    const_mat = constant.matrix if isinstance(constant, Matrix) else constant

    return np.linalg.solve(coeff_mat, const_mat)


def quadratic_roots(a: int | float, b: int | float, c: int | float):
    D = b ** 2 - 4 * a * c
    alpha = (-b + math.sqrt(D)) / 2 * a
    beta = (-b - math.sqrt(D)) / 2 * a

    return alpha, beta


# === Geometry ===

class Line:
    def __init__(self, a: Vector, b: Vector):
        if a.n == b.n:
            self.a = a
            self.b = b
        else:
            raise ValueError("Invalid Points. a and b should have the same length")

    def __repr__(self):
        return f"{self.a}->{self.b}"

    @property
    def length(self):
        return (self.b - self.a).length

    @property
    def midpoint(self):
        return (self.a + self.b) / 2

    @property
    def slope(self):
        return (self.b.y - self.a.y) / max(1e-5,
                                           (self.b.x - self.a.x) if self.b.x > self.a.x else (self.a.x - self.b.x))

    @property
    def y_intercept(self):
        return self.a.y - (self.slope * self.a.x)

    @property
    def x_intercept(self):
        return -(self.y_intercept / self.slope)

    @property
    def line_function(self, string: bool = True):
        if string:
            if self.y_intercept == 0:
                return f"y = {self.slope}x"
            return f"y = {self.slope}x {"+" if self.y_intercept >= 0 else "-"} {abs(self.y_intercept)}"
        else:
            return lambda x: self.slope * x + self.y_intercept

    def intersect(self, other: Self):
        d = (self.b.x - self.a.x) * (other.b.y - other.a.y) + (self.b.y - self.a.y) * (other.a.x - other.b.x)
        if d == 0:
            return None
        t = ((other.a.x - self.a.x) * (other.b.y - other.a.y) + (other.a.y - self.a.y) * (other.a.x - other.b.x)) / d
        u = ((other.a.x - self.a.x) * (self.b.y - self.a.y) + (other.a.y - self.a.y) * (self.a.x - self.b.x)) / d
        if 0 <= t <= 1 and 0 <= u <= 1:
            return Vector(self.b.x * t + self.a.x * (1 - t), self.b.y * t + self.a.y * (1 - t))
        return None


# === Random ===

class RandomInt:
    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def get(self):
        return random.randint(self.start, self.stop)


class RandomFloat:
    def __init__(self, start: int, stop: int):
        self.start = start
        self.stop = stop

    def get(self):
        return random.uniform(self.start, self.stop)


class RandomVec2Int:
    def __init__(self, x_range: tuple[int, int], y_range: tuple[int, int] = None):
        self.x_range = x_range
        if y_range is None:
            self.y_range = x_range
        else:
            self.y_range = y_range

    def get(self):
        x = random.randint(self.x_range[0], self.x_range[1])
        y = random.randint(self.y_range[0], self.y_range[1])
        return Vector(x, y)


class RandomVec3Int:
    def __init__(self, x_range: tuple[int, int], y_range: tuple[int, int], z_range: tuple[int, int]):
        self.x_range = x_range
        self.y_range = y_range
        self.z_range = z_range

    def get(self):
        x = random.randint(self.x_range[0], self.x_range[1])
        y = random.randint(self.y_range[0], self.y_range[1])
        z = random.randint(self.z_range[0], self.z_range[1])
        return Vector(x, y, z)


class RandomVec2Float:
    def __init__(self, x_range: tuple[int | float, int | float], y_range: tuple[int | float, int | float] = None):
        self.x_range = x_range
        if y_range is None:
            self.y_range = x_range
        else:
            self.y_range = y_range

    def get(self):
        x = random.uniform(self.x_range[0], self.x_range[1])
        y = random.uniform(self.y_range[0], self.y_range[1])
        return Vector(x, y)


class RandomVec3Float:
    def __init__(self, x_range: tuple[int, int], y_range: tuple[int, int] = None, z_range: tuple[int, int] = None):
        self.x_range = x_range
        if y_range is None and z_range is None:
            self.y_range = x_range
            self.z_range = x_range
        else:
            self.y_range = y_range
            self.z_range = z_range

    def get(self):
        x = random.uniform(self.x_range[0], self.x_range[1])
        y = random.uniform(self.y_range[0], self.y_range[1])
        z = random.uniform(self.z_range[0], self.z_range[1])
        return Vector(x, y, z)


class RandomDir2:
    def __init__(self):
        self.theta = RandomFloat(0, 360)

    def get(self):
        return angle_to_direction2(self.theta.get() * Degrees)


class RandomDir3:
    def __init__(self):
        self.theta = RandomFloat(0, 180)
        self.phi = RandomFloat(0, 360)

    def get(self):
        return angle_to_direction3(self.theta.get() * Degrees, self.phi.get() * Degrees)


class RandomDir2BetweenAngles:
    def __init__(self, a1: int | float, a2: int | float):
        self.start = a1
        self.stop = a2

    def get(self):
        angle = random.uniform(self.start, self.stop)
        x = math.cos(angle)
        y = math.sin(angle)
        return Vector(x, y)
