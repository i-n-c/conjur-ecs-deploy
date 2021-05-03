# Contributing to Conjur ECS Deploy

For general contribution and community guidelines, please see the [community repo](https://github.com/cyberark/community). In particular, before contributing
please review our [contributor licensing guide](https://github.com/cyberark/community/blob/master/CONTRIBUTING.md#when-the-repo-does-not-include-the-cla)
to ensure your contribution is compliant with our contributor license
agreements.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Pull Request Workflow](#pull-request-workflow)

## Prerequisites

- Minimum AWS permissions for the deploying role as specified in [deployer_iam_policy.yml](deployer_iam_policy.yml)
- bash

## Pull Request Workflow

1. Search the [open issues][issues] in GitHub to find out what has been planned
2. Select an existing issue or open an issue to propose changes or fixes
3. Add the `implementing` label to the issue as you begin to work on it
4. Deploy stack into AWS as described [here](README.md#usage-instructions) and ensure you are able to authenticate to Conjur.
5. Submit a pull request, linking the issue in the description (e.g. `Connected to #123`)
6. Add the `implemented` label to the issue, and ask another contributor to review and merge your code
