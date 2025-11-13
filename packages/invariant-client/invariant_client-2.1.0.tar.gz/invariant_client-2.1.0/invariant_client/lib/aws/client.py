import logging
import json
import pathlib
from typing import Dict, Union

import boto3
import botocore
from botocore.exceptions import ClientError
from mypy_boto3_ec2 import EC2Client
from mypy_boto3_elbv2 import ElasticLoadBalancingv2Client
from mypy_boto3_rds import RDSClient

logger = logging.getLogger(__name__)

class AWSClientError(Exception):
    """Raised when AWS client is unable to be created"""


class AWSClient:
    _session = None
    resources = {
        "addresses": {"client": "ec2", "function": "describe_addresses"},
        "availability_zones": {
            "client": "ec2",
            "function": "describe_availability_zones",
        },
        "customer_gateways": {
            "client": "ec2",
            "function": "describe_customer_gateways",
        },
        "internet_gateways": {
            "client": "ec2",
            "function": "describe_internet_gateways",
        },
        "nat_gateways": {"client": "ec2", "function": "describe_nat_gateways"},
        "network_acls": {"client": "ec2", "function": "describe_network_acls"},
        "network_interfaces": {
            "client": "ec2",
            "function": "describe_network_interfaces",
        },
        "prefix_lists": {"client": "ec2", "function": "describe_prefix_lists"},
        "instances": {"client": "ec2", "function": "describe_instances"},
        "route_tables": {"client": "ec2", "function": "describe_route_tables"},
        "security_groups": {"client": "ec2", "function": "describe_security_groups"},
        "subnets": {"client": "ec2", "function": "describe_subnets"},
        "transit_gateway_attachments": {
            "client": "ec2",
            "function": "describe_transit_gateway_attachments",
        },
        "transit_gateway_route_tables": {
            "client": "ec2",
            "function": "describe_transit_gateway_route_tables",
        },
        "transit_gateway_vpc_attachments": {
            "client": "ec2",
            "function": "describe_transit_gateway_vpc_attachments",
        },
        "transit_gateways": {"client": "ec2", "function": "describe_transit_gateways"},
        "vpc_endpoints": {"client": "ec2", "function": "describe_vpc_endpoints"},
        "vpc_peering_connections": {
            "client": "ec2",
            "function": "describe_vpc_peering_connections",
        },
        "vpcs": {"client": "ec2", "function": "describe_vpcs"},
        "vpn_connections": {"client": "ec2", "function": "describe_vpn_connections"},
        "vpn_gateways": {"client": "ec2", "function": "describe_vpn_gateways"},
        "db_instances": {"client": "rds", "function": "describe_db_instances"},
        "load_balancers": {"client": "elbv2", "function": "describe_load_balancers"},
        "target_groups": {"client": "elbv2", "function": "describe_target_groups"},
    }

    def __init__(
        self,
        accounts=[],
        ignore_accounts=[],
        regions=set([]),
        profile=None,
        role=None,
        skip_resources=[],
    ):
        self.fatal = False
        self.profile = profile
        self.role = role
        if self.profile:
            try:
                self._session = boto3.session.Session(profile_name=self.profile)
            except botocore.exceptions.ProfileNotFound as e:
                raise ConnectionError(f"Unable to setup AWS session: {e}")
        else:
            self._session = boto3.session.Session()
        self.regions = set(regions if regions else self._get_regions())
        self.accounts = self._get_accounts(accounts, ignore_accounts)
        for resource in skip_resources:
            del self.resources[resource]

    def _get_regions(self):
        account_client = self._session.client("account")
        try:
            result = [
                i.get("RegionName")
                for i in account_client.list_regions(
                    RegionOptStatusContains=["ENABLED", "ENABLED_BY_DEFAULT"]
                )["Regions"]
            ]
        except ClientError as e:
            raise ConnectionError(f"Unable to get regions: {e}")
        return set(result)

    def _get_accounts(self, include_accounts=[], exclude_accounts=[]) -> Dict:
        """Get all accessible AWS accounts and optionally filter them.

        Args:
          include_accounts: Account IDs to include, if empty, include all.
          exclude_accounts: Account IDs to exclude.

        Returns:
          A list of accounts to return.
        """
        try:
            org_client = boto3.client("organizations")
            all_accounts = (
                org_client.get_paginator("list_accounts")
                .paginate()
                .build_full_result()["Accounts"]
            )
        except ClientError as e:
            raise AWSClientError(f"Unable to get organization accounts: {e}")

        filtered_accounts = []
        for account_dict in all_accounts:
            account_id = account_dict.get("Id")

            # Inclusion Logic:
            if include_accounts:
                if account_id not in include_accounts:
                    continue  # Skip if not in include list

            # Exclusion Logic:
            if exclude_accounts:
                if account_id in exclude_accounts:
                    continue  # Skip if in exclude list

            filtered_accounts.append(account_dict)
        return filtered_accounts

    def _assume_role(self, account_id, role) -> boto3.session.Session:
        """Assume an account role within AWS.

        Args:
          account_id: Account ID to attempt to assume role on.
          role: Role name to assume.

        Returns:
          Boto3 session

        Raises:
          AWSClientError: When a role is unable to be assumed.
        """
        try:
            sts_client = boto3.client("sts")
            assumed_role = sts_client.assume_role(
                RoleArn=f"arn:aws:iam::{account_id}:role/{role}",
                RoleSessionName="InvariantClient",
            )
            session = boto3.session.Session(
                aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
                aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
                aws_session_token=assumed_role["Credentials"]["SessionToken"],
            )
            return session
        except ClientError as e:
            raise AWSClientError(
                f"Error assuming role for account {account_id}, you can add this to `ignore_accounts` to suppress this error, skipping account: {e}"
            )

    def write_data(self, path, account, region, name, data):
        aws_dir = pathlib.Path(path) / "aws_configs"
        aws_dir.parent.mkdir(parents=True, exist_ok=True)
        config_with_ext = name + ".json"
        config_path = aws_dir / account / region / config_with_ext
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(
                data,
                f,
                indent=1,
                default=str,
                sort_keys=True,
            )

    def _retrieve_configs(
        self,
        client: Union[EC2Client, RDSClient, ElasticLoadBalancingv2Client],
        function_name: str,
        account: str,
        options: dict[str, str] = {},
        path: str = "",
    ):
        """Retrieves config

        Args:
          client: A boto3 client specific to the functions to be called.
          functions: A list of strings of the functions to be called.
          account: The account ID to retrieve configs from.
          options: Options to pass into paginator.

        Raises:
          AWSClientError: Raised when client is unable to be created.
        """
        logger.info(
            f"Fetching {function_name} on account {account} in region {client.meta.region_name}."
        )
        try:
            if client.can_paginate(function_name):
                results = (
                    client.get_paginator(function_name)
                    .paginate(**options)
                    .build_full_result()
                )
            else:
                results = getattr(client, function_name, None)()
                del results["ResponseMetadata"]
            if len(results.keys()) != 1:
                self.fatal = True
                logger.warning(
                    f"Error processing {function_name} results, expected 1 key but got {len(results.keys())}: {results})"
                )
                return
            config_name = next(iter(results))
            self.write_data(
                path, account, client.meta.region_name, config_name, results
            )
        except ClientError as e:
            self.fatal = True
            logger.error(f"Fatal Error: {e}")
            return
        if function_name == "describe_transit_gateway_route_tables":
            tgw_rt = results["TransitGatewayRouteTables"]
            props = self._retrieve_transit_gateway_propagations(client, tgw_rt)
            self.write_data(
                path,
                account,
                client.meta.region_name,
                "TransitGatewayPropagations",
                props,
            )
            routes = self._retrieve_transit_gateway_static_routes(client, tgw_rt)
            self.write_data(
                path,
                account,
                client.meta.region_name,
                "TransitGatewayStaticRoutes",
                routes,
            )
        elif function_name == "describe_load_balancers":
            lbs = results["LoadBalancers"]
            listeners = self._retrieve_load_balancer_listeners(
                client, account, client.meta.region_name, lbs
            )
            self.write_data(
                path,
                account,
                client.meta.region_name,
                "LoadBalancerListeners",
                listeners,
            )
            attributes = self._retrieve_load_balancer_attributes(
                client, account, client.meta.region_name, lbs
            )
            self.write_data(
                path,
                account,
                client.meta.region_name,
                "LoadBalancerAttributes",
                attributes,
            )
        elif function_name == "describe_target_groups":
            target_groups = results["TargetGroups"]
            groups = self._retrieve_load_balancer_target_groups(
                client, account, client.meta.region_name, target_groups
            )
            self.write_data(
                path,
                account,
                client.meta.region_name,
                "LoadBalancerTargetHealth",
                groups,
            )

    def _retrieve_elastic_search_domains(
        self, client: ElasticLoadBalancingv2Client, account: str, path: str
    ):
        domain_names = client.list_domain_names()
        elastic_search_config = client.describe_elasticsearch_domains(
            DomainNames=[
                domainEntry["DomainName"] for domainEntry in domain_names["DomainNames"]
            ]
        )
        del elastic_search_config["ResponseMetadata"]
        self.write_data(
            path,
            account,
            client.meta.region_name,
            "ElasticsearchDomains",
            elastic_search_config,
        )

    def _retrieve_transit_gateway_propagations(self, client: EC2Client, routes):
        props = []
        logger.info(
            "Fetching get_transit_gateway_route_table_propogations for each transit gateway route table id."
        )
        for route in routes:
            try:
                result = client.get_transit_gateway_route_table_propagations(
                    TransitGatewayRouteTableId=route["TransitGatewayRouteTableId"]
                )
                result["TransitGatewayRouteTableId"] = route[
                    "TransitGatewayRouteTableId"
                ]
                del result["ResponseMetadata"]
            except ClientError as e:
                self.fatal = True
                logger.error(e)
                return
            props.append(result)
        return {"TransitGatewayPropagations": props}

    def _retrieve_transit_gateway_static_routes(self, client: EC2Client, routes):
        props = []
        logger.info(
            "Fetching search_transit_gateway_routes for each transit gateway route table id."
        )
        for route in routes:
            try:
                result = client.search_transit_gateway_routes(
                    TransitGatewayRouteTableId=route["TransitGatewayRouteTableId"],
                    Filters=[{"Name": "type", "Values": ["static"]}],
                )
                result["TransitGatewayRouteTableId"] = route[
                    "TransitGatewayRouteTableId"
                ]
                del result["ResponseMetadata"]
            except ClientError as e:
                self.fatal = True
                logger.error(e)
                return
            props.append(result)
        return {"TransitGatewayStaticRoutes": props}

    def _retrieve_load_balancer_target_groups(
        self, client: ElasticLoadBalancingv2Client, account_id, region, target_groups
    ):
        responses = []
        logger.info("Fetching describe_target_health for each ELB target group.")
        for group in target_groups:
            try:
                arn = group["TargetGroupArn"]
                resp = client.describe_target_health(TargetGroupArn=arn)
                resp["TargetGroupArn"] = group["TargetGroupArn"]
                del resp["ResponseMetadata"]
            except (ClientError, KeyError) as e:
                self.fatal = True
                logger.error(e)
                return
            responses.append(resp)
        return {"LoadBalancerTargetHealth": responses}

    def _retrieve_load_balancer_listeners(
        self, client: ElasticLoadBalancingv2Client, account_id, region, lbs
    ):
        results = []
        for lb in lbs:
            try:
                # Try a get instead, these don't have to exist

                arn = lb.get("LoadBalancerArn")
                if not arn:
                    print(f"No target group found for {lb['LoadBalancerArn']}")
                    continue
                response = client.describe_listeners(LoadBalancerArn=arn)
                response["LoadBalancerArn"] = lb["LoadBalancerArn"]
                del response["ResponseMetadata"]
            except (ClientError, KeyError) as e:
                self.fatal = True
                logger.error(e)
                return
            results.append(response)
        return {"LoadBalancerListeners": results}

    def _retrieve_load_balancer_attributes(
        self, client: ElasticLoadBalancingv2Client, account_id, region, lbs
    ):
        results = []
        for lb in lbs:
            try:
                arn = lb["LoadBalancerArn"]
                response = client.describe_load_balancer_attributes(LoadBalancerArn=arn)
                response["LoadBalancerArn"] = lb["LoadBalancerArn"]
                del response["ResponseMetadata"]
            except (ClientError, KeyError) as e:
                self.fatal = True
                logger.error(e)
                return
            results.append(response)
        return {"LoadBalancerAttributes": results}

    def get_configs(self, path):
        for account in self.accounts:
            if self.role:
                session = self._assume_role(account["Id"], self.role)
            else:
                session = self._session
            for region in self.regions:
                for _, resource in self.resources.items():
                    client = session.client(resource["client"], region_name=region)
                    self._retrieve_configs(
                        client, resource["function"], account["Id"], path=path
                    )
                self._retrieve_elastic_search_domains(
                    session.client("es", region_name=region), account["Id"], path=path
                )
        if self.fatal:
            raise AWSClientError("Fatal error retreiving AWS configs.")
        return self.fatal
