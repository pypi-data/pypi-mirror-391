def prime_check(x):
    is_prime = True
    for i in range(2, int(x ** 0.5) + 1):
        if x % i == 0:
            is_prime = False
            continue
    return is_prime

def fibonacci_term(x):
    fibonacci = list()
    fibonacci.append(1)
    fibonacci.append(2)
    
    for i in range(2, x-1):
        fibonacci.append(fibonacci[i-1]+fibonacci[i-2])
    return fibonacci[i]

def hypotenus(x,y):
    sum = x**2 + y**2
    hipotenüs = sum ** 0.5
    return hipotenüs

def sum_of_numbers(x,y):
    if x >= y:
        print("First term should be lower than second term")
    else:
        n = (y - x) + 1
        sum = (n * (n + 1)) / 2
    return sum

def gcd(x,y):
    largest_factor = 0
    if x > y:
        print("First term should be lower or equal to second term")
    else:
        for i in range(1, y):
            if x % i == 0 and y % i == 0:
                largest_factor = int(i)
        return largest_factor

def lcm(x,y):
    if x > y:
        print("First term should be lower or equal to second term")
    else:
        least_common_multiple = (x * y) // gcd(x,y)
        return least_common_multiple

