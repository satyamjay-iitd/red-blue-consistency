from random import randint, random


def gen_set_data(n, add_p, filepath=None):
    """

    :param n: Number of operations
    :param add_p: probability of adding to set
    :param filepath:
    :return:
    """
    assert add_p <= 1.0
    filepath = f'../data/bank/bank_{n // 1000}_{int(add_p * 100)}.dat' if filepath is None else filepath
    file = open(filepath, 'w')
    for i in range(n):
        if random() < add_p:
            element = randint(1, 1000)
            file.write(f'A {element}\n')
        else:
            element = randint(1, 1000)
            file.write(f'R {element}\n')

    file.close()