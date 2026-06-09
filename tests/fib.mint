#mode light

fn fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print("fib(10) =", fib(10))

fn factorial(x):
    result = 1
    i = 1
    while i <= x:
        result = result * i
        i = i + 1
    return result

print("factorial(5) =", factorial(5))

total = 0
for i in [1, 2, 3, 4, 5]:
    total = total + i

print("sum 1..5 =", total)
print("len of [1,2,3]:", len([1, 2, 3]))
print("type of 42:", type_of(42))
print("bool of 0:", bool(0))
print("bool of 1:", bool(1))
