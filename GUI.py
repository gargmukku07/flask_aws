from flask import Flask, jsonify
# import templates
from flask import render_template, request
import boto3
import botocore
from botocore import exceptions


app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    return render_template('index.html')

access_key = ''
secret_key = ''
region = ''
client = ''
ec2 = ''

ami_id = 'ami-cdbdd7a2'
import data
userdata = data.testData


@app.route('/aws', methods=['GET','POST'])
def aws():
    if request.method == 'POST':
        global access_key, secret_key, region
        access_key = request.form['access_key']
        secret_key = request.form['secret_key']
        region = request.form['region']
        # check login
        try:
            global client
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
        global ec2
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
        return render_template('aws_home.html', aws_ec2=environment)
    else:
        key_pair = [key_pair['KeyName'] for key_pair in client.describe_key_pairs()['KeyPairs']]
        securitygroup = [securitygroup['GroupName'] for securitygroup in client.describe_security_groups()['SecurityGroups']]
#        subnet = [subnet['SubnetId'] for subnet in client.describe_subnets()['Subnets']]
        vpc = [vpc['VpcId'] for vpc in client.describe_vpcs()['Vpcs']]

        return render_template('aws_ec2.html', key_pairs=key_pair, securitygroups=securitygroup, vpcs=vpc)
#        return render_template('test.html', vpcs=vpc)


@app.route('/_parse_data', methods=['GET'])
def parse_data():
    if request.method == "GET":

        # only need the id we grabbed in my case.
        id = request.args.get('a', 0, type=str)
        print id
        response = client.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [
                        id,
                    ]
                }
            ]
        )
        print response

        new_list = [new_list['SubnetId'] for new_list in response['Subnets']]

    return jsonify(new_list)


@app.route('/aws_vpc', methods=['GET','POST'])
def aws_vpc():
    if request.method == 'POST':
        vpc_name=request.form['vpc_name']
        cidr_block=request.form['cidr_block']
        environment = 'dev'

#        ec2 = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
        vpcs = ec2.create_vpc(
            CidrBlock = cidr_block,
            InstanceTenancy = 'default',
            AmazonProvidedIpv6CidrBlock = False
        )
        mytag = [{
            'Key': 'Name',
            'Value': environment + '_' + vpc_name
        }]
        ec2.create_tags(
            Resources=[
                vpcs.id,
            ],
             Tags=mytag
        )

        return render_template('aws_home.html')
    else:
        return render_template('aws_vpc.html')


from aws_vpc import aws_vpc_blueprint
app.register_blueprint(aws_vpc_blueprint)

if __name__ == '__main__':
    app.run()