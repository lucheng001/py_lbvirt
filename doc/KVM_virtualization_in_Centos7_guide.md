# Centos7_X64 virtualization deployment and admin guide
**All operations executed by root**

## setup KVM
1. preparing envirment 
	1.1 hardware
    minimal requirement 
   * 2G RAM

   * 6G Disk Space

	1.2 virtualization technology
    enable virtualization technology in BIOS or vcpu
    check wether support
    > grep -E 'svm|vmx' /proc/cpuinfo

2. install kvm and libvirt packages
install
> yum install qemu-kvm libvirt libvirt-python libguestfs-tools virt-install

enable libvirtd service
> systemctl enable libvirtd && systemctl start libvirtd

3. add a bridge to allow vm accessed by outside
使用brctl命令创建网桥:[参见Network Bridge ArchWiki](https://wiki.archlinux.org/index.php/Network_bridge_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87))
	3.1 add bridge
	> brctl addbr br0
	
	3.2 add interface to br0
	> brctl addif br0 ens33
	
	3.3 config ens33 and br0
	ens33 configure file
	```
	# /etc/sysconfig/network-scripts/ifcfg-ens33
	TYPE=Ethernet
	PROXY_METHOD=none
	BROWSER_ONLY=no
	BOOTPROTO=dhcp
	DEFROUTE=yes
	IPV4_FAILURE_FATAL=no
	IPV6INIT=yes
	IPV6_AUTOCONF=yes
	IPV6_DEFROUTE=yes
	IPV6_FAILURE_FATAL=no
	IPV6_ADDR_GEN_MODE=stable-privacy
	NAME=ens33
	UUID=9e3da4cd-54f7-4a7d-877d-54a8518e8f4c
	DEVICE=ens33
	ONBOOT=yes
	BRIDGE=br0    # add ens33 to br0
	```
	br0 configure file
	```
	# /etc/sysconfig/network-scripts/ifcfg-br0
	DEVICE="br0"
	BOOTPROTO=dhcp
	IPV6INIT=yes
	IPV6_AUTOCONF=yes
	ONBOOT=yes
	TYPE=Bridge
	DELAY=0
	IPADDR=10.66.117.2
	NETMASK=255.255.0.0
	GATEWAY=10.66.255.254
	DNS1=192.168.1.1
	DNS2=119.6.6.6
	```
	
## Work With Virtual Machines
1. create virtual machine
use virt-install command to install virtual machine
if wanna connect to guest agent can use virsh console like that
* install with --extra-args
```
virt-install --name Centos --memory 512 --vcpus 1 --disk /opt/vm_img/Centos7.img --location /opt/iso/CentOS-7-x86_64-Minimal-1804.iso --graphics vnc,listen=0.0.0.0 --noautoconsole --extra-args="console=tty0 console=ttys0,115200"
```
* after vnc connect to guest agent and finished system install enalbe virsh in guest agent
> systemctl start serial-getty@ttyS0
> systemctl enable serial-getty@ttyS0

[reference](https://ravada.readthedocs.io/en/latest/docs/config_console.html)
2. clone virtual machine
there are two type of virtual machine clone
	* clone from a machine
	* clone from a templates

	2.1 preparing virtual machine for clone
	remove network configure
	> rm -f /etc/udev/rules.d/70-persistent-net.rules
	
	remove network interface configure
	remove such lines in /etc/sysconfig/network-scripts/ifcfg-eth[x]
	* HWADDR
	* (all configure with static ip suce as ipaddr netmask and so on)
	
	enable dhcp
	
	remove register details
	> rm /etc/sysconfig/rhn/systemid
	
	remove ssh key
	
	2.2 clone machine
	```
	virt-clone --original Centos --name Centos_clone --file /opt/vm_img/Centos7_bak.img
	```
	
3. snapshot
	3.1 take a snapshot
	> virsh snapshot-create-as --domain Centos --name snapshot_centos_base
	
	3.2 show snapshot list
	> virsh snapshot-list Centos
	
	3.3 delete snapshot
	> virsh snapshot-create-as --domain Centos --name snapshot_centos_base
	
	3.4 snapshot info
	> virsh snapshot-info Centos --current
	
	3.5 restore kvm snapshot
	> virsh snapshot-revert Centos snapshot_centos_base

4. network configuration
there are serveral type of network support for virtual machine
* NAT(Network Address Translation)
* bridge networks
* directly allocated physical devices using PCI
* directly allocated virtual functions using PCIe SR-IOV

show host configure
configure file path in (/etc/libvirt/qemu/networks/*.xml)
> virsh net-list --all

auto start default network
> virsh net-autostart default

start the default network
> virsh net-start default

5. enhancing virtualization with qemu guest agent and spice agent
agent can prove more function for virsh command
	5.1 set up communication between virtual mchine and host
	* set up when guest agent is poweroff
	**host**
	> virsh shutdown Centos
	> virsh edit Centos
	edit like that
	```
	<channel type='unix'>
		<target type='virtio' name='org.qemu.guest_agent.0'/>
	</channel>
	```
	**install qemu on guest agent**
	> virsh start Centos
	> yum install qemu-guest-agent
	> systemctl start qemu-guest-agent
	> systemctl enable qemu-guest-agent
	
	* set up on runnning guest agent
	**host**
	create an xml file agent.xml
	```
	<channel type='unix'>
		<target type='virtio' name='org.qemu.guest_agent.0'/>
	</channel>
	```
	> virsh attach-device Centos agent.xml
	
	**install qemu agent on guest agent**
	> yum install qemu-guest-agent
	> systemctl start qemu-guest-agent
	> systemctl enable qemu-guest-agent
	
	5.2 using the qemu guest agent with libvirt
	* virsh shutdown --mode=agent
	* virsh snapshot-create
	* virsh domfsfreeze / virsh domfsthaw
	* virsh domtime
	* virsh setvcpus --guest
	* virsh domifaddr --source agent # Queries the guest operating system's IP address via
the guest agent.
	* virsh domfsinfo # Shows a list of mounted filesystems within the running guest
	* virsh set-user-password  # Sets the password for a user account in the guest.

## adminstration
1. storage pools
Storage pools are divided into storage volumes either by the storage
administrator or the system administrator, and the volumes are then assigned to guest virtual machines
as block devices.
eg: you can set a shared disk space to store all the guest virtual mchines' data.
there two type of storage pools, the default storage pool is in the /var/lib/libvirt/images/
* **localstorage pools** not support live migration.
* **networked (shared) storage pools** networked storage pools include storage devices shared over a network using standard protocols. supported protocols for networked storage pools include:
  * Fibre Channel-based LUNs
  * iSCSI
  * NFS
  * GFS2
  * SCSI RDMA

	1.1 NFS storage pool
  	1.1.1 disk-based storage pools
  	*WARING: guests should not be given write access to whole disks or block devices.*
  1. create a GPT disk label on the disk
  		this disk must be relabled with a GUID Partition Table disk label. GPT disk labels allow for creating a large numbers of partitions, up to 128 partitions, on each device.
  		
  ```
  [root@localhost dev]# parted /dev/sdb
  GNU Parted 3.1
  Using /dev/sdb
  Welcome to GNU Parted! Type 'help' to view a list of commands.
  (parted) mklabel                                             
  New disk label type? gpt                                     
  (parted) quit
  Information: You may need to update /etc/fstab.
  ```

  2. create the storage pool configuration file

  ```
  <pool type='disk'>
    <name>image_disk</name>
    <source>    
      <device path='/dev/sdb'/>
      <format type='gpt'/>
    </source>
    <target>
      <path>/dev</path>
    </target>
  </pool>
  ```

  3. define the device
  > virsh pool-define image_disk.xml

  4. start the device and trun on autostart
  > virsh pool-start image_disk
  > virsh pool-autostart image_disk

  5. check the storeage pool
  > virsh pool-list --all
  > virsh pool-info image_disk

  6. rm the configure file

    1.1.2 deleting a storage pool using virsh
	> virsh pool-destroy image_disk
	> virsh pool-undefine image_disk

	1.1.2 partition-based storage pools
	1.1.3 directory-based storage pools

2. using QEMU-IMG
2.1 create a image
> qemu-img create [-f format] [-o options] filename [size]

2.2 display image info
> qemu-img info [-f format] filename

...

***
3. **remote management of guests**
  **important**
  how to manage your guests remotely
  3.1 set ssh 
  systemctl start sshd
  connect to remote guest
  > virsh -c qemu+ssh://root@10.66.43.141/system

  3.2 set ssl
  [SSL SETUP reference](https://wiki.libvirt.org/page/TLSSetup)
  **install gnutls-utils**
  > yum install gnutls-utils

  **generate a private key**
  > certtool --generate-privkey > cakey.pem

  **create a signature file(self signed) called ca.info**
  cn is the name of your organization
  ```
  cn = LC_Centos_KVM
  ca
  cert_signing_key
  ```

  **generate the self-signed key**
  > certtool --generate-self-signed --load-privkey cakey.pem --template ca.info --outfile cacert.pem

  after this now just remove the ca.info file, and after this will genrate a file named cacert.pem, this file is the public key. the loaded file cakey.pem is the private key.
**install the cacert.pem CA certificate file on all clients and servers in the /etc/pki/CA/cacert.pem directoru to let them know that the certificate issued by your CA can be trusted.**
to view the contents of this file just run
> certtool -i --inputfile cacert.pem

4. **managing guest virtual machines with virsh**
**important**

***






















