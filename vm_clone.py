from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
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

# Function to clone the VM template to a new template
def clone_vm_template(si, template_name, new_template_name, datacenter_name, vm_folder_name, datastore_name, cluster_name):
    content = si.RetrieveContent()
    
    # Get datacenter, folder, datastore, and cluster
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)
    vm_folder = get_obj(content, [vim.Folder], vm_folder_name)
    datastore = get_obj(content, [vim.Datastore], datastore_name)
    cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name)

    # Get the template to clone
    template = get_obj(content, [vim.VirtualMachine], template_name)
    
    # Set the relocation spec
    reloc_spec = vim.vm.RelocateSpec()
    reloc_spec.datastore = datastore
    reloc_spec.pool = cluster.resourcePool

    # Set the clone specification
    clone_spec = vim.vm.CloneSpec()
    clone_spec.location = reloc_spec
    clone_spec.powerOn = False
    clone_spec.template = True  # Important: This marks the new VM as a template

    # Clone the VM template
    task = template.Clone(folder=vm_folder, name=new_template_name, spec=clone_spec)
    
    # Wait for the task to complete
    while task.info.state == vim.TaskInfo.State.running:
        pass

    if task.info.state == vim.TaskInfo.State.success:
        print(f"Template '{new_template_name}' cloned successfully from template '{template_name}'")
    else:
        print(f"Failed to clone template: {task.info.error}")

def main():
    vcenter = 'your_vcenter_server'
    user = 'your_username'
    password = 'your_password'
    template_name = 'your_template_name'
    new_template_name = 'new_template_name'
    datacenter_name = 'your_datacenter_name'
    vm_folder_name = 'your_vm_folder_name'
    datastore_name = 'your_datastore_name'
    cluster_name = 'your_cluster_name'

    si = connect_to_vcenter(vcenter, user, password)
    try:
        clone_vm_template(si, template_name, new_template_name, datacenter_name, vm_folder_name, datastore_name, cluster_name)
    finally:
        Disconnect(si)

if __name__ == "__main__":
    main()
