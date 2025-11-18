from ._classes import *
# raymath

lib.Clamp.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float]
lib.Clamp.restype = ctypes.c_float
def clamp(value,min,max):
    return lib.Clamp(value, min, max)

vector2_zero = Vector2(0, 0)
vector2_one = Vector2(1, 1)


'''
// Add two vectors (v1 + v2)
RMAPI Vector2 Vector2Add(Vector2 v1, Vector2 v2)
{
    Vector2 result = { v1.x + v2.x, v1.y + v2.y };

    return result;
}

// Add vector and float value
RMAPI Vector2 Vector2AddValue(Vector2 v, float add)
{
    Vector2 result = { v.x + add, v.y + add };

    return result;
}

// Subtract two vectors (v1 - v2)
RMAPI Vector2 Vector2Subtract(Vector2 v1, Vector2 v2)
{
    Vector2 result = { v1.x - v2.x, v1.y - v2.y };

    return result;
}

// Subtract vector by float value
RMAPI Vector2 Vector2SubtractValue(Vector2 v, float sub)
{
    Vector2 result = { v.x - sub, v.y - sub };

    return result;
}

// Calculate vector length
RMAPI float Vector2Length(Vector2 v)
{
    float result = sqrtf((v.x*v.x) + (v.y*v.y));

    return result;
}

// Calculate vector square length
RMAPI float Vector2LengthSqr(Vector2 v)
{
    float result = (v.x*v.x) + (v.y*v.y);

    return result;
}
'''

makeconnect("Vector2Add", [Vector2, Vector2], Vector2)
def vector2_add(v1: Vector2, v2: Vector2):
    return lib.Vector2Add(v1, v2)

makeconnect("Vector2AddValue", [Vector2, c_float], Vector2)
def vector2_add_value(v: Vector2, add: float):
    return lib.Vector2AddValue(v, add)

makeconnect("Vector2Subtract", [Vector2, Vector2], Vector2)
def vector2_subtract(v1: Vector2, v2: Vector2):
    return lib.Vector2Subtract(v1, v2)

makeconnect("Vector2SubtractValue", [Vector2, c_float], Vector2)
def vector2_subtract_value(v: Vector2, sub: float):
    return lib.Vector2SubtractValue(v, sub)

makeconnect("Vector2Length", [Vector2], c_float)
def vector2_length(v: Vector2):
    return lib.Vector2Length(v)

makeconnect("Vector2LengthSqr", [Vector2], c_float)
def vector2_length_sqr(v: Vector2):
    return lib.Vector2LengthSqr(v)

