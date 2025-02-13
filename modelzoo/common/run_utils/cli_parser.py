# Copyright 2022 Cerebras Systems.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" PyTorch CLI Utilities"""
import argparse
import collections
import logging
import os
import sys
from typing import Callable, List, Optional

import yaml

from modelzoo.common.run_utils.utils import DeviceType, ExecutionStrategy


def read_params_file(params_file: str) -> dict:
    """ Helper for loading params file. """
    with open(params_file, 'r') as stream:
        params = yaml.safe_load(stream)
    return params


def get_params(params_file: str,) -> dict:
    """Reads params from file and returns them as a dict.

    Args:
        params_file: The YAML file holding the params.
        config: Optional config to load from the params. If None, the default
            config is returned. Defaults to None.
    Returns:
        A dict containing the params.
    """
    params = read_params_file(params_file)

    return params


def get_all_args(
    extra_args_parser_fn: Optional[
        Callable[[], List[argparse.ArgumentParser]]
    ] = None,
):
    """Helper for returning all valid params for each device."""
    parser = get_parser(
        first_parse=False, extra_args_parser_fn=extra_args_parser_fn
    )
    cpu_args = parser.parse_args([DeviceType.CPU, "-m", "train"])
    gpu_args = parser.parse_args([DeviceType.GPU, "-m", "train"])
    pipeline_args = parser.parse_args(
        [DeviceType.CSX, ExecutionStrategy.pipeline, "-m", "train"]
    )
    ws_args = parser.parse_args(
        [DeviceType.CSX, ExecutionStrategy.weight_streaming, "-m", "train"]
    )

    return cpu_args, gpu_args, pipeline_args, ws_args


def discard_params(
    device: str,
    exec_strat: Optional[ExecutionStrategy],
    extra_args_parser_fn: Optional[
        Callable[[], List[argparse.ArgumentParser]]
    ] = None,
):
    """ External utility for determing
    invalid parameters for the current device type. """

    cpu_args, gpu_args, pipeline_args, ws_args = get_all_args(
        extra_args_parser_fn
    )

    if device == DeviceType.CPU:
        curr_device_args = vars(cpu_args).keys()
    elif device == DeviceType.GPU:
        curr_device_args = vars(gpu_args).keys()
    elif device == DeviceType.CSX and exec_strat == ExecutionStrategy.pipeline:
        curr_device_args = vars(pipeline_args).keys()
    elif (
        device == DeviceType.CSX
        and exec_strat == ExecutionStrategy.weight_streaming
    ):
        curr_device_args = vars(ws_args).keys()
    else:
        raise ValueError(
            f"Invalid entry for device {device} and/or execution strategy {exec_strat}"
        )

    all_params = (
        vars(cpu_args).keys()
        | vars(gpu_args).keys()
        | vars(pipeline_args).keys()
        | vars(ws_args).keys()
    )
    discard_params_list = set(all_params) - (set(curr_device_args))

    return discard_params_list


def assemble_disallowlist(
    params: dict,
    extra_args_parser_fn: Optional[
        Callable[[], List[argparse.ArgumentParser]]
    ] = None,
) -> list:
    """ Determine invalid parameters for the current device type. """
    # cpu parser does not currently contain any additional information
    # or parameters but will parse through its elements as well just
    # in case that changes in the future.
    cpu_args, gpu_args, pipeline_args, ws_args = get_all_args(
        extra_args_parser_fn
    )

    all_params_template = {
        **vars(cpu_args),
        **vars(gpu_args),
        **vars(pipeline_args),
        **vars(ws_args),
    }
    unacceptable_params = set(all_params_template.keys()).difference(
        set(params.keys())
    )

    return all_params_template, list(unacceptable_params)


