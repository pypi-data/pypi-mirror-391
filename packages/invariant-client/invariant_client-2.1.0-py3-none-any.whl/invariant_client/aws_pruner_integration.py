
import io
import pathlib
import shutil
import tempfile
import zipfile

import yaml

from invariant_client import aws_pruner, zip_util


AWS_PRUNER_CONFIG_PATH = 'invariant/aws_pruner.yaml'


def use_aws_pruner(bytes: io.BytesIO, no_aws_pruner: bool, aws_pruner_debug_out: str | None) -> io.BytesIO:
    # Use zipfile to inspect 'bytes', test if invariant/aws_pruner.yaml is present
    try:
        with zipfile.ZipFile(bytes, 'r') as zf:
            # get the root path of the zip file
            root_path = pathlib.Path(zf.filelist[0].filename).parts[0]
            if f"{root_path}/{AWS_PRUNER_CONFIG_PATH}" not in zf.namelist():
                return bytes

            if f"{root_path}/aws_configs/" not in zf.namelist():
                return bytes

            with zf.open(f"{root_path}/{AWS_PRUNER_CONFIG_PATH}") as f:
                pruner_config = aws_pruner.UserConfig.from_yaml(f.read().decode('utf-8'))

            apply_pruner = not no_aws_pruner and pruner_config.enabled
            if apply_pruner:
                print("Pruning EC2 instances and network interfaces")
            else:
                print("Pruner dry run: pruning EC2 instances and network interfaces")

            # If use_pruner, copy to tempdir and execute pruner
            with tempfile.TemporaryDirectory() as tempdir:
                # Copy the snapshot to the tempdir
                bytes.seek(0)
                # extract zf to tempdir
                zf.extractall(tempdir)
                # Discover all Reservations.json files and run the pruner on each (modify in place)
                for reservations_path in pathlib.Path(tempdir, root_path, 'aws_configs').rglob("Reservations.json"):
                    path = pathlib.Path(reservations_path).parent
                    print(f"Pruner: processing {path}")
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
                    shutil.copytree(pathlib.Path(tempdir, root_path, 'aws_configs'), debug_out_path)
                if apply_pruner:
                    # Create a new zipfile from the pruned snapshot in the tempdir, discarding the original
                    bytes = io.BytesIO()
                    zip_util.zip_dir(pathlib.Path(tempdir, root_path), bytes)

    except zipfile.BadZipFile:
        print(f"Error: unable to read snapshot zip file, invalid zip file.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return None
    except ValueError as e:
        print(f"Error loading invariant/aws_pruner.yaml: {e}")
        return None

    # Esnure bytes is at position 0
    bytes.seek(0)
    return bytes
