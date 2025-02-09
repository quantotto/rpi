# Quantotto Raspberry Pi image

Building Raspeberry Pi image for Quantotto Agents deployment.

> NOTE:
> - We assume you have a base Raspberry Image (either downloaded or manually built with pi-gen tool)
> - The procedures and tools provided in the repo are adding Quantotto packages and necessary configuration on top of existing OS image

## Pre-requisites

> NOTE:  these instructions don't cover how to install / configure pre-requisites

- Ubuntu 18.04 or later
- Docker
- Python 3.6+
- User with password-less sudo (member of `sudoer` group) to avoid password prompts

## Preparing your environment

Follow the steps below to get your Ubuntu machine ready for image builds.

- Update your OS:
```bash
sudo apt-get -yy update && sudo apt-get -yy upgrade
```

- Install software packages:
```bash
sudo apt-get -yy install \
    coreutils quilt parted \
    qemu-user-static debootstrap \
    zerofree zip dosfstools \
    libarchive-tools libcap2-bin grep \
    rsync xz-utils file git curl bc \
    python3-venv
```
> NOTE: if `libarchive-tools` is not available, try replacing it with `bsdtar` (`bsdtar` is obsolete on newer Ubuntu releases)

- Create python3 virtual environment:
```bash
python3 -m venv .venv
```

- Activate Virtual Environment:
```bash
source .venv/bin/activate
```

- Update / Install Python packages:
```
pip install -U pip
pip install click
pip install docker
```

- Clone this repo
- Download Raspberry OS lite image or build your own with pi-gen up to stage 2 as described [here](https://github.com/RPi-Distro/pi-gen#stage-specification); if downloading:
    - example command would be:
    ```
    wget https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2020-08-24/2020-08-20-raspios-buster-armhf-lite.zip
    ```
    - unzip downloaded file (further steps assume we have a .img file as our base image); for example:
    ```
    unzip 2020-08-20-raspios-buster-armhf-lite.zip
    ```

# Building Image

- Check the location of your base .img file (we will pass it as argument to build command)
- If you would like to pre-set WiFi information and IP address to allow headless start, modify files under `root/` folder:
    - wpa_supplicant.conf (WiFi info)
    - dhcpcd.conf (Network settings: IP address, gateway, DNS etc.)

> NOTE: this build will make sure SSH is automatically configured and started after first boot

- Run python build script (replace `path/to/file.img` with path to base Raspberry OS image file):
```bash
python build.py --base-image-file path/to/file.img
```

- Resulting image will be stored in out/quantotto.zip

## Using build.py CLI tool

- You can configure output directory and other build properties by providing command line arguments
- Please refer to `python build.py --help` for more info:

```
$ python build.py --help
Usage: build.py [OPTIONS]

  Build Quantotto Raspberry Pi image with all the pre-requisites and
  Quantotto application packages

Options:
  --version                   Show the version and exit.
  --base-image-file TEXT      Path to base Raspberry OS image file  [required]
  --docker-image-prefix TEXT  docker image tag prefix  [default:
                              quantotto/rpi; required]

  --tmp-dir TEXT              Temporary directory location  [default: ./tmp;
                              required]

  --out-dir TEXT              Image output directory  [default: ./out;
                              required]

  --keep-tmp                  Do not delete temporary directory (for script
                              debugging)  [default: False]

  --help                      Show this message and exit.
```


## References

- https://github.com/RPi-Distro/pi-gen/blob/master/README.md
- https://www.boulderes.com/resource-library/building-raspberry-pi-disk-images-with-docker-a-case-study-in-software-automation