def add_general_arguments(
    parser: argparse.ArgumentParser,
    default_model_dir: str,
    first_parse: bool = True,
):
    """ Injects general parser arguments.

    Args:
        parser: Parser into which the arguments are being added.
        default_model_dir: String containing model directory path.
        first_parse: Boolean indicating whether this is the first
          time processing the arguments. If True, the "params" arg
          is required to get additional parameters, if False then
          the params file has already been read and is not required.
    """
    required_arguments = parser.add_argument_group("Required Arguments")
    required_arguments.add_argument(
        "-p",
        "--params",
        required=first_parse,
        help="Path to .yaml file with model parameters",
    )
    required_arguments.add_argument(
        "-m",
        "--mode",
        required=True,
        choices=["train", "eval", "train_and_eval", "eval_all"],
        help=(
            "Select mode of execution for the run. Can choose "
            "between train, eval, train_and_eval or eval_all."
        ),
    )
    optional_arguments = parser.add_argument_group(
        "Optional Arguments, All Devices"
    )
    optional_arguments.add_argument(
        "-o",
        "--model_dir",
        default=default_model_dir,
        help="Model directory where checkpoints will be written.",
    )
    optional_arguments.add_argument(
        "--checkpoint_path",
        default=None,
        help="Checkpoint to initialize weights from.",
    )
    optional_arguments.add_argument(
        "--is_pretrained_checkpoint",
        action="store_true",
        default=None if first_parse else False,
        help=(
            "Flag indicating that the provided checkpoint is from a "
            "pre-training run. If set, training will begin from step 0 "
            "after loading the matching weights from the checkpoint and "
            "ignoring the optimizer state if present in the checkpoint."
            "Defaults to False."
        ),
    )
    optional_arguments.add_argument(
        "--logging",
        default=None,
        help="Specifies the default logging level. Defaults to INFO.",
    )
    optional_arguments.add_argument(
        "--max_steps",
        type=int,
        default=None,
        help="Specifies the maximum number of steps to run.",
    )
    optional_arguments.add_argument(
        "--eval_steps",
        type=int,
        default=None,
        help="Specifies the number of steps to run for eval.",
    )

    return


def add_csx_arguments(
    parser: argparse.ArgumentParser, first_parse: bool = True,
):
    """ Injects Cerebras System specific parser arguments.

    Args:
        parser: Parser into which the arguments are being added.
        first_parse: Boolean indicating whether this is the first
          time processing the arguments. If True, default args
          are ignored in case the other has them stored elsewhere.
          If False, default args are set.
    """
    optional_arguments = parser.add_argument_group(
        "Optional Arguments, CSX Specific"
    )
    group = optional_arguments.add_mutually_exclusive_group()
    group.add_argument(
        "--compile_only",
        action="store_true",
        default=None,
        help="Enables compile only workflow. Defaults to None.",
    )
    group.add_argument(
        "--validate_only",
        action="store_true",
        default=None,
        help="Enables validate only workflow"
        "validate_only stops the compilation at ws_km stage for weight streaming mode."
        "for pipeline mode, the compilation is stopped at the optimize_graph stage."
        "Defaults to None.",
    )
    optional_arguments.add_argument(
        "--num_workers_per_csx",
        default=None if first_parse else 0,
        type=int,
        help="Number of workers to use for streaming inputs per CS node. If "
        "0, a default value based on the model will be chosen. Defaults "
        "to 0.",
    )
    optional_arguments.add_argument(
        "-c",
        "--compile_dir",
        default=None,
        help="Compile directory where compile artifacts will be written.",
    )
    optional_arguments.add_argument(
        "--job_labels",
        nargs="+",
        help="A list of equal-sign-separated key value pairs served as job labels.",
    )
    optional_arguments.add_argument(
        "--debug_args_path",
        default=None,
        help="Path to debugs args file. Defaults to None.",
    )
    optional_arguments.add_argument(
        "--mount_dirs",
        nargs="+",
        help="A list of paths to be mounted to the appliance containers. "
        "It should generally contain path to the directory containing the "
        "Cerebras modelzoo.",
    )
    optional_arguments.add_argument(
        "--python_paths",
        nargs="+",
        help="A list of paths to be exported into PYTHONPATH for worker containers. "
        "It should generally contain path to the directory containing the "
        "Cerebras modelzoo, as well as any external python packages needed by input workers.",
    )
    optional_arguments.add_argument(
        "--credentials_path",
        default=None,
        help="Credentials for cluster access. Defaults to None. If None, the value from "
        "a pre-configured location will be used if available.",
    )
    optional_arguments.add_argument(
        "--mgmt_address",
        default=None,
        help="<host>:<port> for cluster management. Defaults to None. If None, the value from "
        "a pre-configured location will be used if available.",
    )
    optional_arguments.add_argument(
        "--job_time_sec",
        type=int,
        default=None,
        help="time limit in seconds for the appliance jobs. When the time limit "
        "is hit, the appliance jobs will be cancelled and the run will be terminated",
    )
    optional_arguments.add_argument(
        "--disable_version_check",
        action="store_true",
        help="Disable version check for local experimentation and debugging",
    )

    return


