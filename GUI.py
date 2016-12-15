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


@app.route('/aws', methods=['GET','POST'])
def aws():
    if request.method == 'POST':
        access_key = request.form['access_key']
        secret_key = request.form['secret_key']
        region = request.form['region']
        # check login
        try:
            client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,
                                  region_name=region)
            region_list = client.describe_regions()
            return render_template('aws_ec2.html')
        except botocore.exceptions.ClientError as e:
            return render_template('denide.html')
    else:
        return render_template('aws.html')

@app.route('/aws_ec2')
def aws_ec2():
    return render_template('aws_ec2.html')

if __name__ == '__main__':
    app.run()
