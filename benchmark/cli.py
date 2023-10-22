import os.path
from enum import Enum
from typing import Annotated

import typer

from rich import print

from benchmarks import WCBenchmark, BankBenchmark
from clients.wc_client import RedisWCClient, RedBlueWCClient
from clients.bank_client import RedisBankClient, RedBlueBankClient
from utils.gen_bank_data import gen_data as gen_bank_data

app = typer.Typer()


class ClientsEnum(str, Enum):
    REDIS = "redis"
    REDBLUE = "redblue"


@app.command()
def wc(
        client: Annotated[ClientsEnum, typer.Argument(case_sensitive=False, help="Client to use")],
        txt_file: Annotated[str, typer.Argument(help="Path to text file", exists=True)] = '../data/wc/small.txt'
):
    if client == ClientsEnum.REDIS:
        _client = RedisWCClient()
    elif client == ClientsEnum.REDBLUE:
        _client = RedBlueWCClient()
    else:
        raise ValueError(f"Unknown client: {client}")

    WCBenchmark(_client, txt_file).run()


@app.command()
def bank(
        client: Annotated[ClientsEnum, typer.Argument(case_sensitive=False, help="Client to use")],
        txn_size: Annotated[int, typer.Argument(help="Number of transactions to run")] = 10000,
        w_p: Annotated[float, typer.Argument(help="Probability of withdrawal")] = 0.1,
        d_p: Annotated[float, typer.Argument(help="Probability of deposit")] = 0.8,
        int_rate: Annotated[int, typer.Argument(help="Interest rate X 1000", min=0, max=1000)] = 10,
):
    data_file = f'../data/bank/bank_{txn_size//1000}_{int(w_p * 10)}_{int(d_p * 10)}.dat'
    if not os.path.exists(data_file):
        print("Generating data file")
        gen_bank_data(txn_size, w_p, d_p, int_rate/1000)
        print("Data file generated")

    assert os.path.exists(data_file)

    if client == ClientsEnum.REDIS:
        _client = RedisBankClient(interest=int_rate)
    elif client == ClientsEnum.REDBLUE:
        _client = RedBlueBankClient(interest=int_rate)
    else:
        raise ValueError(f"Unknown client: {client}")

    BankBenchmark(_client, data_file).run()


if __name__ == "__main__":
    app()
