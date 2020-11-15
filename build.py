import docker
from docker import APIClient
import click
import json
import os
import shutil
import subprocess


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
    out = ""
    for output in cli.build(
        path=".",
        rm=True,
        tag=image_name,
        dockerfile=f"Dockerfile.{partition}",
        network_mode="host"
    ):
        out = json.loads(
            output.decode()
        ).get("stream", "")
        click.echo(
            out,
            nl=False
        )
    if not out.startswith("Successfully tagged"):
        raise Exception("Error building container")

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
            click.echo("Writing image tar")
            with open(outfile, "wb") as tar:
                with click.progressbar(length=int(1.88*1024*1024*1024)) as bar:
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
    if not os.path.exists(base_image_file):
        raise Exception("Base image file does NOT exist")
    p = subprocess.run(
        args=[
            "sudo",
            "rm",
            "-rf",
            tmp_dir,
            out_dir
        ]
    )
    if p.returncode != 0:
        raise Exception("Error in init()")
    click.echo("Creating tars for image partitions")
    p = subprocess.run(
        args=[
            "bash",
            "./tar_partitions.sh",
            base_image_file,
            "baseboot.tar",
            "baseroot.tar"
        ]
    )
    if p.returncode != 0:
        raise Exception("Error in init()")
    os.makedirs(tmp_dir, exist_ok=True)
    click.echo("Initializing QEMU")
    init_qemu()
    click.echo("QEMU ready")

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
    click.echo(f"Building with temp dir={tmp_dir}")
    try:
        click.echo("Initializing")
        init(tmp_dir, out_dir, base_image_file)
        click.echo("Environment is ready")
        partitions = ["root"]
        for p in partitions:
            image_name = f"{docker_image_prefix}_{p}:latest"
            click.echo(f"Building container for {p} FS")
            build_partition_container(image_name, p)
            click.echo(f"Creating tar for {p} FS")
            create_partition_tar(image_name, f"{tmp_dir}/{p}.tar")
        shutil.copy("baseboot.tar", f"{tmp_dir}/boot.tar")
        click.echo(f"Assembling file systems into image")
        generate_final_image(tmp_dir, out_dir)
        click.echo(f"Image done and saved as {out_dir}/quantotto.zip")
    finally:
        if not keep_tmp:
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
