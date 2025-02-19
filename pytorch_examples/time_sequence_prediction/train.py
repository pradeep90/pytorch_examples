from __future__ import print_function
import argparse
import torch
from torch import Tensor, double
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pyre_extensions import Add
from typing_extensions import Literal as L
from typing import TypeVar, Tuple, List, overload

N1 = TypeVar("N1", bound=int)
N2 = TypeVar("N2", bound=int)
N3 = TypeVar("N3", bound=int)


class Sequence(nn.Module):
    def __init__(self) -> None:
        super(Sequence, self).__init__()
        self.lstm1: nn.LSTMCell[L[1], L[51]] = nn.LSTMCell(1, 51)
        self.lstm2: nn.LSTMCell[L[51], L[51]] = nn.LSTMCell(51, 51)
        self.linear: nn.Linear[L[51], L[1]] = nn.Linear(51, 1)

    @overload
    def forward(
        self, input: Tensor[double, N1, N2], future: L[0] = 0
    ) -> Tensor[double, N1, N2]:
        ...

    @overload
    def forward(
        self, input: Tensor[double, N1, N2], future: N3
    ) -> Tensor[double, N1, Add[N2, N3]]:
        ...

    def forward(
        self, input: Tensor[double, N1, N2], future: int = ...
    ) -> Tensor[double, N1, int]:
        outputs: List[Tensor[double, N1, L[1]]] = []
        h_t = torch.zeros(input.size(0), 51, dtype=torch.double)
        c_t = torch.zeros(input.size(0), 51, dtype=torch.double)
        h_t2 = torch.zeros(input.size(0), 51, dtype=torch.double)
        c_t2 = torch.zeros(input.size(0), 51, dtype=torch.double)

        for input_t in input.split(1, dim=1):
            h_t, c_t = self.lstm1(input_t, (h_t, c_t))
            h_t2, c_t2 = self.lstm2(h_t, (h_t2, c_t2))
            output = self.linear(h_t2)
            outputs.append(output)
        for i in range(future):  # if we should predict the future
            h_t, c_t = self.lstm1(output, (h_t, c_t))
            h_t2, c_t2 = self.lstm2(h_t, (h_t2, c_t2))
            output = self.linear(h_t2)
            outputs.append(output)

        # torch.cat is too dynamic, so we have to ignore an error.
        final_outputs = torch.cat(outputs, dim=1)
        return final_outputs  # type: ignore

    # Ideally, we'd say that the signature of `__call__` is the same as that
    # of `forward`. Unfortunately, I don't know of a way to do that.
    @overload
    def __call__(
        self, input: Tensor[double, N1, N2], future: L[0] = 0
    ) -> Tensor[double, N1, N2]:
        ...

    @overload
    def __call__(
        self, input: Tensor[double, N1, N2], future: N3
    ) -> Tensor[double, N1, Add[N2, N3]]:
        ...

    def __call__(
        self, input: Tensor[double, N1, N2], future: int = ...
    ) -> Tensor[double, N1, int]:
        ...


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=15, help="steps to run")
    opt = parser.parse_args()
    # set random seed to 0
    np.random.seed(0)
    torch.manual_seed(0)
    # load data and make training set
    data = torch.load("traindata.pt")
    input: Tensor[double, L[97], L[999]] = torch.from_numpy(data[3:, :-1])
    target: Tensor[double, L[97], L[999]] = torch.from_numpy(data[3:, 1:])
    test_input: Tensor[double, L[3], L[999]] = torch.from_numpy(data[:3, :-1])
    test_target: Tensor[double, L[3], L[999]] = torch.from_numpy(data[:3, 1:])

    # build the model
    seq = Sequence()
    seq.double()
    criterion = nn.MSELoss()
    # use LBFGS as optimizer since we can load the whole data to train
    optimizer = optim.LBFGS(seq.parameters(), lr=0.8)

    def closure() -> Tensor[double]:
        optimizer.zero_grad()
        out = seq(input)
        loss = criterion(out, target)

        print("loss:", loss.item())
        loss.backward()
        return loss

    def draw(yi, color):
        plt.plot(np.arange(input.size(1)), yi[: input.size(1)], color, linewidth=2.0)
        plt.plot(
            np.arange(input.size(1), input.size(1) + future),
            yi[input.size(1) :],
            color + ":",
            linewidth=2.0,
        )

    def draw_result(y) -> None:
        # draw the result
        plt.figure(figsize=(30, 10))
        plt.title(
            "Predict future values for time sequences\n(Dashlines are predicted values)",
            fontsize=30,
        )
        plt.xlabel("x", fontsize=20)
        plt.ylabel("y", fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)

        draw(y[0], "r")
        draw(y[1], "g")
        draw(y[2], "b")
        plt.savefig("predict%d.pdf" % i)
        plt.close()

    # begin to train
    for i in range(opt.steps):
        print("STEP: ", i)

        optimizer.step(closure)
        # begin to predict, no need to track gradient here
        with torch.no_grad():
            future = 1000
            pred = seq(test_input, future=future)
            loss = criterion(pred[:, :-future], test_target)
            print("test loss:", loss.item())
            y = pred.detach().numpy()

        draw_result(y)