def add_ws_arguments(
    ws_parser: argparse.ArgumentParser, first_parse: bool = True,
):
    """ Injects weightstreaming specific parser arguments.

    Args:
        ws_parser: Parser into which the arguments are being added.
    """
    add_csx_arguments(ws_parser, first_parse)
    optional_arguments = ws_parser.add_argument_group(
        "Optional Arguments, Weightstreaming Execution Strategy"
    )
    # Weightstreaming-only arguments
    optional_arguments.add_argument(
        "--num_csx",
        default=None if first_parse else 1,
        type=int,
        help="Number of CS nodes. Defaults to 1",
    )
    optional_arguments.add_argument(
        "--num_wgt_servers",
        default=None,
        type=int,
        help="Maximum number of weight servers to use in weight streaming "
        "execution strategy. Defaults to None.",
    )
    optional_arguments.add_argument(
        "--num_act_servers",
        default=None if first_parse else 1,
        type=int,
        help="Number of ACT server per device. Defaults to 1.",
    )

    return


def add_pipeline_arguments(
    pipeline_parser: argparse.ArgumentParser, first_parse: bool = True,
):
    """ Injects pipeline specific parser arguments.

    Args:
        pipeline_parser: Parser into which the arguments are being added.
    """
    add_csx_arguments(pipeline_parser, first_parse)
    optional_arguments = pipeline_parser.add_argument_group(
        "Optional Arguments, Pipeline Execution Strategy"
    )
    # Pipeline-only argument(s)
    optional_arguments.add_argument(
        "--multireplica",
        action="store_true",
        default=None,
        help="Enables multireplica mode. Defaults to None.",
    )

    return


def add_gpu_arguments(
    gpu_parser: argparse.ArgumentParser, first_parse: bool = True
):
    """ Injects GPU specific parser arguments.

    Args:
        gpu_parser: Parser into which the arguments are being added.
    """
    optional_arguments = gpu_parser.add_argument_group(
        "Optional Arguments, GPU Specific"
    )
    optional_arguments.add_argument(
        "-dist_addr",
        "--dist_addr",
        default=None if first_parse else "localhost:8888",
        help="To init master_addr and master_port of distributed. Defaults to localhost:8888.",
    )
    optional_arguments.add_argument(
        "-dist_backend",
        "--dist_backend",
        choices=["nccl", "mpi", "gloo"],
        default=None if first_parse else "nccl",
        help="Distributed backend engine. Defaults to nccl.",
    )
    optional_arguments.add_argument(
        "-init_method",
        "--init_method",
        default=None if first_parse else "env://",
        help="URL specifying how to initialize the process group. Defaults to env://",
    )

    return


