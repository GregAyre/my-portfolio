import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    sns = boto3.resource('sns')

    portfolio_bucket = s3.Bucket('portfolio.fhircloud.com')
    build_bucket = s3.Bucket('portfoliobuild.fhircloud.com')

    topic = sns.Topic('arn:aws:sns:us-east-1:118738352244:deployPortfolioTopic')

    try:
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully")
    except:
        topic.publish(Subject="Portfolio Deploymnet Failed", Message="The Portfolio code was NOT deployed successfully")
        raise

    print 'Job Complete'
    return 'Hello from Lambda'
