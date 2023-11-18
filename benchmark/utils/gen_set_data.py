from random import randint, random


def gen_set_data(n, add_p, dynamic = False, filepath=None):
    """

    :param n: Number of operations
    :param add_p: probability of adding to set
    :param filepath:
    :return:
    """

    if dynamic:
        return gen_set_data2(n, add_p, filepath)

    assert add_p <= 1.0
    filepath = f'../data/set/set_{n // 1000}_{int(add_p * 100)}.dat' if filepath is None else filepath
    file = open(filepath, 'w')
    for i in range(n):
        if random() < add_p:
            element = randint(1, 1000)
            file.write(f'A {element}\n')
        else:
            element = randint(1, 1000)
            file.write(f'R {element}\n')

    file.close()


def gen_set_data2(n, add_p, filepath=None):
    assert add_p <= 1
    filepath = f'../data/set/set2_{n // 1000}_{int(add_p * 100)}.dat' if filepath is None else filepath
    file = open(filepath, 'w')
    for j in range(3):
        num_a, num_r = 0, 0
        for k in range(5):
            for i in range(n//15):
                r = random()
                if r < add_p:
                    element = randint(1, 100)
                    num_a += 1
                    file.write(f'A {element}\n')
                else:
                    element = randint(1, 100)
                    num_r += 1
                    file.write(f'R {element}\n')
            add_p = 1 - add_p

        print(num_a, num_r)


if __name__ == "__main__":
    gen_set_data2(1000000, 0.95, 'dynamic')
