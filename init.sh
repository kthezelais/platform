#!/bin/bash
# How to run this script?:
# 
#   bash init.sh && python main.py
#

### Installation step
WORKDIR="/var/lib/libvirt/images/.platform"

python clean.py
sudo rm -rf $WORKDIR

sudo mkdir -p $WORKDIR
sudo mkdir -p $WORKDIR/images
sudo mkdir -p $WORKDIR/virtualmachines
sudo chown libvirt-qemu:kvm $WORKDIR
sudo chown libvirt-qemu:kvm $WORKDIR/images
sudo chown libvirt-qemu:kvm $WORKDIR/virtualmachines
sudo chmod -R 775 $WORKDIR
