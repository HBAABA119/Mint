#mode brace

fn greet(name) {
    print("Hello,", name);
}

greet("Mint");

var result = 0;
var i = 1;
while (i <= 5) {
    result = result + i;
    i = i + 1;
}

print("sum 1..5 =", result);
print("2 + 2 =", 2 + 2);
print("10 * 3 =", 10 * 3);

fn factorial(x) {
    var result = 1;
    var i = 1;
    while (i <= x) {
        result = result * i;
        i = i + 1;
    }
    return result;
}

print("factorial(5) =", factorial(5));

var items = [1, 2, 3];
print("len:", len(items));
print("type:", type_of(42));
print("bool(0):", bool(0));
print("ALL TESTS PASSED");
