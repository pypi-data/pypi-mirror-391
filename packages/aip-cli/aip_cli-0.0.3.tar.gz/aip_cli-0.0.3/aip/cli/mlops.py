import logging

from aip.cli.cli import CLIGroup
from aip.core import Client

import click

logger = logging.getLogger(__name__)


@click.group(cls=CLIGroup, help="AIP CLI MLOps subcommand")
@click.pass_obj
def mlops(client: Client):
    pass


@mlops.command(help="Shows the models available")
@click.pass_obj
@click.option("-o", "--output", type=str, default="json", help="Output format. One of: (json, text)")
def list_models(client: Client, output):
    client.model("mlops", output=output).list_models()


@mlops.command(help="Show the list of experiments")
@click.pass_obj
@click.option("-o", "--output", type=str, default="json", help="Output format. One of: (json, text)")
def list_experiments(client: Client, output):
    client.model("mlops", output=output).list_experiments()


@mlops.command(help="Allows to start an experiment train")
@click.pass_obj
@click.option("--model-name", type=click.Choice(["HRNet","YOLOv7"]), required=True, help="Model names those are available in the model registry.")
@click.option("--task", type=click.Choice(["quant_pytorch"]), default="quant_pytorch", show_default=True, help="Type of the task.")
@click.option("--action", type=click.Choice(["train"]), default="train", show_default=True, help="Type of action.")
@click.option("--target", type=click.Choice(["v4h2"]), default="v4h2", show_default=True, help="Type of target board.")
@click.option("--line", type=click.Choice(["torch"]), default="torch", show_default=True, help="Line used.")
@click.option("--epochs", type=int, default=100, show_default=True, help="Number of epochs.")
@click.option("--do-ptq", type=bool, default=False, show_default=True, help="Boolean value if PTQ should be performed.")
@click.option("--train-batch-size", type=int, default=32, show_default=True, help="Size of batch used for training.")
@click.option("--early-exit-batches-per-epoch", type=int, default=4000, show_default=True, help="Number of batches per epoch for early exit.")
@click.option("--early-stopping-patience", type=int, default=8, show_default=True, help="Number of epochs for early exit.")
@click.option("-o", "--output", type=str, default="json", help="Output format. One of: (json, text)")
def train(client: Client, output, **kwargs):
    try:
       data = {key: value for key, value in kwargs.items() if value is not None}
       client.model("mlops", output=output).train(data)
    except Exception as e:
        print("Error type:", type(e).__name__)
        print("Error message:", e)  

@mlops.command(help="To check the status of an experiment created")
@click.pass_obj
@click.option("--experiment-id", type=str, required=True, help="ID of the experiment to determine the status")
@click.option("--type", type=str, default="train", show_default=True, help="Type of the experiment. One of: (train, deploy)")
@click.option("-o", "--output", type=str, default="json", help="Output format. One of: (json, text)")
def status(client: Client, output, **kwargs):
    experiment_id = kwargs["experiment_id"]
    experiment_type = kwargs["type"]
    client.model("mlops", output=output).status(experiment_id, experiment_type)


@mlops.command(help="To fetch the results of a completed experiment")
@click.pass_obj
@click.option("--experiment-id", type=str, required=True, help="ID of the experiment to fetch the result")
@click.option("--type", type=str, default="train", show_default=True, help="Type of the experiment. One of: (train, deploy)")
@click.option("-o", "--output", type=str, default="json", help="Output format. One of: (json, text)")
def result(client: Client, output, **kwargs):
    experiment_id = kwargs.values()
    experiment_type = kwargs["type"]
    client.model("mlops", output=output).result(experiment_id, experiment_type)


@mlops.command(help="To deploy the model on to a board")
@click.pass_obj
@click.option("--deployment-backend", type=str, default="cmn_app", help="Type of backend for the deployment.")
@click.option("--model-name", required=True, type=str, help="Model name those are available.")
@click.option("--target", default="v4h2", type=str, show_default=True, help="Type of target board.")
@click.option("--input-video", type=str, help="Directory path of input video.")
# @click.option("--job-type", type=str, help="Type of job, defaults to reaction_cmn_app")
@click.option("-o", "--output", type=str, help="Output format. One of: (json, text)")
def deploy(client: Client, output, **kwargs):
    data = {key: value for key, value in kwargs if value is not None}
    client.model("mlops", output=output).deploy(data)
