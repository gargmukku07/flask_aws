
pmasterData = """#Cloud-config

write_files:
 - path: '/tmp/puppet_server.sh'
   owner: root:root
   permission: '0755'
   content: |
      #!/usr/bin/bash
      PUPPET_BASE="/opt/puppetlabs"
      PUPPET_HIERA_FILE="/etc/puppetlabs/puppet/hiera.yaml"
      PUPPET_CONF="/etc/puppetlabs/puppet/puppet.conf"
      RED=`tput setaf 1`
      GREEN=`tput setaf 2`
      RESET=`tput sgr0`
      YELLOW=`tput setaf 3`
      CYAN=`tput setaf 6`
      BLANK=`echo`
      function getOSVersion()
        {
          OUTPUT=$(rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release)| cut -d"." -f1)
          if [ "$OUTPUT" = "" ]; then
             echo "ERROR => Failed to get OS major version"
             exit 1
          fi
          if [ "$OUTPUT" -ge "7" ] && [ "$OUTPUT" -lt "8" ]; then
             OS_TYPE="el-7"
          fi
          if [ ${OUTPUT:0:1} -ge 6  ] && [ "${OUTPUT:0:1}" -lt "7" ]; then
             OS_TYPE="el-6"
          fi
          echo "$BLANK $GREEN"
          echo "Operating System Type => $OS_TYPE"
          echo "$RESET $BLANK"
        }
        function setupRepo()
        {
           PUPPET_REPO="https://yum.puppetlabs.com/puppetlabs-release-pc1-${OS_TYPE}.noarch.rpm"
           VERIFY=$(rpm -qa | grep puppetlabs-release-pc1)
           if [ "$VERIFY" = "" ]; then
              curl -o /tmp/puppetlabs-release-pc1-${OS_TYPE}.noarch.rpm  $PUPPET_REPO --insecure
              rpm -ivh /tmp/puppetlabs-release-pc1-${OS_TYPE}.noarch.rpm
              if [ $? -ne 0 ]; then
                 echo "$BLANK $RED"
                 echo "ERROR => Failed to install $PUPPET_REPO"
                 echo "$RESET $BLANK"
                 exit 1
              fi
              echo "$BLANK $CYAN"
              echo "INFO => puppet repo successfully installed"
              echo "$BLANK $RESET"
           else
              echo "$YELLOW $BLANK"
              echo "PUPPET_REPO => $VERIFY already installed"
              echo "$BLANK $RESET"
           fi
        }
        function installPuppetServer()
        {
           echo "$CYAN $BLANK"
           echo "INFO => Installing puppet server, please wait..."
           echo "$BLANK $RESET"
           yum install -y puppetserver
           if [ $? -ne 0 ]; then
              echo "$RED $BLANK"
              echo "ERROR => Failed to install puppet server"
              echo "$BLANK $RESET"
              exit 1
           fi
           echo "$CYAN $BLANK"
           echo "INFO => puppet server installed successfully"
           echo "$BLANK $RESET"
        }
        function installEncryptHiera()
        {
           gem_exe="$PUPPET_BASE/puppet/bin/gem"
           echo "$CYAN $BLANK"
           echo "INFO => Installing hiera-eyaml package, please wait..."
           echo "$BLANK $RESET"
           $gem_exe install hiera-eyaml
           if [ $? -ne 0 ]; then
             echo "$RED $BLANK"
             echo "ERROR => Failed to install hiera-eyaml package using gem..."
             echo "$BLANK $RESET"
             exit 1
           fi
           puppet_server_exe="$PUPPET_BASE/bin/puppetserver"
           echo "$CYAN $BLANK"
           echo "INFO => Installing hiera-eyaml package using puppetserver, please wait..."
           echo "$BLANK $RESET"
           $puppet_server_exe gem install hiera-eyaml
           if [ $? -ne 0 ]; then
             echo "$RED $BLANK"
             echo "ERROR => Failed to install hiera-eyaml package using puppetserver..."
             echo "$BLANK $RESET"
             exit 1
           fi
           echo "$CYAN $BLANK"
           echo "INFO => hiera-eyaml installed successfully"
           echo "$BLANK $RESET"
           if [ ! -L "/usr/bin/eyaml" ]; then
              echo "$CYAN $BLANK"
              echo "INFO => Creating soft-link /usr/bin/eyaml, please wait..."
              echo "$BLANK $RESET"
              sleep 5
              ln -s $PUPPET_BASE/puppet/bin/eyaml /usr/bin/eyaml
           else
              VERIFY=$(file /usr/bin/eyaml | grep 'broken')
              if [ "$VERIFY" != "" ]; then
                 echo "$RED $BLANK"
                 echo "ERROR => Soft Link /usr/bin/eyaml is broken, please remove it and run again"
                 echo "$BLANK $RESET"
                 exit 1
              fi
           fi
        }
        function updateHieraFile()
        {
           script_file=$(realpath $0)
           script_dir=$(dirname $script_file)
           hiera_root_dir=$(dirname $script_dir)
           hiera_dir="$hiera_root_dir/hieradata"
           keys_dir="$hiera_root_dir/keys"
           hiera_file="$hiera_root_dir/hiera.yaml"
           echo "$GREEN $BLANK"
           echo "Hiera Directory => $hiera_dir"
           echo "Hiera File => $hiera_file"
           echo "$CYAN $BLANK"
           echo "Updating $hiera_file with correct hieradata folder, please wait..."
           echo "$BLANK $RESET"
           sed -i -e "s;.*datadir.*;  :datadir: $hiera_dir;g" $hiera_file
           sed -i -e "s;.*pkcs7_private_key.*;  :pkcs7_private_key: $keys_dir/private_key.pkcs7.pem;g" $hiera_file
           sed -i -e "s;.*pkcs7_public_key.*;  :pkcs7_public_key: $keys_dir/public_key.pkcs7.pem;g" $hiera_file
           if [ -f "$PUPPET_HIERA_FILE" ]; then
              rm -f "$PUPPET_HIERA_FILE"
           fi
           if [ ! -L "$PUPPET_HIERA_FILE" ]; then
              ln -s $hiera_file $PUPPET_HIERA_FILE
           fi
           if [ -f "$PUPPET_CONF" ]; then
              VERIFY=$(cat $PUPPET_CONF | grep autosign)
              if [ "$VERIFY" = "" ]; then
                echo "autosign = $script_dir/autosign" >> $PUPPET_CONF
              else
                sed -i -e "s;.*autosign.*;autosign = $script_dir/autosign;g" $PUPPET_CONF
              fi
           fi
        }
        function restartPuppetService()
        {
           service puppetserver restart
           if [ $? -ne 0 ]; then
             echo "$RED $BLANK"
             echo "ERROR => Failed to restart puppetserver service..."
             echo "$BLANK $RESET"
             exit 1
           fi
           echo "$YELLOW $BLANK"
           echo "SUCCESS => puppetserver service restarted successfully"
           echo "$BLANK $RESET"
        }

        getOSVersion
        setupRepo
        installPuppetServer
        installEncryptHiera
        updateHieraFile
        restartPuppetService

runcmd:
 - sh /tmp/puppet_server.sh

"""

