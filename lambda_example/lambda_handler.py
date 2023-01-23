import sys

from ghostbuster.cli import cli


def lambda_handler(event, context):
    # sys.argv = ['ghostbuster', 'scan', 'aws', '--roles', 'roles.csv', '--regions', 'us-east-1' '--skipascii']
    org_lookup_account_id = '111222333444'  # TODO change me!
    org_lookup_role_arn = f'arn:aws:iam::{org_lookup_account_id}:role/ta-application-security-prd-ghostbuster-org-role'
    sys.argv = ['ghostbuster', 'scan', 'aws', '--autoroles', org_lookup_role_arn, '--regions', 'us-east-1' '--skipascii']
    cli()
    return {
        'statusCode': 200,
        'body': f'Gracefully finished running {" ".join(sys.argv)}'
    }
