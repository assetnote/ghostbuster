import sys

from ghostbuster.cli import cli


def lambda_handler(event, context):
    # sys.argv = ['ghostbuster', 'scan', 'aws', '--roles', 'roles.csv', '--regions', 'us-east-1' '--skipascii']

    org_lookup_role_arn = 'arn:aws:iam::474234877840:role/ta-application-security-prd-ghostbuster-org-role'
    sys.argv = ['ghostbuster', 'scan', 'aws', '--autoroles', org_lookup_role_arn, '--regions', 'us-east-1', '--skipascii']
    cli()
    return {
        'statusCode': 200,
        'body': f'Gracefully finished running {" ".join(sys.argv)}'
    }
