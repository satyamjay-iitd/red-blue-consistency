import math
from random import random, randint


def gen_data(n, w_prob, d_prob, int_rate=0.01):
  """
  Generate data for bank benchmark.
  Format:-
    - d 50
    - w 50
    - i
  Transaction don't lead to negative balance.

  Args:
    n: Number of total transactions
    w_prob: Probability of withdrawal
    d_prob: Probability of deposit
    int_rate: Interest rate

  Returns:

  """
  assert w_prob + d_prob <= 1.0
  int_pro = 1 - w_prob - d_prob

  balance = 0
  file = open(f'../data/bank/bank_{n//1000}_{int(w_prob*10)}_{int(d_prob*10)}.dat', 'w')
  for i in range(n):
    if random() < w_prob:
      amount = randint(1, 10)
      if amount > balance:
        amount = 0 if balance == 0 else randint(0, int(balance))
      file.write(f'w {amount}\n')
      balance -= amount
    elif random() < d_prob:
      amount = randint(1, 10)
      file.write(f'd {amount}\n')
      balance += amount

    elif random() < int_pro:
      file.write(f'i\n')
      balance += balance * int_rate

  assert balance >= 0
  file.close()


if __name__ == '__main__':
  gen_data(10000, 0.1, 0.8, 0.1)
  gen_data(10000, 0.3, 0.6, 0.1)
  gen_data(10000, 0.5, 0.4, 0.1)
  gen_data(10000, 0.7, 0.2, 0.1)

  gen_data(100000, 0.1, 0.8, 0.1)
  gen_data(100000, 0.3, 0.6, 0.1)
  gen_data(100000, 0.5, 0.4, 0.1)
  gen_data(100000, 0.7, 0.2, 0.1)

  gen_data(1000000, 0.1, 0.89, 0.01)
  gen_data(1000000, 0.3, 0.69, 0.01)
  gen_data(1000000, 0.5, 0.49, 0.01)
  gen_data(1000000, 0.7, 0.29, 0.01)
