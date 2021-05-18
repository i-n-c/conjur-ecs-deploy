![Shipping containers with conjur logo](images/conjur-ecs-demo.jpg)

# Conjur ECS Deploy

This repo contains a cloudformation template and supporting scripts for deploying a scalable, fault tolerant and secure Conjur OSS instance in AWS.

## Certification level

![](https://img.shields.io/badge/Certification%20Level-Community-28A745?link=https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md)

This repo is a **Community** level project. It's a community contributed project that **is not reviewed or supported
by CyberArk**. For more detailed information on our certification levels, see [our community guidelines](https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md#community).

## Requirements

- Minimum Conjur Version is 1.11.6
- Minimum AWS permissions for the deploying role can be found [here](#IAM-Policy).
- Register a domain on Route53. Instructions can be found [here](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-register.html#domain-register-procedure).
- Create an Amazon Secrets Manager secret. This secret will be used to set the Conjur admin user's password. The value should be stored a non-JSON raw string secret and satisfy the following complexity:
  - Between 12 and 128 characters
  - 2 uppercase letters
  - 2 lowercase letters
  - 1 special character
  - 1 digit 

## Architecture

Conjur Open Source is deployed in containers within ECS (Elastic Container Service). These containers are autoscaled based on CPU usage, and backed by an RDS instance. The containers are hosted on Fargate to allow scaling and reduce instance management load.

Full diagram from cloudformation designer:
![AWS Architecture Diagram](images/cloudformation-designer.png)

## IAM Policy
The user deploying the stack must have the permissions specified in [deployer_iam_policy.yml](deployer_iam_policy.yml)

## Usage Instructions

1. Clone the repo:

    ```bash
      git clone --recursive git@github.com:cyberark/conjur-ecs-deploy
      pushd conjur-ecs-deploy
    ```

2. Generate and store the Conjur Admin password as an ASM Secret. The ARN
   of this secret is required as a template parameter.

   ```bash
   set +o history
    aws --profile myprofile secretsmanager create-secret \
      --name "ConjurAdminPassword" \
      --secret-string "file://dev/shm/secretfile"
    set -o history
    ```

3. Generate parameters file (requires jq & yq utilities)

    ```bash
      scripts/generateEmptyParams cloudformation.yml > params_mystack.yml
    ```

4. Customize the generated parameters file in your editor of choice.
5. Launch a Stack

    Stack Name pattern: `[a-z][a-z0-9]+`

    Stack Name Description: The stack name must start with a lowercase letter
    then contain lowercase letters and numbers. This is because its reused
    in various places with more restrictive character sets (eg rds db name).

    ```bash
      $ aws --profile myprofile \
      cloudformation create-stack \
        --stack-name mystack \
        --template-body file://cloudformation.yml \
        --parameters file://params_mystack.json \
        --capabilities CAPABILITY_NAMED_IAM
    ```

6. Ensure conjur is up by visiting https://your.conjur.domain

7. Configure cli

    ```bash
      docker run -it cyberark/conjur-cli:5
      conjur init -u https://your.conjur.domain
      conjur authn login -u admin
      # You will be prompted for the conjur admin password
      # you stored in ASM before running the template.
      conjur list variables
      # returns [] as a fresh instance has no variables
      # but shows that api operations are succeeding.
    ```
## Contributing

We welcome contributions of all kinds to this repository. For instructions on how to get started and descriptions
of our development workflows, please see our [contributing guide](CONTRIBUTING.md).

## Known Limitations

- The project requires a power user to deploy the stack. Please insure you keep this user's credentials secure.
- The project does not validate user input.

## License

Copyright (c) 2020 CyberArk Software Ltd. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

For the full license text see [`LICENSE`](LICENSE).
