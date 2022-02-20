#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This CLI tool can be used to scan for dangling elastic IPs in your AWS accounts by correlating data
betwen Route53 records and Elastic IPs / IPs in your AWS account.

.. currentmodule:: ghostbuster.scan
.. moduleauthor:: shubham_shah <sshah@assetnote.io>
"""
import csv
import datetime
import sys
import requests
import click
from .__init__ import Info, pass_info
import boto3
import base64
import CloudFlare
import awsipranges
from slack_sdk.webhook import WebhookClient


@click.group(
    help="Commands that help you scan your AWS account for dangling elastic IPs"
)
@click.pass_context
def cli(ctx: click.Context):
    """CLI handler for scanning actions"""
    pass

# ascii art

logo_b64 = "G1swbSAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAbWzMxbeKWhBtbMW3iloQbWzA7MzFt4paE4paEG1sxbeKWhOKWhOKWhOKWhBtbMG0NCiAgICAgIBtbMW3iloQbWzMybeKWhBtbMzdt4paEG1swbSAgICAbWzE7MzI7NDJt4paAG1szN23iloAbWzQwbeKWhBtbMG0gIBtbMTszMm3iloQbWzM3OzQybeKWgBtbMzJt4paAG1swbSAgICAgICAgICAgICAgG1sxOzMybeKWhOKWhOKWhBtbMzc7NDJt4paAG1szMm3iloAbWzQwbeKWiBtbMG0gIBtbMTszMjs0Mm3iloAbWzM3beKWgBtbMzJt4paEG1szN23iloAbWzBtICAgIBtbMTs0Mm3iloAbWzMyOzQwbeKWiBtbMG0gICAgIBtbMzFt4paEG1sxOzQxbeKWhBtbNDBt4paI4paIG1swOzMxbeKWiOKWgOKWgOKWgOKWiBtbMTs0MW3iloTiloDiloAbWzQwbeKWiOKWhBtbMG0NCiAgIBtbMTszMm3iloQbWzQybeKWgOKWgBtbMDszMm3ilojiloDilogbWzE7NDJt4paAG1szN23iloAbWzMyOzQwbeKWhBtbMG0gG1szMm3ilogbWzE7Mzc7NDJt4paEG1szMjs0MG3ilogbWzBtICAbWzE7MzJt4paIG1swOzMybeKWiBtbMzdtICAgIBtbMzJt4paEG1sxOzM3OzQybeKWgBtbMDszMm3ilogbWzE7Mzc7NDJt4paAG1szMm3iloAbWzM3OzQwbeKWhBtbMG0gICAgG1sxOzMybeKWiBtbMDszMm3ilojilogbWzE7NDJt4paEG1swOzMybeKWiBtbMTs0Mm3iloAbWzA7MzJt4paIG1sxOzM3OzQybeKWgBtbMG0gG1sxOzMyOzQybeKWhBtbMDszMm3ilojiloDilogbWzE7NDJt4paA4paA4paA4paAG1swOzMybeKWiBtbMTs0Mm3iloQbWzBtICAgG1szMW3iloQbWzE7NDFt4paAG1s0M23iloDiloAbWzMzOzQxbeKWhBtbNDBt4paE4paEG1swbSAbWzE7MzNt4paE4paE4paE4paEG1swOzMxbeKWhBtbMTs0MW3iloTiloTiloAbWzQwbeKWiOKWhBtbMG0NCiAgIBtbMTszMm3ilogbWzA7MzJt4paI4paAG1szN20gIBtbMTszMm3iloAbWzQybeKWhOKWhBtbMDszMm3ilogbWzM3bSAbWzMybeKWgOKWiBtbMW3ilogbWzBtICAbWzE7MzI7NDJt4paAG1s0MG3ilpEbWzBtICAgG1sxOzMybeKWiBtbMDszMm3ilojiloAbWzFt4paIG1s0Mm3iloQbWzA7MzJt4paA4paIG1sxOzQybeKWgBtbMG0gIBtbMTszMm3ilogbWzA7MzJt4paIG1sxbeKWkRtbMDszMm3iloDiloQbWzE7Mzdt4paEG1swbSAbWzE7MzJt4paIG1swOzMybeKWiBtbMzdtICAbWzE7MzJt4paAG1swbSAbWzE7MzI7NDJt4paEG1swOzMybeKWiBtbMTszNzs0Mm3iloQbWzMyOzQwbeKWgOKWgBtbMG0gG1sxOzMybeKWgBtbMG0gIBtbMzFt4paI4paIG1sxOzQxbeKWhBtbMDszM23ilojilojilojilogbWzFt4paIG1swbSAbWzMzbeKWiOKWiBtbMTszMTs0M23iloQbWzQwbeKWiBtbMDszMW3ilogbWzMzOzQxbeKWhBtbMTs0M23iloAbWzQxbeKWhBtbMzFt4paEG1s0MG3ilojilogbWzBtDQogIBtbMTszMm3iloQbWzQybeKWgBtbMDszMm3ilogbWzM3bSAgICAgIBtbMzJt4paAG1szN20gIBtbMTszMjs0Mm3iloQbWzA7MzJt4paIG1sxOzQybeKWgOKWgBtbMDszMm3ilogbWzE7NDJt4paEG1swbSAgIBtbMTszMm3ilogbWzM3OzQybeKWhBtbMG0gIBtbMTszMm3iloAbWzBtICAbWzE7MzI7NDJt4paAG1swbSAgIBtbMzJt4paIG1sxbeKWkRtbMDszMm3iloQbWzFt4paE4paEG1swbSAgG1sxOzMybeKWiBtbMG0gICAgG1sxOzMybeKWiBtbMDszMm3ilogbWzE7Mzc7NDJt4paAG1swbSAgICAgG1szMW3ilojilpEbWzFt4paIG1swbSAgG1szM23ilogbWzFt4paIG1swbSAgG1sxOzMxbeKWhBtbMDszMzs0MW3iloAbWzMxOzQwbeKWiBtbMTs0MW3iloAbWzA7MzFt4paAG1szN20gIBtbMzNt4paIG1sxbeKWiBtbMDszMW3ilojilogbWzFt4paIG1swbQ0KICAbWzE7MzJt4paIG1swOzMybeKWiBtbMW3ilpEbWzBtICAbWzE7MzJt4paE4paE4paEG1szN23iloQbWzBtICAgG1sxOzMybeKWiBtbMDszMm3ilojiloAbWzM3bSAbWzMybeKWiBtbMW3ilogbWzBtICAgG1sxOzMybeKWiBtbMDszMm3ilogbWzM3bSAgICAbWzMybeKWiBtbMW3ilogbWzBtICAgIBtbMzJt4paA4paA4paA4paIG1sxOzQybeKWgBtbMG0gICAgIBtbMzJt4paEG1sxOzM3OzQybeKWhBtbMDszMm3ilogbWzFt4paIG1swbSAgICAgG1sxOzMxbeKWiBtbNDFt4paEG1s0MG3ilogbWzBtICAbWzMzbeKWiBtbMW3ilogbWzBtIBtbMzFt4paEG1sxOzQxbeKWgBtbMDszMW3ilogbWzE7NDNt4paAG1swbSAgIBtbMzNt4paE4paIG1sxOzQxbeKWgBtbMzFt4paEG1swOzMxbeKWkRtbMW3ilogbWzBtDQogIBtbMTszMm3ilogbWzA7MzJt4paIG1sxOzM3OzQybeKWgBtbMG0gIBtbMTszMm3iloAbWzA7MzJt4paI4paIG1sxbeKWiBtbMG0gIBtbMTszMm3iloQbWzQybeKWgBtbMDszMm3ilpEbWzM3bSAgG1szMm3ilogbWzFt4paIG1swbSAgICAbWzE7MzI7NDJt4paEG1swOzMybeKWiOKWhBtbMzdtIBtbMzJt4paEG1sxbeKWiBtbMG0gICAbWzMybeKWhBtbMW3iloQbWzBtICAgIBtbMzJt4paIG1szN20gICAgIBtbMTszMm3ilogbWzA7MzJt4paIG1sxbeKWkeKWiBtbMG0gICAgIBtbMzFt4paIG1sxbeKWiBtbNDFt4paAG1swbSAgG1szM23ilogbWzE7MzE7NDNt4paEG1s0MG3ilogbWzQxbeKWgBtbMDszMW3iloAbWzMzbeKWiOKWiBtbMTs0M23iloDiloDiloAbWzA7MzNt4paIG1szN20gG1szMW3ilojilogbWzFt4paIG1swbQ0KICAbWzE7MzJt4paAG1s0Mm3iloQbWzA7MzJt4paIG1sxbeKWhOKWhBtbMDszMm3iloTilpHilojilogbWzE7Mzc7NDJt4paAG1swbSAbWzE7MzJt4paA4paI4paAG1swbSAgG1szMm3ilpHilogbWzE7Mzc7NDJt4paAG1swbSAgIBtbMzJt4paEG1sxbeKWgBtbNDJt4paEG1swOzMybeKWiOKWgBtbMW3iloAbWzBtICAgG1szMm3iloDilogbWzFt4paRG1swOzMybeKWhBtbMTszNzs0Mm3iloAbWzA7MzJt4paIG1sxbeKWiBtbMG0gICAgICAbWzE7MzI7NDJt4paEG1swOzMybeKWiBtbMzdtIBtbMW3iloQbWzBtICAgIBtbMzFt4paR4paIG1sxOzQxbeKWgBtbNDBt4paE4paEG1swOzMxbeKWiBtbMTs0MW3iloAbWzA7MzFt4paIG1szN20gIBtbMzNt4paIG1sxOzQzbeKWhBtbMG0gICAgG1szMW3ilogbWzFt4paI4paAG1swbQ0KIBtbMzJt4paIG1szN20gIBtbMTszMjs0Mm3iloQbWzM3beKWgBtbMzI7NDBt4paIG1swOzMybeKWgBtbMW3iloAbWzQybeKWhBtbMzdt4paEG1szMm3iloQbWzBtICAbWzMybeKWhBtbMzdtICAbWzMybeKWiBtbMTszNzs0Mm3iloQbWzA7MzJt4paIG1sxbeKWiBtbMG0gICAbWzE7MzJt4paAG1swbSAgG1szMm3ilogbWzFt4paEG1swbSAgIBtbMTszMjs0Mm3iloAbWzBtIBtbMzJt4paA4paIG1sxOzQybeKWhOKWhBtbNDBt4paAG1szN23iloAbWzBtICAgICAgG1sxOzMybeKWiBtbMDszMm3ilogbWzM3bSAbWzMybeKWgBtbMzdtICAgICAbWzMxbeKWgOKWkRtbMW3ilogbWzQxbeKWhBtbMDszMW3ilogbWzE7NDFt4paAG1szMzs0M23iloAbWzQwbeKWiBtbMG0gG1szM23ilogbWzFt4paIG1swbSAbWzMxbeKWhBtbMTs0MW3iloQbWzA7MzFt4paIG1sxOzQxbeKWhBtbNDBt4paAG1swbQ0KICAgIBtbMTszMm3iloAbWzQybeKWhBtbMG0gICAbWzE7MzJt4paIG1swOzMybeKWiBtbMW3ilogbWzBtICAbWzMybeKWgBtbMzdtICAbWzE7MzI7NDJt4paEG1szN23iloDiloAbWzMyOzQwbeKWiBtbMzdt4paEG1swbSAgIBtbMzJt4paEG1szN20gG1sxOzMybeKWiBtbMDszMm3ilogbWzE7Mzc7NDJt4paAG1swbSAgICAgG1sxbeKWhBtbMG0gICAgICAgICAgIBtbMTszMjs0Mm3iloQbWzBtICAgICAgICAgG1szMW3iloDiloAbWzE7NDFt4paEG1swOzMxbeKWiBtbMTs0MW3iloAbWzQwbeKWiBtbMDszMW3ilojilojilojilogbWzE7NDFt4paE4paEG1s0MG3iloAbWzBtDQogICAgG1szMm3iloQbWzE7Mzdt4paEG1swbSAgICAbWzMybeKWkRtbMW3ilogbWzBtICAgICAbWzE7MzJt4paAG1s0Mm3iloTiloQbWzA7MzJt4paA4paAG1szN20gIBtbMTszMm3iloDiloAbWzBtICAbWzE7MzJt4paAG1swbSAgICAgICAbWzE7MzJt4paEG1swbSAgICAgICAgICAgICAgICAgICAgICAgIBtbMTszMW3iloDiloAbWzA7MzFt4paAG1sxbeKWgOKWgOKWgOKWgBtbMG0NCiAgICAbWzMybeKWgOKWgBtbMzdtICAgIBtbMzJt4paIG1sxbeKWgBtbMG0gICAgIBtbMTszMm3iloQbWzBtIBtbMTszMm3iloQbWzA7MzJt4paEG1sxOzM3beKWhBtbMDszMm3iloQbWzFt4paE4paEG1szN23iloQbWzBtICAbWzE7MzI7NDJt4paA4paAG1szN23iloQbWzBtICAgICAgG1szMm3iloTilogbWzE7Mzc7NDJt4paAG1szMjs0MG3ilogbWzA7MzJt4paEG1sxOzM3beKWhBtbMzJt4paEG1swbSAbWzE7MzI7NDJt4paEG1swOzMybeKWiBtbMTszNzs0Mm3iloAbWzA7MzJt4paIG1sxOzM3OzQybeKWgBtbMzJt4paAG1swOzMybeKWiBtbMTs0Mm3iloAbWzQwbeKWiBtbMG0gG1sxOzMybeKWhOKWhOKWhBtbMDszMm3iloTilojilogbWzE7Mzc7NDJt4paAG1swbSAgG1sxOzMybeKWiBtbNDJt4paA4paAG1szN23iloAbWzMybeKWgBtbMzc7NDBt4paEG1swbQ0KICAgICAbWzE7MzI7NDJt4paEG1swbSAgIBtbMzJt4paIG1sxbeKWiBtbMzdt4paEG1swbSAgICAgIBtbMzJt4paEG1sxOzQybeKWgBtbMDszMm3ilojilojiloDiloDilogbWzE7Mzc7NDJt4paAG1szMm3iloAbWzBtIBtbMTszMm3ilogbWzA7MzJt4paI4paIG1szN20gIBtbMzJt4paIG1sxOzQybeKWgBtbMzc7NDBt4paIG1swbSAbWzMybeKWiOKWiBtbMW3ilojilojiloDiloAbWzM3beKWgBtbMG0gG1sxOzMybeKWgBtbNDJt4paEG1swbSAbWzE7MzJt4paIG1swOzMybeKWiOKWiBtbMzdtICAbWzMybeKWgBtbMzdtIBtbMTszMjs0Mm3iloQbWzM3beKWgBtbMDszMm3iloDiloAbWzFt4paA4paA4paIG1swbSAgG1sxOzMybeKWiOKWkRtbMG0gIBtbMzJt4paA4paIG1szN20NCiAgICAbWzE7MzJt4paEG1swbSAgICAbWzMybeKWgBtbMW3ilogbWzBtICAgICAgIBtbMTszMm3iloQbWzBtIBtbMzJt4paIG1sxOzQybeKWgBtbMDszMm3iloTiloTilojilogbWzFt4paAG1swbSAbWzE7MzI7NDJt4paAG1swOzMybeKWiBtbMTszNzs0Mm3iloAbWzBtICAbWzE7MzJt4paAG1swOzMybeKWiOKWiBtbMzdtICAbWzMybeKWgOKWgOKWiBtbMTs0Mm3iloAbWzQwbeKWhBtbMG0gICAgIBtbMTszMm3ilpHilojilogbWzBtICAgG1sxOzMybeKWhBtbNDJt4paAG1swOzMybeKWiOKWiBtbMTs0Mm3iloAbWzQwbeKWiBtbMG0gICAbWzE7MzJt4paEG1swOzMybeKWiOKWiOKWiBtbMTszNzs0Mm3iloAbWzA7MzJt4paI4paIG1szN20NCiAgICAgICAgICAgICAgICAgIBtbMzJt4paAG1szN20gG1szMm3ilogbWzE7NDJt4paEG1swOzMybeKWgBtbMW3iloDilojilpEbWzA7MzJt4paEG1szN20gG1sxOzMybeKWiBtbMDszMm3ilogbWzFt4paRG1swbSAgIBtbMTszMm3ilogbWzA7MzJt4paIG1szN20gICAgIBtbMzJt4paA4paI4paIG1sxOzM3beKWhBtbMG0gICAbWzE7MzJt4paRG1szN23ilogbWzA7MzJt4paI4paEG1szN20gIBtbMTszMjs0Mm3iloDiloQbWzA7MzJt4paIG1sxbeKWiBtbMG0gICAgIBtbMTszMm3ilogbWzM3OzQybeKWhBtbMDszMm3ilojiloQbWzFt4paAG1s0Mm3iloQbWzA7MzJt4paEG1szN20NCiAgICAgICAgICAbWzE7MzJt4paAG1swbSAgICAgG1sxOzMybeKWhBtbNDJt4paEG1swOzMybeKWgBtbMzdtIBtbMzJt4paIG1sxbeKWiBtbMG0gIBtbMTszMm3ilogbWzA7MzJt4paIG1sxOzQybeKWhBtbMG0gIBtbMTszMm3iloAbWzA7MzJt4paIG1sxOzQybeKWgOKWgOKWgBtbMDszMm3ilogbWzE7NDJt4paEG1swbSAbWzE7MzJt4paIG1s0Mm3iloAbWzBtICAgG1sxOzMybeKWkRtbMDszMm3ilogbWzE7NDJt4paAG1s0MG3iloQbWzBtICAbWzE7MzJt4paRG1swOzMybeKWiBtbMTs0Mm3iloQbWzBtICAgG1szMm3ilogbWzE7Mzc7NDJt4paAG1szMjs0MG3ilogbWzM3OzQybeKWhBtbMDszMm3ilojilogbWzE7NDJt4paAG1s0MG3ilogbWzBtIBtbMzJt4paI4paIG1sxbeKWiOKWkRtbMG0gG1sxOzMybeKWgBtbMDszMm3ilogbWzE7Mzc7NDJt4paAG1szMjs0MG3iloQbWzBtDQogICAgICAgICAgG1szMm3iloAbWzM3bSAgICAgG1szMm3ilogbWzFt4paI4paE4paEG1swOzMybeKWiBtbMTs0Mm3iloAbWzA7MzJt4paE4paE4paIG1sxOzQybeKWhBtbNDBt4paIG1swbSAbWzE7NDJt4paAG1swbSAbWzMybeKWgOKWiBtbMTs0Mm3iloQbWzQwbeKWgBtbNDJt4paEG1swOzMybeKWgBtbMzdtIBtbMTszMm3ilogbWzA7MzJt4paIG1sxOzQybeKWgOKWgBtbMDszMm3ilogbWzE7Mzc7NDJt4paEG1swOzMybeKWiOKWiBtbMTszNzs0Mm3iloAbWzBtICAbWzE7MzJt4paIG1s0Mm3iloQbWzBtIBtbMTszMm3iloAbWzBtICAgG1szMm3ilojiloDiloDiloQbWzFt4paAG1swOzMybeKWhBtbMTs0Mm3iloQbWzBtICAbWzE7MzJt4paIG1s0Mm3iloQbWzQwbeKWkRtbMG0gIBtbMTszMm3iloDilogbWzA7MzJt4paIG1sxOzM3beKWgBtbMG0NCiAgICAgICAgICAgICAgICAbWzE7MzI7NDJt4paEG1swOzMybeKWiOKWiBtbMTszNzs0Mm3iloAbWzMybeKWgBtbMzdt4paA4paAG1szMm3iloAbWzM3beKWgBtbMDszMm3ilogbWzM3bSAgICAgG1sxOzMyOzQybeKWhBtbMG0gIBtbMW3iloQbWzBtICAbWzE7MzI7NDJt4paAG1swOzMybeKWiOKWiBtbMTszNzs0Mm3iloAbWzMybeKWgOKWgBtbMDszMm3iloAbWzM3bSAbWzE7MzI7NDJt4paAG1swbSAgG1szMm3iloQbWzM3bSAbWzE7NDJt4paAG1swbSAgICAgG1sxOzQybeKWgBtbMG0gICAbWzE7MzJt4paA4paAG1swbSAbWzE7MzJt4paAG1swbSAbWzE7MzJt4paIG1s0Mm3iloQbWzQwbeKWiBtbMG0gIBtbMTszMm3iloAbWzBtDQogICAgICAgICAgICAgICAgIBtbMTszMm3iloDiloAbWzA7MzJt4paA4paAG1sxbeKWgOKWgOKWgBtbMG0gG1sxOzMybeKWhBtbMG0gICAgIBtbMTszMm3iloQbWzBtICAbWzMybeKWgBtbMzdtICAbWzMybeKWiBtbMzdtIBtbMTszMm3iloAbWzA7MzJt4paIG1sxOzQybeKWhBtbMG0gG1szMm3iloQbWzM3bSAbWzE7MzJt4paAG1swbSAgG1sxOzMybeKWgBtbMG0gICAgICAgICAgICAgICAbWzE7MzJt4paAG1s0Mm3iloQbWzQwbeKWgBtbMG0NCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAbWzMybeKWhBtbMzdtICAbWzE7MzJt4paA4paAG1swbSAbWzE7MzJt4paAG1swbSAgICAgICAgICAgICAgICAgICAgICAbWzE7NDJt4paAG1swbQ0KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAbWzE7MzJt4paAG1swbQ0KDQo="

def send_webhook(slackwebhook, takeovers):
    webhook = WebhookClient(url=slackwebhook)
    from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

    rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)
    webhook.retry_handlers.append(rate_limit_handler)
    for takeover in takeovers:
        payload = "Potential AWS Elastic IP takeover: {} Records: {}".format(
            takeover["name"], takeover["records"]
        )
        _ = webhook.send(text=payload)

def get_cloudflare_records(cloudflaretoken):
    click.echo("Obtaining all zone names from Cloudflare.")
    cf = CloudFlare.CloudFlare(token=cloudflaretoken, raw=True)
    dns_records = []
    # get zone names
    cloudflare_zones = []
    try:
        page_number = 0
        while True:
            page_number += 1
            raw_results = cf.zones.get(
                params={"per_page": 100, "page": page_number}
            )
            zones = raw_results["result"]
            for zone in zones:
                zone_id = zone["id"]
                zone_name = zone["name"]
                cloudflare_zones.append({"name": zone_name, "id": zone_id})
            total_pages = raw_results["result_info"]["total_pages"]
            if page_number == total_pages:
                break
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit("Failed to retreive zones %d %s - api call failed" % (e, e))

    click.echo("Obtaining DNS A records for all zones from Cloudflare.")
    # get dns records for zones
    for zone in cloudflare_zones:
        try:
            page_number = 0
            while True:
                page_number += 1
                raw_results = cf.zones.dns_records.get(
                    zone["id"], params={"per_page": 100, "page": page_number}
                )
                cf_dns_records = raw_results["result"]
                for record in cf_dns_records:
                    if record.get("content"):
                        if record["type"] == "A":
                            dns_records.append(
                                {
                                    "name": record["name"],
                                    "records": [record["content"]],
                                }
                            )
                total_pages = raw_results["result_info"]["total_pages"]
                if page_number == total_pages:
                    break
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit("Failed to retreive DNS records %d %s - api call failed" % (e, e))
    return dns_records

def get_route53_hosted_zones(route53, next_zone=None):
    """Recursively returns a list of hosted zones in Amazon Route 53."""
    if next_zone:
        response = route53.list_hosted_zones_by_name(
            DNSName=next_zone[0], HostedZoneId=next_zone[1]
        )
    else:
        response = route53.list_hosted_zones_by_name()
    hosted_zones = response["HostedZones"]
    # if response is truncated, call function again with next zone name/id
    if response["IsTruncated"]:
        hosted_zones += get_route53_hosted_zones(
            route53, (response["NextDNSName"], response["NextHostedZoneId"])
        )
    return hosted_zones


def get_route53_zone_records(route53, zone_id, next_record=None):
    """Recursively returns a list of records of a hosted zone in Route 53."""
    if next_record:
        response = route53.list_resource_record_sets(
            HostedZoneId=zone_id,
            StartRecordName=next_record[0],
            StartRecordType=next_record[1],
        )
    else:
        response = route53.list_resource_record_sets(HostedZoneId=zone_id)
    zone_records = response["ResourceRecordSets"]
    # if response is truncated, call function again with next record name/id
    if response["IsTruncated"]:
        zone_records += get_route53_zone_records(
            route53, zone_id, (response["NextRecordName"], response["NextRecordType"])
        )
    return zone_records


def get_record_value(record):
    """Return a list of values for a hosted zone record."""
    # test if record's value is Alias or dict of records
    try:
        value = [
            ":".join(
                [
                    "ALIAS",
                    record["AliasTarget"]["HostedZoneId"],
                    record["AliasTarget"]["DNSName"],
                ]
            )
        ]
    except KeyError:
        value = []
        for v in record["ResourceRecords"]:
            value.append(v["Value"])
    return value


def try_record(test, record):
    """Return a value for a record"""
    # test for Key and Type errors
    try:
        value = record[test]
    except KeyError:
        value = ""
    except TypeError:
        value = ""
    return value


@click.option(
    "--regions", default="us-east-1", help="Comma delimited list of regions to run on."
)
@click.option(
    "--exclude", default="", help="Comma delimited list of profile names to exclude."
)
@click.option(
    "--allregions",
    default=False,
    is_flag=True,
    help="Run on all regions.",
)
@click.option(
    "--cloudflaretoken",
    default="",
    help="Pull DNS records from Cloudflare, provide a CF API token.",
)
@click.option(
    "--records",
    required=False,
    type=click.Path(exists=True),
    help="Manually specify DNS records to check against. Ghostbuster will check these IPs after checking retrieved DNS records. See records.csv for an example.",
)
@click.option(
    "--slackwebhook",
    default="",
    help="Specify a Slack webhook URL to send notifications about potential takeovers.",
)
@click.option(
    "--skipascii",
    default=False,
    is_flag=True,
    help="Skip printing the ASCII art when starting up Ghostbuster.",
)
@click.option(
    "--profile",
    default="",
    help="Specify a specific AWS profile to run ghostbuster on.",
)
@cli.command(help="Scan for dangling elastic IPs inside your AWS accounts.")
@pass_info
def aws(
    _: Info,
    regions: str,
    exclude: str,
    allregions: bool,
    cloudflaretoken: str,
    records: str,
    slackwebhook: str,
    skipascii: str,
    profile: str
    ):
    """Scan for dangling elastic IPs inside your AWS accounts."""
    # ascii art
    if not skipascii:
        sys.stdout.write(base64.b64decode(logo_b64).decode('utf-8'))
    session = boto3.Session()
    profiles = session.available_profiles
    if exclude != "":
        exclude_list = exclude.split(",")
        for excluded_profile in exclude_list:
            profiles.remove(excluded_profile)
    if profile != "":
        profiles = [profile]
    dns_records = []
    # collection of records from cloudflare
    if cloudflaretoken != "":
        cf_dns_records = get_cloudflare_records(cloudflaretoken)
        dns_records = dns_records + cf_dns_records
        click.echo("Obtained {0} DNS A records so far.".format(len(dns_records)))

    # collection of records from r53
    for profile in profiles:
        profile_session = boto3.session.Session(profile_name=profile)
        route53 = profile_session.client("route53")
        click.echo(
            "Obtaining Route53 hosted zones for AWS profile: {0}.".format(profile)
        )
        hosted_zones = get_route53_hosted_zones(route53)
        for zone in hosted_zones:
            zone_records = get_route53_zone_records(route53, zone["Id"])
            for record in zone_records:
                if record["Type"] == "A":
                    # we aren't interested in alias records
                    if record.get("AliasTarget"):
                        # skip
                        pass
                    else:
                        a_records = []
                        for r53value in record["ResourceRecords"]:
                            a_records.append(r53value["Value"])
                        r53_obj = {"name": record["Name"], "records": a_records}
                        dns_records.append(r53_obj)

    click.echo("Obtained {0} DNS A records so far.".format(len(dns_records)))

    # collection of IPs
    if allregions:
        ec2 = boto3.client("ec2")
        aws_regions = [
            region["RegionName"] for region in ec2.describe_regions()["Regions"]
        ]
    else:
        aws_regions = regions.split(",")
    elastic_ips = []
    # collect elastic compute addresses / EIPs for all regions
    for region in aws_regions:
        for profile in profiles:
            click.echo(
                "Obtaining EIPs for region: {}, profile: {}".format(region, profile)
            )
            profile_session = boto3.session.Session(profile_name=profile)
            client = profile_session.client("ec2", region_name=region)
            # super annoying, boto3 doesn't have a native paginator class for describe_addresses
            while True:
                addresses_dict = []
                if addresses_dict and "NextToken" in addresses_dict:
                    addresses_dict = client.describe_addresses(
                        NextToken=addresses_dict["NextToken"]
                    )
                else:
                    addresses_dict = client.describe_addresses()
                for eip_dict in addresses_dict["Addresses"]:
                    elastic_ips.append(eip_dict["PublicIp"])
                if "NextToken" not in addresses_dict:
                    break

            click.echo(
                "Obtaining IPs for network interfaces for region: {}, profile: {}".format(
                    region, profile
                )
            )
            nic_paginator = client.get_paginator("describe_network_interfaces")
            for resp in nic_paginator.paginate():
                for interface in resp.get("NetworkInterfaces", []):
                    if interface.get("Association"):
                        nic_public_ip = interface["Association"]["PublicIp"]
                        elastic_ips.append(nic_public_ip)

    unique_ips = list(set(elastic_ips))
    click.echo("Obtained {0} unique elastic IPs from AWS.".format(len(unique_ips)))

    dns_ec2_ips = []
    # find all DNS records that point to EC2 IP addresses
    aws_ip_ranges = awsipranges.get_ranges()
    for record_set in dns_records:
        for record in record_set["records"]:
            aws_metadata = aws_ip_ranges.get(record)
            if aws_metadata:
                for service in aws_metadata.services:
                    if service == "EC2":
                        dns_ec2_ips.append(record_set)
    takeovers = []
    # check to see if any of the record sets we have, we don't own the elastic IPs
    for record_set in dns_ec2_ips:
        for record in record_set["records"]:
            if record not in elastic_ips:
                takeovers.append(record_set)
                click.echo("Takeover possible: {}".format(record_set))

    # check if manually specified A records exist in AWS acc (eips/public ips)
    if records:
        with open(records, "r") as fp:
            csv_reader = csv.DictReader(fp)
            for row in csv_reader:
                aws_metadata = aws_ip_ranges.get(row["record"])
                if aws_metadata:
                    for service in aws_metadata.services:
                        if service == "EC2":
                            if row["record"] not in elastic_ips:
                                takeover_obj = {
                                    "name": row["name"],
                                    "records": [row["record"]],
                                }
                                takeovers.append(takeover_obj)
                                click.echo("Takeover possible: {}".format(takeover_obj))

    # send slack webhooks, with retries incase of 429s
    if slackwebhook != "":
        send_webhook(slackwebhook, takeovers)

    if len(takeovers) == 0:
        click.echo("No takeovers detected! Nice work.")