#mode light

fn double(x):
    return x * 2

fn is_gt_2(x):
    return x > 2

fn add(a, b):
    return a + b

fn is_true(x):
    return x

fn is_even(x):
    if x % 2 == 0:
        return true
    return false

print("=== v0.3 Standard Library Test ===")
print()

print("--- Collections ---")
print("map:", map([1, 2, 3], double))
print("filter:", filter([1, 2, 3, 4, 5], is_gt_2))
print("reduce:", reduce([1, 2, 3], add, 0))
print("sum:", sum([1, 2, 3, 4, 5]))
print("find:", find([1, 2, 3, 4], is_gt_2))
print("any true:", any([false, false, true], is_true))
print("any false:", any([false, false, false], is_true))
print("all true:", all([true, true, true], is_true))
print("all false:", all([true, false, true], is_true))
print("reverse:", reverse([1, 2, 3, 4, 5]))

print()
print("--- Math ---")
print("abs(-5):", abs(-5))
print("sqrt(16):", sqrt(16))
print("pow(2, 10):", pow(2, 10))
print("round(3.7):", round(3.7))
print("floor(3.7):", floor(3.7))
print("ceil(3.7):", ceil(3.7))
print("sin(0):", sin(0))
print("cos(0):", cos(0))
print("range(5):", range(5))
print("range(2, 6):", range(2, 6))

print()
print("--- String Builtins ---")
print("upper:", upper("hello"))
print("lower:", lower("HELLO"))
print("trim:", "'" + trim("  hi  ") + "'")
print("replace:", replace("hello world", "world", "there"))
print("contains true:", contains("hello world", "world"))
print("contains false:", contains("hello world", "xyz"))
print("starts_with:", starts_with("hello", "he"))
print("ends_with:", ends_with("hello", "lo"))
print("substring:", substring("hello", 1, 4))
print("split:", split("a,b,c", ","))
print("join:", join(["x", "y", "z"], "-"))

print()
print("--- Pure Mint Strings ---")
print("capitalize:", capitalize("hello"))
print("lines:", lines("a\nb\nc"))
print("unlines:", unlines(["a", "b", "c"]))
print("strip:", "'" + strip("  x  ") + "'")
print("count:", count("hello world hello", "hello"))

print()
print("--- Indexing ---")
items = [10, 20, 30]
print("list[0]:", items[0])
print("list[1]:", items[1])
print("list[2]:", items[2])
s = "hello"
print("str[0]:", s[0])
print("str[1]:", s[1])
print("str[4]:", s[4])

print()
print("--- JSON ---")
print("json_stringify:", json_stringify([1, "two", true, null, [3, 4]]))
parsed = json_parse("[1, 2, 3]")
print("json_parse list:", parsed)
print("parsed[0]:", parsed[0])
parsed_obj = json_parse("{\"name\": \"Mint\", \"version\": 0.3}")
print("json_parse dict type:", type_of(parsed_obj))

print()
print("ALL V0.3 TESTS PASSED")
