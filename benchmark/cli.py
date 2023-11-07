import os.path
from enum import Enum
from typing import Annotated

import typer

from rich import print

from benchmarks import WCBenchmark, BankBenchmark, SetBenchmark
from clients.set_client import RedisSetClient, RedBlueSetClient
from clients.wc_client import RedisWCClient, RedBlueWCClient
from clients.bank_client import RedisBankClient, RedBlueBankClient
from utils.gen_bank_data import gen_data as gen_bank_data
from utils.gen_set_data import gen_set_data

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
        WCBenchmark(RedisWCClient, [{}, {}, {}], txt_file).run()
    elif client == ClientsEnum.REDBLUE:
        WCBenchmark(RedBlueWCClient, [{"port": 7379}, {"port": 7380}, {"port": 7381}], txt_file).run()
        # WCBenchmark(RedBlueWCClient, [{"port": 7379}], txt_file).run()
    else:
        raise ValueError(f"Unknown client: {client}")


@app.command()
def bank(
        client: Annotated[ClientsEnum, typer.Argument(case_sensitive=False, help="Client to use")],
        txn_size: Annotated[int, typer.Argument(help="Number of transactions to run")] = 100000,
        w_p: Annotated[float, typer.Argument(help="Probability of withdrawal")] = 0.1,
        d_p: Annotated[float, typer.Argument(help="Probability of deposit")] = 0.8,
        int_rate: Annotated[int, typer.Argument(help="Interest rate X 10000", min=0, max=10000)] = 100,
):
    data_file = f'../data/bank/bank_{txn_size // 1000}_{int(w_p * 100)}_{int(d_p * 100)}.dat'
    if not os.path.exists(data_file):
        print("Generating data file")
        gen_bank_data(txn_size, w_p, d_p, int_rate / 10000, filepath=data_file)
        print("Data file generated")

    assert os.path.exists(data_file)

    if client == ClientsEnum.REDIS:
        BankBenchmark(
            RedisBankClient,
            [{'interest': int_rate}, {'interest': int_rate}, {'interest': int_rate}],
            data_file
        ).run()
    elif client == ClientsEnum.REDBLUE:
        BankBenchmark(
            RedBlueBankClient,
            [
                {"port": 7379, 'interest': int_rate},
                {"port": 7380, 'interest': int_rate},
                {"port": 7381, 'interest': int_rate}],
            data_file
        ).run()
    else:
        raise ValueError(f"Unknown client: {client}")


@app.command(name="set")
def _set(
        client: Annotated[ClientsEnum, typer.Argument(case_sensitive=False, help="Client to use")],
        n_ops: Annotated[int, typer.Argument(help="Number of set ops")] = 1000000,
        add_p: Annotated[float, typer.Argument(help="Probability of adding to set", min=0, max=1)] = 0.9,
):
    data_file = f'../data/set/set_{n_ops // 1000}_{add_p * 10}.dat'
    if not os.path.exists(data_file):
        print("Generating data file")
        gen_set_data(n_ops, add_p, filepath=data_file)
        print("Data file generated")

    assert os.path.exists(data_file)

    if client == ClientsEnum.REDIS:
        SetBenchmark(RedisSetClient, [{}, {}, {}], data_file).run()
    elif client == ClientsEnum.REDBLUE:
        SetBenchmark(RedBlueSetClient, [{"port": 7379}, {"port": 7380}, {"port": 7381}], data_file).run()
    else:
        raise ValueError(f"Unknown client: {client}")


if __name__ == "__main__":
    app()
