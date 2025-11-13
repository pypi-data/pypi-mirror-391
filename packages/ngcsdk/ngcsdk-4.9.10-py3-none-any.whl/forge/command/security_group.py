# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import json
import pathlib
import sys

from forge.api.security_group import SecurityGroupAPI
from forge.command._shared import (
    construct_item_metavar,
    decorate_create_command_with_label_arguments,
    decorate_update_command_with_label_arguments,
    make_item_type,
    wrap_bad_request_exception,
)
from forge.command.forge import ForgeCommand
from forge.printer.security_group import (
    RULE_FIELDS,
    SECURITY_GROUP_FIELDS,
    SecurityGroupPrinter,
)
from ngcbase.command.args_validation import check_add_args_columns, check_valid_columns
from ngcbase.command.clicommand import CLICommand
from ngcbase.util.utils import get_columns_help


def _read_rules_json(rules_json: str):
    if rules_json == "-":
        text = sys.stdin.read()
    else:
        rules_json = pathlib.Path(rules_json)
        text = rules_json.read_text(encoding="utf-8")
    return json.loads(text)


class SecurityGroupCommand(ForgeCommand):  # noqa: D101

    CMD_NAME = "security-group"
    HELP = "Security Group Commands"
    DESC = "Security Group Commands"

    def __init__(self, parser):
        super().__init__(parser)
        self.parser = parser
        self.config = self.client.config
        self.api = self.client.forge.security_group
        self.printer = SecurityGroupPrinter(self.client.config)

    LIST_HELP = "List security groups."

    columns_dict = SECURITY_GROUP_FIELDS
    columns_default = ("id", "Id")
    columns_help = get_columns_help(columns_dict, columns_default)
    status_enum = ["Pending", "Provisioning", "Ready", "Deleting", "Error"]

    @CLICommand.arguments(
        "query",
        metavar="<query>",
        help="Filter across all security groups. Input will be matched against name, description and status fields.",
        type=str,
        nargs="?",
        default=None,
    )
    @CLICommand.arguments(
        "--status",
        metavar="<status>",
        help=f"Filter by status. Choices are: {', '.join(status_enum)}",
        type=str,
        default=None,
        choices=status_enum,
    )
    @CLICommand.arguments(
        "--column",
        metavar="<column>",
        help=columns_help,
        default=None,
        action="append",
        type=lambda value, columns_dict=columns_dict: check_valid_columns(value, columns_dict),
    )
    @CLICommand.arguments("--site", metavar="<site>", help="Filter by site id.", type=str)
    @CLICommand.command(help=LIST_HELP, description=LIST_HELP)
    def list(self, args):
        """List security groups."""
        resp = self.api.list(args.query, org=args.org, site=args.site, status=args.status)
        check_add_args_columns(args.column, SecurityGroupCommand.columns_default)
        self.printer.print_list(resp, args.column)

    LIST_RULES_HELP = "List the rules of a specific security group."

    rule_columns_default = ("name", "Name")

    @CLICommand.arguments("security_group", metavar="<security-group>", help="Security group id", type=str)
    @CLICommand.arguments(
        "--column",
        metavar="<column>",
        help=get_columns_help(RULE_FIELDS, rule_columns_default),
        default=None,
        action="append",
        type=lambda value, columns_dict=RULE_FIELDS: check_valid_columns(value, columns_dict),
    )
    @CLICommand.arguments(
        "--direction",
        metavar="(INGRESS|EGRESS)",
        help="Filter rows based on direction.",
        choices=("INGRESS", "EGRESS"),
    )
    @CLICommand.arguments(
        "--action",
        metavar="(PERMIT|DENY)",
        help="Filter rows based on action.",
        choices=("PERMIT", "DENY"),
    )
    @CLICommand.arguments(
        "--protocol",
        metavar="(TCP|UDP|ICMP|ANY)",
        help="Filter rows based on protocol. Can be specified multiple times to include multiple protocols.",
        action="append",
        choices=("TCP", "UDP", "ICMP", "ANY"),
    )
    @CLICommand.command(name="list-rules", help=LIST_RULES_HELP, description=LIST_RULES_HELP)
    def list_rules(self, args):
        """List security groups."""
        resp = self.api.list_rules(args.security_group, org=args.org)
        if args.direction:
            resp = [rule for rule in resp if rule["direction"] == args.direction]
        if args.action:
            resp = [rule for rule in resp if rule["action"] == args.action]
        if args.protocol:
            resp = [rule for rule in resp if rule["protocol"] in args.protocol]
        check_add_args_columns(args.column, SecurityGroupCommand.rule_columns_default)
        self.printer.print_list_rules(resp, args.column)

    INFO_HELP = "Security group information."

    @CLICommand.arguments("security_group", metavar="<security-group>", help="Security group id", type=str)
    @CLICommand.arguments("--status-history", help="Show status history.", action="store_true")
    @CLICommand.command(help=INFO_HELP, description=INFO_HELP)
    def info(self, args):
        """Security group info."""
        resp = self.api.info(args.security_group, org=args.org)
        self.printer.print_info(resp, args.status_history)

    CREATE_HELP = "Create security group."

    @decorate_create_command_with_label_arguments()
    @CLICommand.arguments("name", metavar="<name>", help="Security group name.", type=str)
    @CLICommand.arguments("--site", metavar="<site>", help="Specify site id.", type=str, required=True)
    @CLICommand.arguments("--description", metavar="<description>", help="Description of the security group.", type=str)
    @CLICommand.arguments(
        "--rule",
        dest="rules",
        metavar=construct_item_metavar(SecurityGroupAPI.Rule),
        help=(
            "Specify a rule for this security group. Can be specified multiple times."
            " (For security groups with many rules, consider using '--rules-json' instead.)"
        ),
        type=make_item_type(SecurityGroupAPI.Rule),
        action="append",
    )
    @CLICommand.arguments(
        "--rules-json",
        metavar="(<json-file>|-)",
        help=(
            "Read rules from a JSON file. Or use '-' to read JSON rules from stdin."
            " The expected JSON format is the same as 'list-rules --format_type=json'."
        ),
        type=str,
    )
    @CLICommand.command(help=CREATE_HELP, description=CREATE_HELP)
    def create(self, args):
        """Create security group."""
        if args.rules_json:
            args.rules = args.rules or []
            args.rules.extend(_read_rules_json(args.rules_json))

        with wrap_bad_request_exception():
            resp = self.api.create(
                args.name,
                org=args.org,
                site=args.site,
                description=args.description,
                labels=args.label,
                rules=args.rules,
            )
        self.printer.print_info(resp)

    UPDATE_HELP = "Update security group."

    @decorate_update_command_with_label_arguments(
        label_getter=lambda self, args: self.api.info(args.security_group, org=args.org).get("labels"),
        what="security group",
    )
    @CLICommand.arguments("security_group", metavar="<security-group>", help="Security group id.", type=str)
    @CLICommand.arguments("--name", metavar="<name>", help="Specify security group name.", type=str)
    @CLICommand.arguments("--description", metavar="<description>", help="Description of the security group.", type=str)
    @CLICommand.arguments(
        "--rule",
        dest="rules",
        metavar=construct_item_metavar(SecurityGroupAPI.Rule),
        help=(
            "Specify a rule for this security group. Overwrites existing rules. Can be specified multiple times."
            " (For security groups with many rules, consider using '--rules-json' instead.)"
        ),
        type=make_item_type(SecurityGroupAPI.Rule),
        action="append",
    )
    @CLICommand.arguments(
        "--rules-json",
        metavar="(<json-file>|-)",
        help=(
            "Read rules from a JSON file. Or use '-' to read JSON rules from stdin."
            " The expected JSON format is the same as 'list-rules --format_type=json'."
        ),
        type=str,
    )
    @CLICommand.command(help=UPDATE_HELP, description=UPDATE_HELP)
    def update(self, args):
        """Update security group."""
        if args.rules_json:
            args.rules = args.rules or []
            args.rules.extend(_read_rules_json(args.rules_json))
        with wrap_bad_request_exception():
            resp = self.api.update(
                args.security_group,
                org=args.org,
                name=args.name,
                description=args.description,
                rules=args.rules,
                labels=args.label,
            )
        self.printer.print_info(resp)

    REMOVE_HELP = "Remove security group."

    @CLICommand.arguments("security_group", metavar="<security-group>", help="Security group id.", type=str)
    @CLICommand.command(help=REMOVE_HELP, description=REMOVE_HELP)
    def remove(self, args):
        """Remove security group."""
        self.api.remove(args.security_group, org=args.org)
        if self.config.format_type == "json":
            # Print valid JSON, even though we don't have anything interesting to show here.
            self.printer.print_json({})
