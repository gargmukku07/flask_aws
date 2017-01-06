import boto3
import botocore
from botocore import exceptions
from flask import Blueprint
from flask import render_template, request

aws_vpc_blueprint = Blueprint('aws_vpc', __name__)


@aws_vpc_blueprint.route('/aws_vpc', methods=['GET','POST'])
def aws_vpc():
    if request.method == 'POST':
        vpc_name = request.form['vpc_name']
        cidr_block = request.form['cidr_block']
        environment = 'dev'
        #ec2 = boto3.resource('ec2', aws_access_key_id=a, aws_secret_access_key=b, region_name=c)
        #vpc = ec2.create_vpc(
        #    CidrBlock=cidr_block,
        #    InstanceTenancy='default',
        #    AmazonProvidedIpv6CidrBlock='False'
        #)
        return render_template('test.html')
    else:
        return render_template('aws_vpc.html')