appData = """#Cloud-config
write_files:
 - path: '/tmp/puppet_agent.sh'
   owner: root:root
   permission: '0755'
   content: |
        #!/usr/bin/bash
        PUPPET_BASE="/opt/puppetlabs"
        PUPPET_CONF="/etc/puppetlabs/puppet/puppet.conf"
        FACTS_DIR="/etc/facter/facts.d"
        RED=`tput setaf 1`
        GREEN=`tput setaf 2`
        RESET=`tput sgr0`
        YELLOW=`tput setaf 3`
        CYAN=`tput setaf 6`
        BLANK=`echo`

        function getOSVersion()
        {
          OUTPUT=$(rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release)| cut -d"." -f1)
          if [ "$OUTPUT" = "" ]; then
             echo "ERROR => Failed to get OS major version"
             exit 1
          fi
          if [ "$OUTPUT" -ge "7" ] && [ "$OUTPUT" -lt "8" ]; then
             OS_TYPE="el-7"
          fi
          if [ ${OUTPUT:0:1} -ge 6  ] && [ "${OUTPUT:0:1}" -lt "7" ]; then
             OS_TYPE="el-6"
          fi
          echo "$BLANK $GREEN"
          echo "Operating System Type => $OS_TYPE"
          echo "$RESET $BLANK"
        }

        function setupRepo()
        {
           PUPPET_REPO="https://yum.puppetlabs.com/puppetlabs-release-pc1-${OS_TYPE}.noarch.rpm"
           VERIFY=$(rpm -qa | grep puppetlabs-release-pc1)
           if [ "$VERIFY" = "" ]; then
              curl -o /tmp/puppetlabs-release-pc1-${OS_TYPE}.noarch.rpm  $PUPPET_REPO --insecure
              rpm -ivh /tmp/puppetlabs-release-pc1-${OS_TYPE}.noarch.rpm
              if [ $? -ne 0 ]; then
                 echo "$BLANK $RED"
                 echo "ERROR => Failed to install $PUPPET_REPO"
                 echo "$RESET $BLANK"
                 exit 1
              fi
              echo "$BLANK $CYAN"
              echo "INFO => puppet repo successfully installed"
              echo "$BLANK $RESET"
           else
              echo "$YELLOW $BLANK"
              echo "PUPPET_REPO => $VERIFY already installed"
              echo "$BLANK $RESET"
           fi
        }

        function readInputValues()
        {
           echo "$GREEN $BLANK"
           echo "*************************************"
           echo "  Puppet Agent Installation Utility"
           echo "*************************************"
           echo "$YELLOW"
           echo -n "Enter Puppet Master[FQDN] => $CYAN"
           read PUPPET_MASTER
           if [ "$PUPPET_MASTER" = "" ]; then
             echo "$RED $BLANK"
             echo "ERROR => Please enter puppet master[FQDN] to continue..."
             echo "$RESET $BLANK"
             exit 1
           fi
           echo "$YELLOW"
           echo -n "Enter The Environment => $CYAN"
           read ENVIRONMENT
           if [ "$ENVIRONMENT" = "" ]; then
             echo "$RED $BLANK"
             echo "ERROR => Please enter <ENVIRONMENT> to continue..."
             echo "$RESET $BLANK"
             exit 1
           fi
           echo "$YELLOW"
           echo -n "Is $CYAN[$ENVIRONMENT]$YELLOW environment added/configured on puppet master[Y/N]?:$CYAN "
           read ANSWER
           if [ "$ANSWER" = "N" ]; then
             echo "$RED $BLANK"
             echo "ERROR => Please add/configure $CYAN[$ENVIRONMENT]$RED environment on puppet master first to continue..."
             echo "$RESET $BLANK"
             exit 1
           fi
           echo "$YELLOW"
           echo "What would you like to setup?"
           echo "[1] Author"
           echo "[2] Publish"
           echo "[3] Standby"
           echo "[4] Webserver"
           echo "[5] Zabbix"
           echo "[6] Exit"
           echo "$BLANK $GREEN"
           echo -n "Enter Option From [1..6]: "
           read OPTIONS
           if [ $OPTIONS -lt 1 ] || [ $OPTIONS -gt 6 ]; then
              echo "$RED $BLANK"
              echo "ERROR => Please select options from [1..6]"
              echo "$RESET $BLANK"
              exit 1
           fi
           case $OPTIONS in
             1)
               ROLE_TYPE="author"
               shift
               ;;
             2)
               ROLE_TYPE="publish"
               shift
               ;;
             3)
               ROLE_TYPE="standby"
               shift
               ;;
             4)
               ROLE_TYPE="webserver"
               shift
               ;;
             5)
               ROLE_TYPE="zabbix"
               shift
               ;;
             6)
               exit 0
               ;;
           esac

        }

        function installPuppetAgent()
        {
           echo "$GREEN $BLANK"
           echo "Installing Puppet Agent, Please Wait..."
           echo "$RESET $BLANK"
           yum install -y puppet
           if [ $? -ne 0 ]; then
              echo "$RED $BLANK"
              echo "ERROR => Failed to install puppet agent"
              echo "$RESET $BLANK"
              exit 1
           fi
           echo "$YELLOW $BLANK"
           echo "SUCCESS => Puppet Agent Successfully Installed"
           echo "$RESET $BLANK"
        }

        function configurePuppet()
        {
           HOST=`hostname`
           CONTENTS="
        [main]
        server = $PUPPET_MASTER
        environment = $ENVIRONMENT
        [agent]
        certname = `echo "${HOST,,}"`
        report = true
        pluginsync = true"

           echo -n "$CONTENTS" >> $PUPPET_CONF
           awk '{if (++dup[$0] == 1) print $0;}' $PUPPET_CONF > /tmp/puppet.conf
           mv /tmp/puppet.conf $PUPPET_CONF
           mkdir -p $FACTS_DIR
           if [ ! -f "$FACTS_DIR/facts.txt" ]; then
              echo "role_type=$ROLE_TYPE" > $FACTS_DIR/facts.txt
              echo "project_env=$ENVIRONMENT" >> $FACTS_DIR/facts.txt
           fi
        }

        function connectToPuppetMaster()
        {
           echo "Adding csr_attribute configuration..."
           if [ -f "/etc/puppetlabs/puppet/csr_attributes.yaml" ]; then
              echo "file present"
            else
              echo "---" > /etc/puppetlabs/puppet/csr_attributes.yaml
              echo "extension_requests:" >> /etc/puppetlabs/puppet/csr_attributes.yaml
              echo "  pp_uuid: d2b039d926eb4864b8941ec0c6fee632" >> /etc/puppetlabs/puppet/csr_attributes.yaml
           fi
        }

        function restartPuppetAgent()
        {
           echo "$GREEN $BLANK"
           echo "Restarting Puppet Agent Service"
           service puppet restart
           if [ $? -ne 0 ]; then
              echo "$RED $BLANK"
              echo "ERROR => Failed to restart puppet agent service"
              echo "$RESET $BLANK"
              exit 1
           fi
           echo "$YELLOW $BLANK"
           echo "SUCCESS => puppet agent service restarted successfully"
           echo "$RESET $BLANK"
        }

        readInputValues
        getOSVersion
        setupRepo
        installPuppetAgent
        configurePuppet
        connectToPuppetMaster
        restartPuppetAgent

runcmd:
 - sh /tmp/puppet_agent.sh

"""

testData = """
cloud-config
#
puppet:
 # Every key present in the conf object will be added to puppet.conf:
 # [name]
 # subkey=value
 #
 # For example the configuration below will have the following section
 # added to puppet.conf:
  [main]
  certname = "%f"
  server = "%f"
  environment = production
  runinterval = 1h
 #
 # The puppmaster ca certificate will be available in
 # /var/lib/puppet/ssl/certs/ca.pem

"""