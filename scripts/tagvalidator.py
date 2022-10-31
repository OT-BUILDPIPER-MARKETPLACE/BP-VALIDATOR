#!/usr/bin/env python3
from itertools import repeat
import os
import csv
import glob
import argparse
from otfilesystemlibs import yaml_manager
from otawslibs import generate_aws_session
from botocore.exceptions import ClientError
import pandas as pd
from generate_html import generate_html

def _getProperty(property_file_path):

    try:
        yaml_loader = yaml_manager.getYamlLoader()
        parse_yaml = yaml_loader._loadYaml(args.property_file_path)
        return parse_yaml
    except FileNotFoundError:
        print (f"unable to find {property_file_path}. Please mention correct property file path.")
    return None
def _validateEc2Tags(resource, region, valid_tag, output_filepath,case_insensitive, session):
    ec2_client = session.client(resource, region_name=region)
    paginator = ec2_client.get_paginator('describe_instances')
    responses = paginator.paginate()

    tag_checklist = ['Instance Id', 'Region'] + list(valid_tag.keys())

    with open(output_filepath, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(tag_checklist)

        for response in responses:
            for reservation in response['Reservations']:
                resource_tag_info=[reservation['Instances'][0]['InstanceId'],region]

                try:
                    for valid_tag_key in valid_tag.keys():
                        tag_key_found = "✘"
                        for fetch_tag in reservation['Instances'][0]['Tags']:
                            tag_key_found = scanResourceTags(fetch_tag,valid_tag_key,valid_tag,case_insensitive)
                            if tag_key_found == "✔":
                                break
                        resource_tag_info.append(tag_key_found)
                except ClientError:
                    print (f"{reservation['Instances'][0]['InstanceId']} does not have tags....")
                    resource_tag_info.extend(repeat("✘",len(valid_tag.keys())))
                except KeyError:
                    print(f"No Tag found {valid_tag_key} on instance {reservation['Instances'][0]['InstanceId']}")
                    resource_tag_info.extend(repeat("✘",len(valid_tag.keys())))
                except Exception as e:
                    print(e)

                writer.writerow(list(resource_tag_info))

def _validateRDSTags(resource, region, valid_tag, output_filepath,case_insensitive, session):

    rds_client = session.client(resource, region_name=region)
    paginator = rds_client.get_paginator('describe_db_instances')
    responses = paginator.paginate()

    tag_checklist = ['RDS Name', 'Region'] + list(valid_tag.keys())

    with open(output_filepath, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(tag_checklist)

        for databases in responses:
            for db in databases['DBInstances']:
                resource_tag_info=[db['DBInstanceIdentifier'],region]
                try:
                    for valid_tag_key in valid_tag.keys():
                        tag_key_found = "✘"

                        for fetch_tag in db['TagList']:
                            tag_key_found = scanResourceTags(fetch_tag,valid_tag_key,valid_tag,case_insensitive)
                            if tag_key_found == "✔":
                                break
                        resource_tag_info.append(tag_key_found)

                except ClientError:
                    print (f"{db['DBInstanceIdentifier']} does not have tags....")
                    resource_tag_info.extend(repeat("✘",len(valid_tag.keys())))
                except KeyError:
                    print(f"No Tag found {valid_tag_key} on db {db['DBInstanceIdentifier']}")
                except Exception as e:
                    print(e)

                writer.writerow(list(resource_tag_info))


def _validateDynamoDBTags(resource, region, valid_tag, output_filepath,case_insensitive, session):

    dynamodb_client = session.client(resource, region_name=region)

    tag_checklist = ['Table Name', 'Region'] + list(valid_tag.keys())

    tables = dynamodb_client.list_tables()
    with open(output_filepath, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(tag_checklist)

        for table in tables['TableNames']:
            table_arn = dynamodb_client.describe_table(
                                        TableName=table
                                    )['Table']['TableArn']
            table_tags = dynamodb_client.list_tags_of_resource(
                                    ResourceArn=table_arn
                                )['Tags']
            resource_tag_info=[table,region]
            try:
                for valid_tag_key in valid_tag.keys():
                    tag_key_found = "✘"

                    for fetch_tag in table_tags:
                        tag_key_found = scanResourceTags(fetch_tag,valid_tag_key,valid_tag,case_insensitive)
                        if tag_key_found == "✔":
                            break
                    resource_tag_info.append(tag_key_found)

            except ClientError:
                print (f"{table} does not have tags....")
                resource_tag_info.extend(repeat("✘",len(valid_tag.keys())))
            except KeyError:
                print(f"No Tag found {valid_tag_key} on db {table}")
            except Exception as e:
                print(e)
            writer.writerow(list(resource_tag_info))

def _validateS3Tags(resource, valid_tag, output_filepath,case_insensitive, session):

    s3_client = session.client(resource)
    s3_buckets = s3_client.list_buckets()['Buckets']

    tag_checklist = ['Bucket Name'] + list(valid_tag.keys())

    with open(output_filepath, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(tag_checklist)

        for bucket in s3_buckets:
            resource_tag_info=[bucket['Name']]
            try:
                bucket_tags = s3_client.get_bucket_tagging(Bucket=bucket['Name'])
                for valid_tag_key in valid_tag.keys():
                    tag_key_found = "✘"

                    for fetch_tag in bucket_tags['TagSet']:
                        tag_key_found = scanResourceTags(fetch_tag,valid_tag_key,valid_tag,case_insensitive)
                        if tag_key_found == "✔":
                            break
                    resource_tag_info.append(tag_key_found)
            except ClientError:
                print (f"{bucket['Name']} does not have tags....")
                resource_tag_info.extend(repeat("✘",len(valid_tag.keys())))
            except KeyError:
                print(f"No Tag found {valid_tag_key} on bucket {bucket['Name']}")
                resource_tag_info.extend(repeat("✘",len(valid_tag.keys())))
            except Exception as e:
                print(e)
            writer.writerow(list(resource_tag_info))


def _validateRoute53Tags(resource, valid_tag, output_filepath, case_insensitive, session):
    route53_client = session.client(resource)
    tag_checklist = ['Hosted Zone Name'] + ['Hosted Zone ID'] + list(valid_tag.keys())
    while True:
        hosted_zones = route53_client.list_hosted_zones()
        with open(output_filepath, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(tag_checklist)
            for zone in hosted_zones['HostedZones']:
                zone_id = zone['Id'].split("/")[2]
                resource_tag_info=[zone['Name'], zone_id]
                try:
                    route53_tags = route53_client.list_tags_for_resource(ResourceType='hostedzone',ResourceId=zone_id)['ResourceTagSet']['Tags']
                    for valid_tag_key in valid_tag.keys():
                        tag_key_found = "✘"

                        for fetch_tag in route53_tags:
                            tag_key_found = scanResourceTags(fetch_tag,valid_tag_key,valid_tag,case_insensitive)
                            if tag_key_found == "✔":
                                break

                        resource_tag_info.append(tag_key_found)

                except ClientError:
                    print (f"{zone['Name']} ({zone_id}) does not have tags....")
                    resource_tag_info.extend(repeat("✘",len(valid_tag.keys())))
                except KeyError:
                    print(f"No Tag found {valid_tag_key} on Route53 {zone['Name']}")
                    resource_tag_info.extend(repeat("✘",len(valid_tag.keys())))
                except Exception as e:
                    print(e)
                writer.writerow(list(resource_tag_info))

        if not hosted_zones['IsTruncated']:
            break


def _validatorFactory(properties,services, aws_profile, args):

    case_insensitive = properties["case_insensitive"]
    service_fetched = []

    if aws_profile:
        session = generate_aws_session._create_session(aws_profile)
    else:
        session = generate_aws_session._create_session()

    try:
        for service in services:
            for region in properties['region']:

                if service == "ec2":
                    _validateEc2Tags('ec2', region, properties['services']['ec2'], f'{args.report_path}/ec2_tags_status.csv', case_insensitive, session)
                    service_fetched.append(service)
                elif service == "rds":
                    _validateRDSTags('rds', region, properties['services']['rds'], f'{args.report_path}/rds_tags_status.csv', case_insensitive, session)
                    service_fetched.append(service)

                elif service == "dynamodb":
                    _validateDynamoDBTags('dynamodb', region, properties['services']['dynamodb'], f'{args.report_path}/dynamodb_tags_status.csv', case_insensitive, session)
                    service_fetched.append(service)
                else:
                    break

            if service == "s3":
                _validateS3Tags('s3', properties['services']['s3'], f'{args.report_path}/s3_tags_status.csv', case_insensitive, session)
                service_fetched.append(service)
            elif service == "route53":
                _validateRoute53Tags('route53', properties['services']['route53'], f'{args.report_path}/route53_tags_status.csv', case_insensitive, session)
                service_fetched.append(service)

    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception('AWS Authentication Failure!!!! .. Please mention valid AWS profile in property file or use valid IAM role ').with_traceback(e.__traceback__)
        else:
            raise e

    if not service_fetched:
        print(f"No Valid Services found in property file.. Quiting!!!! ")
        quit()
    else:
        service_fetched = list(set(service_fetched))
        generateHtmlReport(service_fetched, case_insensitive, args)
def generateHtmlReport(service_fetched,case_insensitive, args):

    for service in service_fetched:
    ### Generate HTML report from CSV files
        try:
            generate_html(f"{args.report_path}/{service}_tags_status.csv",f"{args.report_path}/{service}_tags_status.html", case_insensitive, pd)
        except FileNotFoundError:
            print(f"{args.report_path}/{service}_tags_status.csv not present")

def _tagValidator(args):

    properties = _getProperty(args.property_file_path)

    if properties:
        services = properties['services']
        if "aws_profile" in properties:
            aws_profile = properties['aws_profile']
        else:
            aws_profile = None
        _validatorFactory(properties,services, aws_profile, args)

def scanResourceTags(fetch_tag,valid_tag_key,valid_tag,case_insensitive):

    tag_key_found = "✘"

    if valid_tag[valid_tag_key] == ["any"]:
        if case_insensitive and fetch_tag['Key'].upper() == valid_tag_key.upper():
            tag_key_found = "✔"
        if not case_insensitive and fetch_tag['Key'] == valid_tag_key:
            tag_key_found = "✔"

    else:
        if case_insensitive and fetch_tag['Key'].upper() == valid_tag_key.upper() and fetch_tag['Value'].upper() in [x.upper() for x in valid_tag[valid_tag_key]]:
            tag_key_found = "✔"
        if not case_insensitive and fetch_tag['Key'] == valid_tag_key and fetch_tag['Value'] in valid_tag[fetch_tag['Key']]:
            tag_key_found = "✔"

    return tag_key_found

def _cleanOldReports(report_path):

    csvFileList = glob.glob(f'{report_path}/*.csv')
    for filePath in csvFileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)

    htmlFileList = glob.glob(f'{report_path}/*.html')
    for filePath in htmlFileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file", default="tagvalidator.yml", type=str)
    parser.add_argument("-r", "--report-path", help="Provide path of CSV and HTML reports", type=str, required=True)
    args = parser.parse_args()

    _cleanOldReports(args.report_path)
    _tagValidator(args)
