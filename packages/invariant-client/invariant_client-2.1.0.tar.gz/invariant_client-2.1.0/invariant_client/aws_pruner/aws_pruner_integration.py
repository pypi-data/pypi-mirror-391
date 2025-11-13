
from argparse import Namespace
import io
import os
import pathlib
import shutil

import yaml

from invariant_client import aws_pruner, zip_util


def use_aws_pruner(tempdir: os.PathLike, args: Namespace, aws_pruner_debug_out: os.PathLike | None) -> io.BytesIO:
    # Use zipfile to inspect 'bytes', test if invariant/aws_pruner.yaml is present
    try:
        if pathlib.Path(tempdir, 'invariant', 'aws_pruner.yaml').exists():
            with open(pathlib.Path(tempdir, 'invariant', 'aws_pruner.yaml'), 'r') as f:
                pruner_config = aws_pruner.UserConfig.from_yaml(f.read())
        else:
            pruner_config = aws_pruner.UserConfig.from_dict({})
        apply_pruner = not getattr(args, 'no_aws_pruner') and pruner_config.enabled
        if apply_pruner:
            print("Pruning EC2 instances and network interfaces")
        else:
            print("Pruner dry run: pruning EC2 instances and network interfaces")

        # Discover all Reservations.json files and run the pruner on each (modify in place)
        for reservations_path in pathlib.Path(tempdir, 'aws_configs').rglob("Reservations.json"):
            path = pathlib.Path(reservations_path).parent
            print(f"Pruner: processing {path.relative_to(tempdir)}")
            aws_prune_tool = aws_pruner.AwsPruneTool(
                path,
                pruner_config.prune_level,
                pruner_config.filter_exclude,
                pruner_config.filter_include,
                pruner_config.group_by,
            )
            aws_prune_tool.load()
            aws_prune_tool.execute()
            aws_prune_tool.write()
        if aws_pruner_debug_out is not None:
            # Copy the contents of the aws_config directory in tempdir to aws_pruner_debug_out
            debug_out_path = pathlib.Path(aws_pruner_debug_out)
            if debug_out_path.is_dir():
                # remove contents
                shutil.rmtree(debug_out_path)
            print(f"Pruner writing debug output to {debug_out_path} ...")
            shutil.copytree(pathlib.Path(tempdir, 'aws_configs'), debug_out_path)
        return apply_pruner

    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return None
    except ValueError as e:
        print(f"Error loading invariant/aws_pruner.yaml: {e}")
        return None