"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from zowe.core_for_zowe_sdk import SdkApi
from zowe.core_for_zowe_sdk.exceptions import FileNotFound
import os


class Files(SdkApi):
    """
    Class used to represent the base z/OSMF Files API.

    ...

    Attributes
    ----------
    connection
        connection object
    """

    def __init__(self, connection):
        """
        Construct a Files object.

        Parameters
        ----------
        connection
            The z/OSMF connection object (generated by the ZoweSDK object)
        """
        super().__init__(connection, "/zosmf/restfiles/")

    def list_dsn(self, name_pattern):
        """Retrieve a list of datasets based on a given pattern.

        Returns
        -------
        json
            A JSON with a list of dataset names matching the given pattern
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["params"] = {"dslevel": name_pattern}
        custom_args["url"] = "{}ds".format(self.request_endpoint)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def list_dsn_members(self, dataset_name, member_pattern=None, member_start=None, limit=1000):
        """Retrieve the list of members on a given PDS/PDSE.

        Returns
        -------
        json
            A JSON with a list of members from a given PDS/PDSE
        """
        custom_args = self.create_custom_request_arguments()
        additional_parms = {}
        if member_start is not None:
            additional_parms['start'] = member_start
        if member_pattern is not None:
            additional_parms['pattern'] = member_pattern
        url = "{}ds/{}/member".format(self.request_endpoint, dataset_name)
        separator = '?'
        for k,v in additional_parms.items():
            url = "{}{}{}={}".format(url,separator,k,v)
            separator = '&'
        custom_args['url'] = url
        custom_args["headers"]["X-IBM-Max-Items"] = "{}".format(limit)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json['items']

    def get_dsn_content(self, dataset_name):
        """Retrieve the contents of a given dataset.

        Returns
        -------
        json
            A JSON with the contents of a given dataset
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self.request_endpoint, dataset_name)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def get_dsn_binary_content(self, dataset_name, with_prefixes=False):
        """
        Retrieve the contents of a given dataset as a binary bytes object.

        Parameters
        ----------
        dataset_name: str - Name of the dataset to retrieve
        with_prefixes: boolean - if True include a 4 byte big endian record len prefix
                                 default: False 
        Returns
        -------
        bytes
            The contents of the dataset with no transformation
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self.request_endpoint, dataset_name)
        custom_args["headers"]["Accept"] = "application/octet-stream"
        if with_prefixes:
            custom_args["headers"]["X-IBM-Data-Type"] = 'record'
        else:
            custom_args["headers"]["X-IBM-Data-Type"] = 'binary'
        content = self.request_handler.perform_request("GET", custom_args)
        return content

    def write_to_dsn(self, dataset_name, data):
        """Write content to an existing dataset.

        Returns
        -------
        json
            A JSON containing the result of the operation
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self.request_endpoint, dataset_name)
        custom_args["data"] = data
        custom_args['headers']['Content-Type'] = 'text/plain'
        response_json = self.request_handler.perform_request(
            "PUT", custom_args, expected_code=[204, 201]
        )
        return response_json

    def download_dsn(self, dataset_name, output_file):
        """Retrieve the contents of a dataset and saves it to a given file."""
        response_json = self.get_dsn_content(dataset_name)
        dataset_content = response_json['response']
        out_file = open(output_file, 'w')
        out_file.write(dataset_content)
        out_file.close()

    def download_binary_dsn(self, dataset_name, output_file, with_prefixes=False):
        """Retrieve the contents of a binary dataset and saves it to a given file. 
        
        Parameters
        ----------
        dataset_name:str - Name of the dataset to download
        output_file:str - Name of the local file to create
        with_prefixes:boolean - If true, include a four big endian bytes record length prefix.
                                The default is False

        Returns
        -------
        bytes
            Binary content of the dataset.
        """
        content = self.get_dsn_binary_content(dataset_name, with_prefixes=with_prefixes)
        out_file = open(output_file, 'wb')
        out_file.write(content)
        out_file.close()

    def upload_file_to_dsn(self, input_file, dataset_name):
        """Upload contents of a given file and uploads it to a dataset."""
        if os.path.isfile(input_file):
            in_file = open(input_file, 'r')
            file_contents = in_file.read()
            response_json = self.write_to_dsn(dataset_name, file_contents)
        else:
            raise FileNotFound(input_file)
