from flask import Flask

# import templates

from flask import render_template
import boto3
import botocore

from flask import request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('aws.html')

access_key = ''
secret_key = ''
region = ''


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
        subnet_id = request.form['subnet_id']
        instance_type = request.form['instance_type']
        instance_count = int(request.form['instance_count'])
        ec2 = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
        instance = ec2.create_instances(
            ImageId='ami-cdbdd7a2',
            MinCount=1,
            MaxCount=instance_count,
            KeyName=key_name,
            InstanceType=instance_type
        )
        return render_template('index.html', aws_ec2=environment)
    else:
        return render_template('aws_ec2.html')

if __name__ == '__main__':
    app.run()
