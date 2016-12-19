from flask import Flask

# import templates

from flask import render_template, request
import boto3
import botocore
from botocore import exceptions


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('aws.html')

access_key = ''
secret_key = ''
region = ''
ami_id = 'ami-cdbdd7a2'
userdata = """#Cloud-config

runcmd:
 - mkdir /app
 - touch /app/mukul.txt

packages:
 - httpd
"""
@app.route('/aws', methods=['GET','POST'])
def aws():
    if request.method == 'POST':
        global access_key, secret_key, region
        access_key = request.form['access_key']
        secret_key = request.form['secret_key']
        region = request.form['region']

        # check login
        try:
            client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
                                  region_name=region)
            region_list = client.describe_regions()
            return render_template('aws_home.html')
        except botocore.exceptions.ClientError as e:
            return render_template('denide.html')
    else:
        return render_template('aws.html')


@app.route('/aws_ec2', methods=['GET','POST'])
def aws_ec2():
    if request.method == 'POST':
        server_type = request.form['server_type']
        environment = request.form['environment']
        key_name = request.form['key_name']
        security_group = request.form['security_group']
        # No use if security group provided.
        subnet_id = request.form['subnet_id']
        instance_type = request.form['instance_type']
        instance_count = int(request.form['instance_count'])
        ec2 = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
        instances = ec2.create_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=instance_count,
            KeyName=key_name,
            SecurityGroups=[
                security_group,
            ],
            UserData=userdata,
            InstanceType=instance_type
        )
        mytag = [{
            'Key': 'Name',
            'Value': environment + '_' + server_type
        }]
        for instance in instances:
            ec2.create_tags(
                Resources=[
                    instance.id,
                ],
                Tags=mytag
            )
        return render_template('index.html', aws_ec2=environment)
    else:
        return render_template('aws_ec2.html')

if __name__ == '__main__':
    app.run()
