# -*- coding: utf-8 -*- #
# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command to create a Data Fusion instance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding

from googlecloudsdk.api_lib.compute import base_classes as compute_base
from googlecloudsdk.api_lib.data_fusion import datafusion as df
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute import scope_prompter
from googlecloudsdk.command_lib.data_fusion import operation_poller
from googlecloudsdk.command_lib.data_fusion import resource_args
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


_EDITIONS = ['basic', 'enterprise']


class Create(base.Command):
  """Create and initialize a Cloud Data Fusion instance.

  If run asynchronously with `--async`, exits after printing an operation
  that can be used to poll the status of the creation operation via:

    {command} operations list

  ## EXAMPLES

  To create instance 'my-instance' in project 'my-project', location in
  'my-location', and zone in 'my-zone' run:

    $ {command} --project=my-project --location=my-location my-instance
      --zone=my-zone
  """

  @staticmethod
  def Args(parser):
    resource_args.AddInstanceResourceArg(parser, 'Instance to create.')
    base.ASYNC_FLAG.AddToParser(parser)
    labels_util.AddCreateLabelsFlags(parser)
    parser.add_argument(
        '--zone',
        help='Compute Engine zone in which the instance will '
        'be created. For example: `--zone=us-central1-a`.',
        required=True)
    parser.add_argument(
        '--edition',
        choices=_EDITIONS,
        default='basic',
        help='Edition of the Data Fusion instance to create. '
        'For example: `--edition=enterprise`.')
    parser.add_argument(
        '--options',
        type=arg_parsers.ArgDict(),
        metavar='KEY=VALUE',
        help='Options to use for instance creation, '
        'specified as KEY1=VALUE1,KEY2=VALUE2.')
    parser.add_argument(
        '--enable_stackdriver_logging',
        action='store_true',
        help='Enable Stackdriver logging for this Data Fusion instance.')
    parser.add_argument(
        '--enable_stackdriver_monitoring',
        action='store_true',
        help='Enable Stackdriver monitoring for this Data Fusion instance.')

  def Run(self, args):
    datafusion = df.Datafusion()
    instance_ref = args.CONCEPTS.instance.Parse()

    # Prompt for zone if it is not specified
    zone = args.zone
    if not zone:
      holder = compute_base.ComputeApiHolder(self.ReleaseTrack())
      _, zone = scope_prompter.PromptForScope(
          resource_name='instance',
          underspecified_names=[instance_ref.Name()],
          scopes=[compute_scope.ScopeEnum.ZONE],
          default_scope=None,
          scope_lister=flags.GetDefaultScopeLister(holder.client))

    options = args.options
    if not options:
      options = {}
    labels = args.labels
    if not labels:
      labels = {}
    enable_stackdriver_logging = args.enable_stackdriver_logging
    if not enable_stackdriver_logging:
      enable_stackdriver_logging = False
    enable_stackdriver_monitoring = args.enable_stackdriver_monitoring
    if not enable_stackdriver_monitoring:
      enable_stackdriver_monitoring = False
    edition = args.edition.upper()
    if edition == 'ENTERPRISE':
      edition = datafusion.messages.Instance.TypeValueValuesEnum.ENTERPRISE
    else:
      edition = datafusion.messages.Instance.TypeValueValuesEnum.BASIC
    instance = datafusion.messages.Instance(
        zone=zone,
        type=edition,
        enableStackdriverLogging=enable_stackdriver_logging,
        enableStackdriverMonitoring=enable_stackdriver_monitoring,
        options=encoding.DictToAdditionalPropertyMessage(
            options, datafusion.messages.Instance.OptionsValue, True),
        labels=encoding.DictToAdditionalPropertyMessage(
            labels, datafusion.messages.Instance.LabelsValue, True))

    req = datafusion.messages.DatafusionProjectsLocationsInstancesCreateRequest(
        instance=instance,
        instanceId=instance_ref.Name(),
        parent=instance_ref.Parent().RelativeName())

    operation = datafusion.client.projects_locations_instances.Create(req)

    if args.async:
      log.CreatedResource(
          instance_ref.RelativeName(), kind='instance', is_async=True)
      return operation
    else:
      waiter.WaitFor(
          operation_poller.OperationPoller(),
          operation.name,
          'Waiting for [{}] to complete. This may take several minutes.'.format(
              operation.name),
          wait_ceiling_ms=df.OPERATION_TIMEOUT)
      log.CreatedResource(
          instance_ref.RelativeName(), kind='instance', is_async=False)
