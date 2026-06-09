#mode light

print("=== Variables and Arithmetic ===")
x = 10
y = 3
print("x + y =", x + y)
print("x - y =", x - y)
print("x * y =", x * y)
print("x / y =", x / y)
print("x % y =", x % y)

print("=== Comparisons ===")
print("10 == 10:", 10 == 10)
print("10 != 5:", 10 != 5)
print("3 < 5:", 3 < 5)
print("5 <= 5:", 5 <= 5)
print("10 > 3:", 10 > 3)

print("=== Boolean Logic ===")
print("true and true:", true and true)
print("true and false:", true and false)
print("false or true:", false or true)
print("not true:", not true)
print("not false:", not false)

print("=== If/Else ===")
n = 7
if n > 5:
    print(n, "is greater than 5")
else:
    print(n, "is less or equal to 5")

print("=== While Loop ===")
i = 0
while i < 5:
    print("i =", i)
    i = i + 1

print("=== For Loop ===")
total = 0
for val in [10, 20, 30]:
    total = total + val
    print("adding", val)
print("total =", total)

print("=== Lists ===")
items = [1, 2, 3, 4, 5]
print("items:", items)
print("len(items):", len(items))
items = push(items, 6)
print("after push:", items)
last = pop(items)
print("popped:", last)
print("remaining:", items)

print("=== Functions ===")
fn double(x):
    return x * 2

print("double(21) =", double(21))

fn factorial(x):
    result = 1
    i = 1
    while i <= x:
        result = result * i
        i = i + 1
    return result

print("factorial(5) =", factorial(5))

print("=== Type Functions ===")
print("type_of(42):", type_of(42))
print("type_of(\"hi\"):", type_of("hi"))
print("type_of(true):", type_of(true))
print("bool(0):", bool(0))
print("bool(1):", bool(1))
print("bool(\"\"):", bool(""))
print("int(3.14):", int(3.14))
print("num(\"42\"):", num("42"))

print("=== ALL TESTS PASSED ===")