def get_parser(
    run_dir: Optional[str] = None,
    first_parse: bool = True,
    extra_args_parser_fn: Optional[
        Callable[[], List[argparse.ArgumentParser]]
    ] = None,
) -> argparse.ArgumentParser:
    """Returns an ArgumentParser for parsing commandline options.

    Args:
        run_dir: String to be used to determine model directory.
        first_parse: Boolean indicating whether this is the first
          time processing the arguments. If True, the parser is
          being used to collect commandline inputs. If False, it
          is only being used for verification on existing params.
        extra_args_parser_fn: Parent parser passed in by models with
          unique specific arguments.
    Returns:
        A parser instance.
    """

    default_model_dir = None

    if first_parse:
        # Set default model dir to be inside same directory
        # as the top level run.py
        if run_dir:
            default_model_dir = os.path.join(run_dir, "model_dir")

        if not default_model_dir:
            raise ValueError("Could not get default model directory")

    parents = []
    extra_args = {}
    if extra_args_parser_fn:
        extra_args = extra_args_parser_fn()
        if isinstance(extra_args, argparse.ArgumentParser):
            # pylint: disable=protected-access
            extra_args._action_groups[
                1
            ].title = "User-Defined and/or Model Specific Arguments"
            parents.append(extra_args)
        if not isinstance(extra_args, dict):
            # Rename the action groups of each parser passed into this parser generator
            if isinstance(extra_args, list):
                for item in extra_args:
                    # pylint: disable=protected-access
                    item._action_groups[
                        1
                    ].title = "User-Defined and/or Model Specific Arguments"
            extra_args = {DeviceType.ANY: extra_args}

        parents.extend(extra_args.get(DeviceType.ANY, []))

    parent = argparse.ArgumentParser(parents=parents, add_help=False)
    add_general_arguments(parent, default_model_dir, first_parse)

    parser = argparse.ArgumentParser(
        epilog=(
            "Please run 'python run.py {CPU,GPU} -h' or 'python run.py CSX {pipeline,weight_streaming} -h' \n"
            "to list available subcommands. \n \n"
            "Here are some example commands for running on different devices: \n \n"
            "    python run.py CPU --params /path/to/params.yaml --mode train \n \n"
            "    python run.py CSX weight_streaming --params /path/to/params.yaml --mode eval --num_csx 1 \n \n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sp = parser.add_subparsers(title="Target Device", dest="target_device")
    sp.required = True

    sp.add_parser(
        DeviceType.CPU,
        parents=[parent] + extra_args.get(DeviceType.CPU, []),
        help="Run on CPU",
    )

    gpu_parser = sp.add_parser(
        DeviceType.GPU,
        parents=[parent] + extra_args.get(DeviceType.GPU, []),
        help="Run on GPU",
    )
    add_gpu_arguments(gpu_parser, first_parse)

    csx_parser = sp.add_parser(
        DeviceType.CSX,
        help="Run on Cerebras System",
        epilog=(
            "To see a complete list of all available arguments for your chosen execution strategy, \n"
            "please run 'python run.py CSX {pipeline,weight_streaming} -h'. \n\n"
            "Here are some example commands for running with different execution strategies: \n \n"
            "    python run.py CSX weight_streaming --params /path/to/params.yaml --mode eval --num_csx 1 \n \n"
            "    python run.py CSX pipeline --params /path/to/params.yaml --mode train --multireplica \n \n"
            "When running from the Cerebras Modelzoo, you generally specify --python_paths and \n"
            "--mount_dirs. This can be done here or in the params under the 'runconfig' section \n"
            "Both should at least include a path \n"
            "to the directory in which the Cerebras Modelzoo resides. \n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    execution_strategy_parser = csx_parser.add_subparsers(
        title="Execution Strategy", dest="execution_strategy"
    )
    execution_strategy_parser.required = True

    # PIPELINED EXECUTION MODE
    pipeline_parser = execution_strategy_parser.add_parser(
        ExecutionStrategy.pipeline,
        usage=(
            "CSX pipeline ... --params /path/to/params.yaml --mode {mode} --python_paths /path/to/modelzoo"
            "{paths to other python packages needed by dataloader ...}  --mount_dirs "
            "/path/to/modelzoo {path to directories needed by dataloader ...}"
        ),
        parents=[parent] + extra_args.get(ExecutionStrategy.pipeline, []),
        help="Run the pipeline execution strategy on the Cerebras System.",
    )
    add_pipeline_arguments(pipeline_parser, first_parse)

    # WEIGHTSTREAMING EXECUTION MODE
    ws_parser = execution_strategy_parser.add_parser(
        ExecutionStrategy.weight_streaming,
        usage=(
            "CSX weight_streaming ... --params /path/to/params.yaml --mode {mode} --python_paths "
            "/path/to/modelzoo {paths to other python packages needed by dataloader ...} "
            "--mount_dirs /path/to/modelzoo {path to directories needed by dataloader ...}"
        ),
        parents=[parent]
        + extra_args.get(ExecutionStrategy.weight_streaming, []),
        help="Run the weight-streaming execution strategy on the Cerebras System.",
    )
    add_ws_arguments(ws_parser, first_parse)

    return parser


def update_defaults(params: dict, default_params: dict) -> dict:
    """Updates the params dict with global default for a key
    if a key is not present.
    Works on nested dictionaries and recursively updates defaults
    for nested dictionaries.
    All other types, apart from dict are considered as base type
    and aren't updated recursively.
    Args:
        params: dict holding the params.
        default_params: dict holding the default params.
    Returns:
        A dict containing the params, with the defaults updated
    """
    for k, v in default_params.items():
        if isinstance(v, collections.abc.Mapping):
            params[k] = update_defaults(params.get(k, {}), v)
        elif k not in params:
            params[k] = v
    return params


def update_params_from_file(params, params_file):
    """Update provided params from provided file"""
    if os.path.exists(params_file):
        default_params = read_params_file(params_file)
        update_defaults(params, default_params)


def update_params_from_args(
    args: argparse.Namespace, params: dict, sysadmin_params: dict
):
    """Update params in-place with the arguments from args.

    Args:
        args: The namespace containing args from the commandline.
        params: The params to be updated.
        first_parse: Indicates whether to keep in the params path.
    """
    if args:
        for (k, v) in list(vars(args).items()):
            if k in ["config", "params"]:
                continue
            if k in ["python_paths", "mount_dirs"]:
                append_args = []
                if v is not None:
                    logging.info(v)
                    append_args.extend([v] if isinstance(v, str) else v)
                if params.get(k) is not None:
                    logging.info(params[k])
                    append_args.extend(
                        [params[k]] if isinstance(params[k], str) else params[k]
                    )
                if sysadmin_params.get(k) is not None:
                    logging.info(sysadmin_params[k])
                    append_args.extend(
                        [sysadmin_params[k]]
                        if isinstance(sysadmin_params[k], str)
                        else sysadmin_params[k]
                    )
                if append_args:
                    params[k] = append_args
                continue

            params[k] = (
                v
                if v is not None
                else (params.get(k) or sysadmin_params.get(k))
            )

    if params.get("is_pretrained_checkpoint") and not params.get(
        "checkpoint_path"
    ):
        raise RuntimeError(
            "'--is_pretrained_checkpoint' can only be used if a "
            "'--checkpoint_path' is provided."
        )

    mode = params.get("mode")
    if mode != "train" and params.get("multireplica"):
        logging.warning(
            f"Multireplica is only supported in `train` mode. "
            f"Disabling it for {mode} mode."
        )
        params["multireplica"] = None

    model_dir = params["model_dir"]
    os.makedirs(model_dir, exist_ok=True)
    params.setdefault("service_dir", model_dir)


def post_process_params(
    params: dict, valid_arguments: list, invalid_arguments: list
) -> list:
    """ Removes arguments that are not used by this target device. """
    target_device = params["runconfig"].pop("target_device", None)
    execution_strategy = params["runconfig"].pop("execution_strategy", None)
    assert target_device is not None

    new_command, invalid_params = [], []
    new_command.append(target_device)
    if execution_strategy:
        new_command.append(execution_strategy)

    for k, v in params["runconfig"].copy().items():
        if v == None or v == False:
            continue

        # Ignore arguments from params.yaml that apply to different devices
        if k in invalid_arguments:
            invalid_params.append(k)
            params["runconfig"].pop(k)
        # Construct new parser input ignoring extra args that the parser
        # does not handle, such as num_epochs
        elif k in valid_arguments:
            new_command.append(f"--{k}")
            if isinstance(v, list):
                new_command.extend(map(str, v))
            elif not isinstance(v, bool):
                new_command.append(f"{v}")

    if invalid_params:
        logging.info(
            f"User specified a {target_device} run, but the following "
            f"non-{target_device} configurations were found in params file: "
            f"{str(invalid_params)}. Ignoring these arguments and continuing."
        )

    return new_command


def get_params_from_args(
    run_dir: Optional[str] = None,
    argv: Optional[List] = None,
    extra_args_parser_fn: Optional[
        Callable[[], List[argparse.ArgumentParser]]
    ] = None,
) -> dict:
    """
    Parse the arguments and get the params dict from the resulting args

    Args:
        run_dir: The path to the `run.py` file
        argv: The args to be parse. Defaults to sys.argv if not provided
    """
    parser = get_parser(run_dir, extra_args_parser_fn=extra_args_parser_fn)
    args = parser.parse_args(argv if argv else sys.argv[1:])

    params_template, invalid_params = assemble_disallowlist(
        vars(args), extra_args_parser_fn=extra_args_parser_fn
    )
    params = get_params(args.params,)

    sysadmin_file = os.getenv('CEREBRAS_WAFER_SCALE_CLUSTER_DEFAULTS')
    sysadmin_params = (
        get_params(sysadmin_file) if sysadmin_file is not None else {}
    )
    update_params_from_args(args, params["runconfig"], sysadmin_params)

    rerun_command = post_process_params(
        params, params_template.keys(), invalid_params
    )
    parser = get_parser(
        run_dir, first_parse=False, extra_args_parser_fn=extra_args_parser_fn
    )
    try:
        logging.info(rerun_command)
        params_final = parser.parse_args(rerun_command)
    except SystemExit:
        logging.error(
            f"A mismatch was detected between your params.yaml file "
            f"and specified command-line arguments. "
            f"Please correct the error and run again."
        )
        raise

    params["runconfig"] = {**params["runconfig"], **vars(params_final)}
    params["runconfig"] = {**params_template, **params["runconfig"]}
    params["runconfig"].pop("config", None)
    params["runconfig"].pop("params", None)

    return params
