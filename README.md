# BP-VALIDATOR

As **VALIDATOR** has capability to scan AWS specific resource's tags as per user-defined property file and generates a CSV and HTML report.

## SERVICES SUPPORTED
- EC2
- Route53
- S3
- RDS
- DynamoDB

## CONFIGURATIONS 
Configuration for this utility will be managed in YAML format. Below are the configurations details :

- ***aws_profile :*** It is a aws profile that you can use to a perform utility in AWS.

- ***region :*** The AWS Region where this utility is executed.

- ***services:ec2:key:value (Optional) :*** Tags given to ec2 instances.It will validate all the ec2 matches to this given tags.

- ***services:s3:key:value (Optional) :*** Tags given to s3.It will validate all the s3 matches to this given tags.

- ***services:route53:key:value (Optional) :*** Tags given to route53.It will validate all the route53 matches to this given tags.

- ***services:dynamodb:key:value (Optional) :*** Tags given to dynamodb.It will validate all the dynamodb matches to this given tags.

- ***services:rds:key:value (Optional) :*** Tags given to rds .It will validate all the rds matches to this given tags.

## SAMPLE CONF FILE
```
case_insensitive: true

aws_profile: default

region:
  - us-east-1

services:
  ec2:
    env:
      - any
    learner:
      - any

  s3:
    learner:
      - any
    env:
      - any

  route53:
    learner:
      - any
    env:
      - any

  dynamodb:
    env:
      - any
    learner:
      - any

  rds:
    learner:
      - any
    env:
      - any
```

## USAGE

===============================================================

Three things are needed to use this :
- AWS resources access (either via AWS Access and Secret keys or IAM ROLE).
- YAML Property file
- Reports Path where you want to store HTML ans CSV reports

### LOCALLY
To run this utility locally from your system.

- Run the python script.

   ```
   python3 ./scripts/tagvalidator.py -p <yaml property file path> -r <reports path>
   ```