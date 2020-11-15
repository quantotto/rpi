import docker
from docker import APIClient
import click
import json
import os
import shutil
import subprocess
import shlex


def init_qemu():
    cli = docker.from_env()
    cli.containers.run(
        "multiarch/qemu-user-static",
        command=["--reset", "-p", "yes"],
        remove=True,
        privileged=True
    )

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
            ).get("stream", ""),
            end=''
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

def generate_final_image(in_dir: str, out_dir: str):
    subprocess.run(
        args=[
            "sudo",
            "./generate.sh",
            in_dir,
            out_dir
        ],
        env=os.environ
    )

def init(tmp_dir: str, out_dir: str, base_image_file: str):
    subprocess.run(
            args=[
                "sudo",
                "rm",
                "-rf",
                tmp_dir,
                out_dir
            ]
        )
    subprocess.call(
        shlex.split(
            f"./extractfs.sh "
            f"{base_image_file} "
            f"baseboot.tar baseroot.tar"
        )
    )
    os.makedirs(tmp_dir, exist_ok=True)
    init_qemu()

@click.command()
@click.version_option()
@click.option("--base-image-file", type=str, required=True, prompt=True, help="Path to base Raspberry OS image file")
@click.option("--docker-image-prefix", type=str, required=True, default="quantotto/rpi", help="docker image tag prefix", show_default=True)
@click.option("--tmp-dir", type=str, required=True, default="./tmp", help="Temporary directory location", show_default=True)
@click.option("--out-dir", type=str, required=True, default="./out", help="Image output directory", show_default=True)
@click.option("--keep-tmp", is_flag=True, default=False, help="Do not delete temporary directory (for script debugging)", show_default=True)
def build(
    base_image_file: str,
    docker_image_prefix: str,
    tmp_dir: str,
    out_dir: str,
    keep_tmp: bool
):
    """Build Quantotto Raspberry Pi image
    with all the pre-requisites and Quantotto
    application packages
    """
    print(f"Building with temp dir={tmp_dir}")
    try:
        init(tmp_dir, out_dir, base_image_file)
        partitions = ["root"]
        for p in partitions:
            image_name = f"{docker_image_prefix}_{p}:latest"
            build_partition_container(image_name, p)
            create_partition_tar(image_name, f"{tmp_dir}/{p}.tar")
        shutil.copy("baseboot.tar", f"{tmp_dir}/boot.tar")
        generate_final_image(tmp_dir, out_dir)
        print(f"Image done and saved as {out_dir}/quantotto.zip")
    finally:
        if not keep_tmp:
            print(f"Deleting {tmp_dir}")
            subprocess.Popen(
                args=[
                    "sudo",
                    "rm",
                    "-rf",
                    tmp_dir
                ]
            )

if __name__ == '__main__':
    build()
