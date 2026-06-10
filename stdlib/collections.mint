#mode light

fn map(list, func):
    result = []
    for item in list:
        result = push(result, func(item))
    return result

fn filter(list, predicate):
    result = []
    for item in list:
        if predicate(item):
            result = push(result, item)
    return result

fn reduce(list, func, initial):
    result = initial
    for item in list:
        result = func(result, item)
    return result

fn find(list, predicate):
    for item in list:
        if predicate(item):
            return item
    return null

fn any(list, predicate):
    for item in list:
        if predicate(item):
            return true
    return false

fn all(list, predicate):
    for item in list:
        if not predicate(item):
            return false
    return true

fn sum(list):
    result = 0
    for item in list:
        result = result + item
    return result

fn reverse(list):
    result = []
    i = len(list) - 1
    while i >= 0:
        result = push(result, list[i])
        i = i - 1
    return result
