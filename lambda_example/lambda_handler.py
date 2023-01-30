import sys

from ghostbuster.cli import cli


def lambda_handler(event, context):
    # --roles roles.csv
    sys.argv = ['ghostbuster', 'scan', 'aws', '--roles', 'roles.csv', '--regions', 'us-east-1', '--skipascii']
    try:
        cli()
    except Exception as e:
        print(str(e))  # some weird Runtime.Exit error 

    # --json --roles roles.csv
    sys.argv = ['ghostbuster', 'scan', 'aws', '--roles', 'roles.csv', '--regions', 'us-east-1', '--skipascii', '--json']
    try:
        cli()
    except Exception as e:
        print(str(e))

    # --autoroles org_lookup_role_arn
    org_lookup_role_arn = 'arn:aws:iam::474234877840:role/ta-application-security-prd-ghostbuster-org-role'
    sys.argv = ['ghostbuster', 'scan', 'aws', '--autoroles', org_lookup_role_arn, '--regions', 'us-east-1', '--skipascii']
    try:
        cli()
    except Exception as e:
        print(str(e))

    return {
        'statusCode': 200,
        'body': f'Finished running {" ".join(sys.argv)}'
    }
