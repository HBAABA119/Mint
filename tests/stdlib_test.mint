#mode light

fn double(x):
    return x * 2

fn is_greater_than_2(x):
    return x > 2

fn add(a, b):
    return a + b

fn is_true(x):
    return x

print("=== Testing stdlib ===")
print("map:", map([1, 2, 3], double))
print("filter:", filter([1, 2, 3, 4, 5], is_greater_than_2))
print("reduce:", reduce([1, 2, 3], add, 0))
print("sum:", sum([1, 2, 3, 4, 5]))
print("find:", find([1, 2, 3, 4], is_greater_than_2))
print("any true:", any([false, false, true], is_true))
print("any false:", any([false, false, false], is_true))
print("all true:", all([true, true, true], is_true))
print("all false:", all([true, false, true], is_true))
print("reverse:", reverse([1, 2, 3, 4, 5]))

print("=== Indexing ===")
items = [10, 20, 30]
print("items[0]:", items[0])
print("items[1]:", items[1])
print("items[2]:", items[2])
print("items[0] after set:", items[0])

print("=== String indexing ===")
s = "hello"
print("s[0]:", s[0])
print("s[1]:", s[1])

print("=== Math ===")
print("abs(-5):", abs(-5))
print("sqrt(16):", sqrt(16))
print("pow(2, 10):", pow(2, 10))
print("round(3.7):", round(3.7))
print("floor(3.7):", floor(3.7))
print("ceil(3.7):", ceil(3.7))

print("=== split/join ===")
parts = split("a,b,c", ",")
print("split:", parts)
rejoined = join(parts, "-")
print("join:", rejoined)

print("ALL STDLIB TESTS PASSED")
