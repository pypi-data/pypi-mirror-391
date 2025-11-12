import argparse
import os
import importlib.util
from omegaconf import OmegaConf
import inspect
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


from . import KagurazakaTask
from . import KagurazakaVanillaTorchTaskV1


def load_task_from_file(file_path, task_name):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Add the directory containing the task file to sys.path
    task_dir = os.path.dirname(os.path.abspath(file_path))
    import sys
    if task_dir not in sys.path:
        sys.path.insert(0, task_dir)

    # Load module spec
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, task_name)


def cfg_value_serializer(v):
    if isinstance(v, dict):
        return [json.dumps(v)]
    elif isinstance(v, list):
        return [cfg_value_serializer(item) for item in v]
    elif v == "store_true":
        return []
    else:
        return [str(v)]


def cfg_to_cli_args(resolved: dict | None):
    if resolved is None:
        return []
    ret = []
    for k, v in resolved.items():
        ret.extend([f"--{k}"] + cfg_value_serializer(v))
    return ret


def main():
    parser = argparse.ArgumentParser(description='Dynamically load a Python class from a module.', add_help=False)
    parser.add_argument('task_file_path', type=str, help='The file path of the task file')
    parser.add_argument('task_name', type=str, help='The name of the task class to use')
    parser.add_argument('--backbone', type=str, help='The backbone to use (default: auto)', default='auto', choices=['auto', 'mp', 'torch_vanilla_single'])
    parser.add_argument('--cfg', type=str, help='The file path of the config file to use.', default=None)
    parser.add_argument('--mixin-cfg', type=str, help='The file path of the mixin config file to use. Has higher priority than --cfg.', default=None)
    parser.add_argument('--mixin', type=str, nargs='+', help='The mixin to use. Has higher priority than --mixin-cfg. Provide in the format of "key=value".', default=[])

    parser.add_argument('-h', '--help', action='store_true', help='Show help message for task and exit')
    parser.add_argument('-hb', '--help-backbone', action='store_true', help='Show help message for chosen backbone and exit')
    parser.add_argument('-hk', '--help-kagurazaka', action='help', help='Show Kagurazaka help message and exit')
    args, remaining_args = parser.parse_known_args()

    # Load config
    if args.cfg is not None:
        cfg = OmegaConf.load(args.cfg)
        # inject some useful paths to the config, so can be used for omegaconf resolve
        cfg.CONFIG_DIR = os.path.abspath(os.path.dirname(args.cfg))
        cfg.SCRIPT_DIR = os.path.abspath(os.path.dirname(args.task_file_path))
        cfg.CONFIG_PATH = os.path.abspath(args.cfg)
        cfg.SCRIPT_PATH = os.path.abspath(args.task_file_path)

        resolved_cfg = OmegaConf.to_container(cfg, resolve=True)
        logger.info(f"Resolved config: {resolved_cfg}")

        cfg_mixin = cfg.mixin
        cfg_backbone = resolved_cfg.get("backbone", {})
        cfg_task = resolved_cfg.get("task", {})
    else:
        cfg_mixin = OmegaConf.create({})
        cfg_backbone = {}
        cfg_task = {}

    cfg_backbone_cli_args = cfg_to_cli_args(cfg_backbone)
    cfg_task_cli_args = cfg_to_cli_args(cfg_task)
    
    remaining_args += cfg_backbone_cli_args + cfg_task_cli_args
    
    print(remaining_args)

    # Mixin config -- CLI > YAML (mixin-cfg) > YAML (cfg)
    if args.mixin_cfg is not None:
        mixin_args = OmegaConf.load(args.mixin_cfg)
    else:
        mixin_args = OmegaConf.create({})
    if args.mixin is not None:
        mixin_args = OmegaConf.merge(cfg_mixin, mixin_args, OmegaConf.from_dotlist(args.mixin))
    mixin_args = OmegaConf.to_container(mixin_args, resolve=True)

    if args.help:
        remaining_args += ["-h"]
    if args.help_backbone:
        remaining_args += ["-hb"]

    loaded_task = load_task_from_file(args.task_file_path, args.task_name)
    logger.info(f"Successfully loaded task '{args.task_name}' from module '{args.task_file_path}'.")

    if inspect.isfunction(loaded_task):
        loaded_class = loaded_task(mixin_args)
    elif inspect.isclass(loaded_task):
        loaded_class = loaded_task
    else:
        raise ValueError("The loaded task is not a function or a class.")

    backbone = args.backbone

    if issubclass(loaded_class, KagurazakaTask):
        if backbone == 'auto': backbone = 'mp'
    if issubclass(loaded_class, KagurazakaVanillaTorchTaskV1):
        if backbone == 'auto': backbone = 'torch_vanilla_single'

    if backbone == 'mp':
        from .backbone.mp import process
    elif backbone == 'torch_vanilla_single':
        from .backbone.torch_vanilla_single import process
    else:
        raise ValueError(f"The backbone {backbone} is not supported.")

    process(loaded_class, remaining_args)
