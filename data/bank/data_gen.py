from random import random, randint


def gen_data(n, w_prob, d_prob, int_pro):
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
    int_pro: Probability of interest

  Returns:

  """
  balance = 0
  file = open(f'bank_{n}.csv', 'w')
  for i in range(n):
    if random() < w_prob:
      amount = randint(1, 50)
      if amount < balance:
        amount = randint(1, balance)
      file.write(f'w {amount}\n')
      balance -= amount
    elif random() < d_prob:
      amount = randint(1, 50)
      file.write(f'd {amount}\n')
      balance += amount

    elif random() < int_pro:
      file.write(f'i\n')
      balance += balance*0.05

  file.close()