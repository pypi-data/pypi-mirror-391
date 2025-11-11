import os
from abc import ABC, abstractmethod

class QuantumDataPltPlotter(ABC):
    def __init__(self, task_type: str):
        self.task_type = task_type


    @abstractmethod
    def plot_result_npy(self, **kwargs):
        pass

    def plot_result_npz(self, **kwargs):
        pass

    def save_plot(self, fig, save_name: str = "result_",save_format: str = "png"):
        save_path = "./tmp/client/"+save_name +"."+ save_format
        fig.savefig(save_path)
