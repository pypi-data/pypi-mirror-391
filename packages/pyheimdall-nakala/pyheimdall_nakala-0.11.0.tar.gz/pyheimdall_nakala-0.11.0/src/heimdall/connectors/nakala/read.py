# -*- coding: utf-8 -*-
import heimdall
import requests
import uuid
from heimdall.util import set_language, get_nodes

"""
Provides connector to the Nakala research repository.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""  # nopep8: E501

ITEM_EID = 'item'
FILE_EID = 'file'


@heimdall.decorators.get_database('nakala:api')
def getDatabase(**options):
    r"""Imports a database from a Nakala repository

    :param \**options: Keyword arguments, see below.
    :return: HERA element tree
    :rtype: lxml.ElementTree

    :Keyword arguments:
        * **url** (``str``) -- URL of a Nakala items list

    Option ``url`` can be either a Nakala collection URL, or the URL of
    a Nakala search query.

    * ``{baseurl}/collections/{identifier}`` for collections
    * ``{baseurl}/search?{query parameters}`` for search queries

    ``baseurl`` depends on the Nakala instance you are using.
    At the time of writing, there are two different instances:
    * ``https://api.nakala.fr/`` for the real Nakala
    * ``https://apitest.nakala.fr/`` for the sandbox (test) instance

    See ``{baseurl}/doc`` for details.
    """
    presets = _load_presets()

    url = options['url']
    headers = {'accept': 'application/json', }
    payload = {'page': 1, 'limit': 25, }
    response = _request(url, headers, payload)
    data = response.get('datas', None)
    if data is None:
        # NOTE: search results wrap items in key 'datas'; however,
        # collection results wrap them in 'data', that's nakala logic for ya
        data = response['data']
        last = int(response['lastPage'])
        while int(payload['page']) != last:
            # request remaining pages; depending on url, this can take time ...
            payload['page'] += 1
            print(payload['page'], '/', last, '(', payload['limit'], ')')
            response = _request(url, headers, payload)
            data += response['data']
    print(len(data))
    tree = _create_tree(data, presets)
    return tree


def update_presets(tree):
    properties = heimdall.util.get_node(tree, 'properties')
    nakala_properties = dict()
    for url, p in _load_presets().items():
        if 'nakala.fr' in url:
            nakala_properties[url] = p
            pid = p.get('id')
            old_p = heimdall.getProperty(tree, lambda e: e.get('id') == pid)
            if old_p is None:
                properties.append(p)
            else:
                # TODO: upgrade this crap
                properties.remove(old_p)
                properties.append(p)
    return nakala_properties


def _load_presets():
    path = 'https://gitlab.huma-num.fr/datasphere/heimdall/presets/-/raw/main/properties.xml'  # nopep8: E501
    tree = heimdall.getDatabase(format='hera:xml', url=path)
    PRESETS = dict()
    for p in heimdall.getProperties(tree):
        uris = get_nodes(p, 'uri')
        for uri in uris:
            try:
                do_not_want = PRESETS[uri.text]
                raise ValueError(f"URI '{uri}' not unique")
            except KeyError:
                PRESETS[uri.text] = p
    return PRESETS


def _request(url, headers, payload):
    response = requests.get(url, headers=headers, params=payload)
    if response.status_code != requests.codes.ok:
        response.raise_for_status()
    # NOTE: maybe check for response.headers, too?
    return response.json()


def _create_tree(data, presets):
    root = heimdall.util.tree.create_empty_tree()
    items = root.get_container('items')
    for o in data:
        (item, files) = _create_item(o, presets)
        items.append(item)
        for file in files:
            items.append(file)
    return root


def _create_item(data, properties):
    item = heimdall.elements.Item(eid=ITEM_EID)
    files = list()
    for key, value in data.items():
        if key == 'files':
            for o in data['files']:
                file = _create_file_item(o)
                uuid_ = str(uuid.uuid4())
                m = _create_metadata(file, 'id', uuid_)
                m.set('pid', 'id')
                # TODO maybe use file.sha1 instead of uuid?
                _create_metadata(item, 'file', uuid_)
                files.append(file)
        elif key == 'metas':
            for o in data['metas']:
                _create_meta(item, o, properties)
        elif type(value) is list:
            for v in value:
                _create_metadata(item, key, v)
        else:
            _create_metadata(item, key, value)
    return (item, files)


def _create_file_item(data):
    item = heimdall.elements.Item(eid=FILE_EID)
    for key, value in data.items():
        _create_metadata(item, key, value)
    return item


def _create_metadata(item, key, value):
    element = heimdall.elements.Metadata(aid=key)
    element.text = str(value)
    item.append(element)
    return element


def _create_meta(item, meta, properties):
    value = str(meta.get('value', ''))
    if value is None or len(value.strip()) < 1:
        return None  # no value, metadata is missing, don't create it
    uri = meta['propertyUri']
    pid = properties[uri].get('id')
    node = heimdall.elements.Metadata(pid=pid, aid=pid)
    language_code = meta.get('lang', None)
    if language_code is not None:
        set_language(node, language_code)
    node.text = value
    item.append(node)
    return node
