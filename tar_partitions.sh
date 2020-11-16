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
    mount | grep "${LOOPDEV}" | awk '{ print $3 }' | xargs -r sudo umount
    sudo losetup -a | grep "${IMAGE_FILE}" | awk -F: '{ print $1 }' | xargs -r sudo losetup -d
    sudo rm -rf tmpboot
    sudo rm -rf tmproot
}

function onerror() {
    echo "Error creating tars for partitions"
    cleanup
    sudo rm -rf ${BOOT_TAR}
    sudo rm -rf ${ROOT_TAR}
}

sudo rm -rf ${BOOT_TAR}
sudo rm -rf ${ROOT_TAR}

echo "Creating loop device"
sudo losetup -a | grep "${IMAGE_FILE}" | awk -F: '{ print $1 }' | xargs -r sudo losetup -d
sudo losetup -fP ${IMAGE_FILE}
LOOPDEV=$(sudo losetup -a | grep "${IMAGE_FILE}" | awk -F: '{ print $1 }')

echo "Using ${LOOPDEV} device"

echo "Creating temp folders"
sudo rm -rf tmpboot
sudo rm -rf tmproot

mkdir -p tmpboot
mkdir -p tmproot

echo "Mounting partitions"
sudo mount ${LOOPDEV}p1 ./tmpboot
sudo mount ${LOOPDEV}p2 ./tmproot

echo "Creating tar archives for partitions"
sudo tar cf ${BOOT_TAR} -C ./tmpboot --numeric-owner --no-ignore-command-error .
sudo tar cf ${ROOT_TAR} -C ./tmproot --numeric-owner --no-ignore-command-error .

cleanup
echo "tar_partitions.sh success"
