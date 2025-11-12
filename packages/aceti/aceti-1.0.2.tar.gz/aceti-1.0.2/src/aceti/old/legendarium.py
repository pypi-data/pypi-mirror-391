import sys
sys.path.append('.')

import pandas as pd
import numpy as np
import os
from typing import Union
import lzma
import pickle
import yaml
from collections import defaultdict

class Legendarium:

    def __init__(self, experiment_name : str, experiment_description : str, path : str):

        self._exp_name = experiment_name
        self._exp_desc = experiment_description
        self._path = path

        # Check if directory exists
        if path is not None:
            if not os.path.exists(self._path):
                os.makedirs(self._path)
            else:
                # Check if the there is a file with the same experiment name
                if os.path.exists(os.path.join(self._path, f"{self._exp_name}.metrics.xz")):
                    raise Exception("Experiment already exists!")
        

        self.metrics_meta = {}
        self.metrics = []
        self.parameters = {}
        self.n_metrics = 0
        self.data_names = []

    def create_parameter(self, parameter_name : str, parameter_value):        
        """ 
        Create a parameter for the experiment
        """
        self.parameters.update({parameter_name : parameter_value})

    def create_metric(self, metric_name : str, data_type : type, description : str, unit : str):

        self.metrics_meta.update({metric_name : {"type" : data_type, "description" : description, "unit" : unit, "order": self.n_metrics}})
        self.n_metrics += 1

    def write(self, run : int, step : int, **kwargs):
        """ 
        Write data to the metric
        """

        # Check if metric exists
        for metric_name, new_data in kwargs.items():

            if metric_name not in self.metrics_meta:
                raise Exception(f"Metric {metric_name} not found!")
            
            # Check if the data type is correct
            if not isinstance(run, int):
                raise Exception("Run should be an integer!")
            
            if not isinstance(step, int):
                raise Exception("Step should be an integer!")
            
            # Check if the data type is correct
            if not issubclass(type(kwargs[metric_name]), self.metrics_meta[metric_name]["type"]):
                raise Exception(f"Data type mismatch for metric {metric_name}!")
            
        # Check if all the metrics are present
        if len(kwargs) != self.n_metrics:
            raise Exception("Not all metrics are present in the data!")
        
        new_data = [run, step] + [None] * self.n_metrics
    
        
        for key, value in kwargs.items():
            
            # Comprobamos si la clave es una metrica registrada
            if key not in self.metrics_meta:
                raise Exception(f"Metric {key} not found!")
            
            # Comprobamos si el tipo de dato es correcto
            if not isinstance(value, self.metrics_meta[key]["type"]):
                raise Exception(f"Data type mismatch for metric {key}!")
            
            # Obtenemos la posición en la lista
            pos = self.metrics_meta[key]["order"]
            new_data[pos + 2] = value

        # Añadimos la información de los parámetros
        for key, value in self.parameters.items():
            new_data.append(value)
        
        self.metrics.append(new_data)


    def save(self):
        """
        Save the experiment
        """

        data_names = ["run", "step"] + list(self.metrics_meta.keys()) + list(self.parameters.keys())


        # Save the metrics
        with lzma.open(os.path.join(self._path, f"{self._exp_name}.metrics.xz"), "wb") as f:
            pickle.dump(self.metrics, f)

        # Save the metrics meta
        with open(os.path.join(self._path, f"{self._exp_name}.meta.yaml"), "w") as f:
            yaml.dump(data_names, f)


def load_experiment_pd(experiment_name : str, path : str):
    # Load the metrics as a pandas dataframe

    # Load the metrics
    with lzma.open(os.path.join(path, f"{experiment_name}.metrics.xz"), "rb") as f:
        metrics = pickle.load(f)

    # Load the metrics meta
    with open(os.path.join(path, f"{experiment_name}.meta.yaml"), "r") as f:
        data_names = yaml.load(f, Loader=yaml.FullLoader)

    # Create the dataframe
    df = pd.DataFrame(metrics, columns = data_names)

    return df

def load_experiments(path : str):
    # Load all the experiments in a directory and return a pandas dataframe

    pds = []

    for file in os.listdir(path):
        if file.endswith(".metrics.xz"):
            experiment_name = file.split(".")[0]
            try:
                df = load_experiment_pd(experiment_name, path)
                pds.append(df)
            except Exception as e:
                print(f"Error loading experiment {experiment_name}: {e}")


    return pd.concat(pds)


if __name__ == "__main__":


    # Create an instance of the class
    exp = Legendarium(f"test", "Test experiment", "experiments")

    # Create a parameter
    exp.create_parameter("algorithm", "Greedy")
    exp.create_parameter("max_distance", 100.0)

    # Create a metric
    exp.create_metric("reward", float, "Reward function", "points")
    exp.create_metric("map", np.ndarray, "Mean map", "%")

    for run in range(3):

        # Write data
        for i in range(100):
            exp.write(run = run, step = i, reward = np.random.rand(), map = np.random.rand(100,100))

    # Save the data
    exp.save()

    # Load the data
    df = load_experiments("experiments")
    print(df.head())

    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.lineplot(data = df, x = "step", y = "reward", hue = "run")
    plt.show()