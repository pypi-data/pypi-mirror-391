"""
@Author = 'Michael Stanley'

A utility script to convert a folder of text files into a single key-value text file.

============ Change Log ============
11/10/2025 = Created.

============ License ============
Copyright (C) 2025 Michael Stanley

MIT License
"""
import click
import time
from datetime import datetime
from pathlib import Path

__version__ = "0.0.1"

@click.command()
@click.option("--folder", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), default=None,
              required=True, help="The path to the folder to watch.")
@click.option("--output", type=click.Path(file_okay=True, dir_okay=False, writable=True), default=None,
              required=True, help="The path to the output file.")
@click.option("--refresh_delay", type=float, default=1.0, required=False, 
              help="How long to sleep between each check of the folder for new data, in seconds. Default is to "
              "sleep for 1 second. Decimal values allowed. E.G. 0.25 to sleep for a quarter-second.")
def red_aluminum_cli(folder, output, refresh_delay):
    print(f"{datetime.now()}: Red Aluminum startup...")
    print(f"{datetime.now()}: Watching {folder}...")
    folder = Path(folder)
    output = Path(output)
    red_aluminum(folder, output, refresh_delay)


def red_aluminum(folder: Path, output: Path, refresh_delay: float):
    previous_data = {}
    while True:
        new_data = gather_data(folder=folder)
        consolidated_data = compare_and_consolidate_data(new_data=new_data, previous_data=previous_data)
        converted_data = convert_data_for_output(data=consolidated_data)
        print(f"{datetime.now()}: Output Data: {consolidated_data}")
        output_data(output_text=converted_data, output=output)
        previous_data = new_data
        time.sleep(refresh_delay)


def gather_data(folder: Path) -> dict:
    data = {}
    for file_item in folder.iterdir():
        if file_item.is_file():
            if file_item.suffix.casefold() == ".txt":
                file_data = read_file_data(file_item=file_item)
                data[file_item.stem] = file_data
    return data


def read_file_data(file_item: Path) -> str:
    file_data = ""
    try:
        with open(file=file_item, mode="rt") as file_reader:
            file_data = file_reader.read()
    except FileNotFoundError as fnf:
        file_data = ""
    return file_data.replace("\n", " ")


def compare_and_consolidate_data(new_data: dict, previous_data: dict) -> dict:
    consolidated_data = {}
    for key, value in new_data.items():
        if value:
            consolidated_value = value
        else:
            consolidated_value = previous_data.get(key, "")
        consolidated_data[key] = consolidated_value
    return consolidated_data


def convert_data_for_output(data: dict) -> str:
    output_lines = []
    data_keys = sorted(data.keys())
    for key in data_keys:
        this_data = data[key]
        this_line = f"{key} = {this_data}"
        output_lines.append(this_line)
    
    return "\n".join(output_lines)


def output_data(output_text: str, output: Path) -> None:
    try:
        with open(file=output, mode="wt") as output_writer:
            output_writer.write(output_text)
    except OSError as ose:
        # This should catch most of the errors when trying to write the file.
        print(f"Failure when writing file: {ose}")
