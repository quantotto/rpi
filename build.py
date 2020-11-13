import docker
import click


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
            with open(outfile, "wb") as tar:
                for chunk in cnt.export():
                    tar.write(chunk)
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
@click.option("--force-rebuild", is_flag=True, default=False)
@click.option("--tmp-dir", type=str, required=True, default="./tmp")
def build(force_rebuild: bool, tmp_dir: str):
    """Build Quantotto Raspberry Pi image
    with all the pre-requisites and Quantotto
    application packages
    """
    print(f"Building with force_rebuild={force_rebuild}; temp dir={tmp_dir}")

    create_partition_tar("quantotto/rpi:latest", f"{tmp_dir}/root.tar")


if __name__ == '__main__':
    build()
