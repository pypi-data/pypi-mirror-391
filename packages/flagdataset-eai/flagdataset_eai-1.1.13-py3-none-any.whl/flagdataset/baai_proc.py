# -*- coding: utf-8 -*-

from pathlib import Path


def proc_data(cmd_args):
    from .process.handle import handle_single_data


    save_path_arg = cmd_args.save_path # noqa
    data_path = Path(save_path_arg) / "data"
    logw_path = Path(save_path_arg) / "log"
    proc_path = Path(save_path_arg) / "proc"
    proc_path.mkdir(parents=True, exist_ok=True)


    single_path = data_path / "data/contest"
    output_type = cmd_args.output_type

    print("============output_type==============")
    print(f"output_type: {output_type}\n")

    try:
        handle_single_data(single_path, [], proc_path, True, logw_path, output_type)
    except Exception as e:
        print(e)


    print()
    print(f"数据保存目录: {proc_path.absolute()}")
