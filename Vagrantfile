Vagrant.configure('2') do |config|
  require 'json'

  opts = {
    'datafile' => '.vagrant.json',
    'hostname' => nil,
    'playbook' => '.env/ansible/main.yml',
    'vm_box' => 'centos-6.6-x64',
    'vm_box_url' => 'http://dl.mway.co/d/vagrant/boxes/centos-6.6-x64.box',
    'vm_cpus' => 1,
    'vm_ip' => '10.0.100.100',
    'vm_memory' => 1024,
    'vm_name' => nil,
    'vm_nat_dns' => true,
    'vm_network' => 'private_network',
  }

  opts = opts.merge(JSON.load(File.read(opts['datafile']))) if opts['datafile'] && File.exist?(opts['datafile'])
  opts['vm_name'] ||= opts['hostname']

  config.vm.hostname = opts['hostname']
  config.vm.provision :ansible, playbook: opts['playbook'], raw_arguments: Shellwords.shellsplit(ENV['ANSIBLE_ARGS'] || '')
  config.vm.define opts['vm_name'] do |guest|
    guest.vm.box = opts['vm_box']
    guest.vm.box_url = opts['vm_box_url']
    guest.vm.provider :virtualbox do |vb, override|
      vb.name = config.vm.hostname
      vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on'] if opts['vm_nat_dns']
      vb.customize ['modifyvm', :id, '--natdnsproxy1', 'on'] if opts['vm_nat_dns']
      vb.customize ['modifyvm', :id, '--memory', opts['vm_memory']]
      vb.customize ['modifyvm', :id, '--cpus', opts['vm_cpus']]
      override.vm.network opts['vm_network'], ip: opts['vm_ip']
    end
  end
end
