import docker
from docker import APIClient
import click
import json
import os


def build_partition_container(image_name: str, partition: str):
    cli = APIClient()
    for output in cli.build(
        path=".",
        tag=image_name,
        dockerfile=f"Dockerfile.{partition}",
        network_mode="host"
    ):
        print(
            json.loads(
                output.decode()
            )["stream"]
        )

def create_partition_tar(docker_tag: str, outfile: str, retries: int=1):
    if retries < 0:
        raise ValueError("retries cannot be negative number")
    cli = docker.from_env()
    retries_left = retries + 1
    cnt = None
    while True:
        retries_left -= 1
        try:
            cnt = cli.containers.run(docker_tag, detach=True)
            print("Writing image tar")
            with open(outfile, "wb") as tar:
                with click.progressbar(length=2*1024*1024*1024) as bar:
                    for chunk in cnt.export():
                        size = tar.write(chunk)
                        bar.update(size)
        except Exception as e:
            if retries_left > 0:
                continue
            raise Exception(f"Failed getting image: {e}")
        finally:
            if cnt:
                cnt.stop()
                cnt.remove()
        break

@click.command()
@click.version_option()
@click.option("--image-prefix", type=str, required=True, default="quantotto/rpi")
@click.option("--tmp-dir", type=str, required=True, default="./tmp")
def build(image_prefix: str, tmp_dir: str):
    """Build Quantotto Raspberry Pi image
    with all the pre-requisites and Quantotto
    application packages
    """
    print(f"Building with temp dir={tmp_dir}")
    os.makedirs(tmp_dir, exist_ok=True)
    partitions = ["root"]
    for p in partitions:
        image_name = f"{image_prefix}_{p}:latest"
        build_partition_container(image_name, p)
        create_partition_tar(image_name, f"{tmp_dir}/{p}.tar")


if __name__ == '__main__':
    build()
