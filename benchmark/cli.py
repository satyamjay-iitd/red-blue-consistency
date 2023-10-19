from enum import Enum
from typing import Annotated

import typer

from benchmarks import WCBenchmark
from clients import RedisWCClient, RedBlueWCClient

app = typer.Typer()


class ClientsEnum(str, Enum):
    REDIS = "redis"
    REDBLUE = "redblue"

    def to_client(self):
        if self == ClientsEnum.REDIS:
            return RedisWCClient()
        elif self == ClientsEnum.REDBLUE:
            return RedBlueWCClient()


@app.command()
def wc(
        client: Annotated[ClientsEnum, typer.Argument(case_sensitive=False, help="Client to use")],
        txt_file: Annotated[str, typer.Argument(help="Path to text file", exists=True)] = '../data/small.txt'
):
    benchmark = WCBenchmark(client.to_client(), txt_file)
    benchmark.run()


@app.command()
def sdu(
        _: Annotated[ClientsEnum, typer.Argument(case_sensitive=False, help="Client to use")],
):
    raise NotImplementedError()


if __name__ == "__main__":
    app()
