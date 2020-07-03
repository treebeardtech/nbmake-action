import csv

from dagster import execute_pipeline, execute_solid, pipeline, solid

from csv import DictReader


@solid
def hello_cereal(context):
    dataset_path = "cereal.csv"
    with open(dataset_path, "r") as fd:
        cereals = [row for row in csv.DictReader(fd)]

    context.log.info(f"Found {len(cereals)} cereals.")

    return cereals


@pipeline
def hello_cereal_pipeline():
    hello_cereal()


def test_hello_cereal_solid():
    res = execute_solid(hello_cereal)
    assert res.success
    assert len(res.output_value()) == 77


def test_hello_cereal_pipeline():
    res = execute_pipeline(hello_cereal_pipeline)
    assert res.success
    assert len(res.result_for_solid("hello_cereal").output_value()) == 77


if __name__ == "__main__":
    result = execute_pipeline(hello_cereal_pipeline)
    assert result.success
