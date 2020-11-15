#/bin/bash

set -e

if [ -z $3 ]; then
    echo "Usage: $0 <Image File> <boot fs tar path> <root fs tar path>"
    exit 1
fi

IMAGE_FILE=$(realpath $1)
BOOT_TAR=$2
ROOT_TAR=$3
LOOPDEV=""

trap onerror ERR

function cleanup() {
    echo "Cleaning up"
    mount | grep "${LOOPDEV}" | awk '{ print $3 }' | xargs -r sudo umount
    losetup -a | grep "${IMAGE_FILE}" | awk -F: '{ print $1 }' | xargs -r sudo losetup -d
    sudo rm -rf tmpboot
    sudo rm -rf tmproot
}

function onerror() {
    cleanup
    sudo rm -rf ${BOOT_TAR}
    sudo rm -rf ${ROOT_TAR}
}

sudo rm -rf ${BOOT_TAR}
sudo rm -rf ${ROOT_TAR}

losetup -a | grep "${IMAGE_FILE}" | awk -F: '{ print $1 }' | xargs -r sudo losetup -d
sudo losetup -fP ${IMAGE_FILE}
LOOPDEV=$(losetup -a | grep "${IMAGE_FILE}" | awk -F: '{ print $1 }')

sudo rm -rf tmpboot
sudo rm -rf tmproot

mkdir -p tmpboot
mkdir -p tmproot

sudo mount ${LOOPDEV}p1 ./tmpboot
sudo mount ${LOOPDEV}p2 ./tmproot

sudo tar cf ${BOOT_TAR} -C ./tmpboot --numeric-owner --no-ignore-command-error .
sudo tar cf ${ROOT_TAR} -C ./tmproot --numeric-owner --no-ignore-command-error .

cleanup
