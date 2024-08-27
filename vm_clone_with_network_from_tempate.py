from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

# Function to connect to vCenter
def connect_to_vcenter(vcenter, user, password):
    context = ssl._create_unverified_context()
    si = SmartConnect(host=vcenter, user=user, pwd=password, sslContext=context)
    return si

# Function to get an object by name
def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

# Function to clone the VM template to a new VM and assign an IP address
def clone_vm_with_ip(si, template_name, vm_name, datacenter_name, vm_folder_name, datastore_name, cluster_name, network_name, ip_address, gateway, subnet_mask, dns_servers):
    content = si.RetrieveContent()
    
    # Get datacenter, folder, datastore, cluster, and network
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)
    vm_folder = get_obj(content, [vim.Folder], vm_folder_name)
    datastore = get_obj(content, [vim.Datastore], datastore_name)
    cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name)
    network = get_obj(content, [vim.Network], network_name)

    # Get the template to clone
    template = get_obj(content, [vim.VirtualMachine], template_name)
    
    # Set the relocation spec
    reloc_spec = vim.vm.RelocateSpec()
    reloc_spec.datastore = datastore
    reloc_spec.pool = cluster.resourcePool

    # Customize the IP settings
    adaptermap = vim.vm.customization.AdapterMapping()
    adaptermap.adapter = vim.vm.customization.IPSettings()
    adaptermap.adapter.ip = vim.vm.customization.FixedIp()
    adaptermap.adapter.ip.ipAddress = ip_address
    adaptermap.adapter.gateway = gateway
    adaptermap.adapter.subnetMask = subnet_mask
    adaptermap.adapter.dnsDomain = ""
    adaptermap.adapter.dnsServerList = dns_servers
    adaptermap.adapter.network = network

    # Create the global IP settings
    globalip = vim.vm.customization.GlobalIPSettings()
    globalip.dnsServerList = dns_servers

    # Create the identity customization spec
    ident = vim.vm.customization.LinuxPrep(domain="local", hostName=vim.vm.customization.FixedName(name=vm_name))

    # Create the customization spec
    custom_spec = vim.vm.customization.Specification()
    custom_spec.nicSettingMap = [adaptermap]
    custom_spec.globalIPSettings = globalip
    custom_spec.identity = ident

    # Set the clone specification
    clone_spec = vim.vm.CloneSpec()
    clone_spec.location = reloc_spec
    clone_spec.powerOn = True
    clone_spec.template = False
    clone_spec.customization = custom_spec

    # Clone the VM
    task = template.Clone(folder=vm_folder, name=vm_name, spec=clone_spec)
    
    # Wait for the task to complete
    while task.info.state == vim.TaskInfo.State.running:
        pass

    if task.info.state == vim.TaskInfo.State.success:
        print(f"VM '{vm_name}' cloned successfully from template '{template_name}' with IP '{ip_address}'")
    else:
        print(f"Failed to clone VM: {task.info.error}")

def main():
    vcenter = 'your_vcenter_server'
    user = 'your_username'
    password = 'your_password'
    template_name = 'your_template_name'
    vm_name = 'new_vm_name'
    datacenter_name = 'your_datacenter_name'
    vm_folder_name = 'your_vm_folder_name'
    datastore_name = 'your_datastore_name'
    cluster_name = 'your_cluster_name'
    network_name = 'your_network_name'
    ip_address = 'your_ip_address'
    gateway = ['your_gateway']
    subnet_mask = 'your_subnet_mask'
    dns_servers = ['your_dns_server_1', 'your_dns_server_2']

    si = connect_to_vcenter(vcenter, user, password)
    try:
        clone_vm_with_ip(si, template_name, vm_name, datacenter_name, vm_folder_name, datastore_name, cluster_name, network_name, ip_address, gateway, subnet_mask, dns_servers)
    finally:
        Disconnect(si)

if __name__ == "__main__":
    main()
