import sys

from ghostbuster.cli import cli


def lambda_handler(event, context):
    # --roles roles.csv
    # sys.argv = ['ghostbuster', 'scan', 'aws', '--roles', 'roles.csv', '--regions', 'us-east-1', '--skipascii']
    # cli()

    # --json --roles roles.csv
    # sys.argv = ['ghostbuster', 'scan', 'aws', '--roles', 'roles.csv', '--regions', 'us-east-1', '--skipascii', '--json']
    # cli()

    # --autoroles org_lookup_role_arn
    org_lookup_role_arn = 'arn:aws:iam::474234877840:role/ta-application-security-prd-ghostbuster-org-role'
    sys.argv = ['ghostbuster', 'scan', 'aws', '--autoroles', org_lookup_role_arn, '--regions', 'us-east-1', '--skipascii']
    cli()
    """ 
        cli completes the task, but then ends with
    
    Error: Runtime exited without providing a reason 
    Runtime.ExitError

    This results in lambda ending with Internal Server Error instead of returning 200 below:
    """
    return {
        'statusCode': 200,
        'body': f'Finished running {" ".join(sys.argv)}'
    }
