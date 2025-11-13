# -*- coding: utf-8 -*-
import heimdall
import requests
from json import dumps
from .models import (
    Collection, Data, File,
    get_accepted_uris, get_accepted_types,
    )
from .strategies import FilterItemsByEntityId, FilterPathsByPointers

"""
Provides the Nakala CREATE connector.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""  # nopep8: E501


@heimdall.decorators.create_database('nakala:api')
def upload(tree, **options):
    r"""Posts a HERA elements tree to the Nakala API

    :param tree: (:py:class:`xml.etree.ElementTree.Element`) HERA elements tree
    :param \**options: Keyword arguments, see below.
    :return: None
    :rtype: :py:class:`NoneType`

    :Keyword arguments:
        * **api_key** (:py:class:`str`) -- Nakala user API key.
        * **collections_getter** (:py:class:`function`, optional) -- Function returning Nakala identifiers of collections to link uploaded items to. If this argument is not provided, :py:class:`heimdall.connectors.nakala.create_collection` will be used.
        * **data_filter** (:py:class:`function`, optional) -- "Data" items filtering function. Each of these items will be uploaded as a data item on Nakala. In other words, each item belonging to one of these entities will become a data page on Nakala, with its own DOI. If this argument is not provided, :py:class:`heimdall.connectors.nakala.strategies.FilterItemsByEntityId```(['file', ])`` will be used.
        * **meta_creator** (:py:class:`function`, optional) -- Function converting each metadata to the format expected by Nakala. If this argument is not provided, :py:class:`heimdall.connectors.nakala.create_nakala_metadata` will be used.
        * **path_filter** (:py:class:`function`, default: :py:class:`heimdall.connectors.nakala.strategies.get_files_in_pointed_items`) -- File paths getter function, returning a list of paths to local files to be uploaded on Nakala, each of these file belonging to the data page corresponding to its item. If this argument is not provided, :py:class:`heimdall.connectors.nakala.strategies.FilterPathByPointers```('file', 'path', 'path')`` will be used, to make easier using this connector and the ``format='files'`` connector together.
        * **test** (:py:class:`bool`, optional, default: ``True``) -- If ``True``, Nakala test server will be used ; if ``False``, Nakala production (*ie.* "real") server will be used.
        * **private** (:py:class:`bool`, optional, default: ``True``) -- If ``False``, all data will be published publicly on Nakala, permanently, with no easy mean to unpublish them.
    """  # nopep8: E501
    api_key = options['api_key']
    get_collections = options.get('collections_getter', create_collection)
    data_filter = options.get('data_filter', FilterItemsByEntityId(['item', ]))
    meta_creator = options.get('meta_creator', create_nakala_metadata)
    path_filter = options.get('path_filter',
                              FilterPathsByPointers('file', 'path', 'path'))
    private = options.get('private', True)
    test = options.get('test', True)

    uris = filter_uris(tree)
    collections = get_collections(api_key, private, test)

    counter = 0
    for item in heimdall.getItems(tree, data_filter):
        eid = item.get('eid')
        doi = get_doi(item, tree)
        entity = heimdall.getEntity(tree, lambda e: e.get('id') == eid)
        metas = _create_metas(item, uris[eid], meta_creator)
        append_types(metas, entity.uri, test)
        paths = path_filter(item, tree)
        f_upload = True
        m_upload = True
        reupload = False
        if doi is not None:
            reupload = True
            data = Data(doi=doi, private=private, test=test)
            data.get(api_key)
            hashes = [{'file': path, 'sha1': File(path).sha} for path in paths]
            f_upload = _must_reupload_files(data.files, hashes)
            m_upload = _must_reupload_metas(data.metadata, metas)
        hashes = upload_files(paths, api_key, test) if f_upload else None
        metas = metas if m_upload else None

        doi = upload_item(
                metas, hashes, collections,
                api_key, doi, private, test
                )
        if doi is not None and not reupload:
            heimdall.createMetadata(item, doi, pid='identifier', aid='doi')
            counter += 1
    return collections


def get_doi(item, tree):
    doi = heimdall.getValue(item, aid='doi')  # be nice 'files' connector
    if doi is not None:
        return doi
    doi = heimdall.getValue(item, pid='doi')   # be nice 'csv' connector
    return doi


def create_collection(api_key, private=True, test=True):
    r"""Creates a new Nakala collection.

    :param api_key: (:py:class:`str`) Nakala API key.
    :param test: (:py:class:`bool`, optional, default: ``True``) -- If ``True``, Nakala test server will be used ; if ``False``, Nakala production (*ie.* "real") server will be used.
    :param private: (:py:class:`bool`, optional, default: ``True``) -- If ``True``, the created collection will be private to the user identified by ``api_key``. If ``False``, it will be public.
    :return: List of length 1, containing the Nakala identifier of the created collection.
    :rtype: :py:class:`list` of :py:class:`str`
    """  # nopep8: E501
    c = Collection("Tu peux pas test", private=private, test=test)
    c.upload(api_key)
    return [c.id, ]


def filter_uris(tree, test=True):
    r"""Filter from ``tree`` attributes and properties with URIs accepted by Nakala.

    :param tree: (:py:class:`xml.etree.ElementTree.Element`) HERA elements tree
    :param test: (:py:class:`bool`, optional, default: ``True``) -- If ``True``, Nakala test server will be used ; if ``False``, Nakala production (*ie.* "real") server will be used.
    :return: Dictionary of attributes and properties identifiers, categorized by entity identifier and URI (``{eid: {uri: {'aid': [..], 'pid': [..]}}}``).
    :rtype: :py:class:`dict`
    :see also: :py:class:`heimdall.connectors.nakala.models.get_accepted_uris`
    """  # nopep8: E501
    ACCEPTED_URIS = get_accepted_uris(test)
    uris = dict()  # {eid: {uri: {'aid': [..], 'pid': [..]}}}
    for e in heimdall.getEntities(tree):
        eid = e.get('id')
        uris[eid] = dict()
        for a in e.attributes:
            for uri in a.uri:
                if uri in ACCEPTED_URIS:
                    d = uris[eid].get(uri, dict())
                    ids = d.get('aid', list())
                    ids.append(a.get('id'))
                    d['aid'] = ids
                    uris[eid][uri] = d
            pid = a.get('pid')
            p = heimdall.getProperty(tree, lambda p: p.get('id') == pid)
            if p is not None:
                for uri in p.uri:
                    if uri in ACCEPTED_URIS:
                        d = uris[eid].get(uri, dict())
                        ids = d.get('pid', list())
                        ids.append(p.get('id'))
                        d['pid'] = ids
                        uris[eid][uri] = d
    return uris


def append_types(metas, entity_uris, test=True):
    r"""Append valid uri as types to metadata

    :param metas: (:py:class:`list`) Metadata list
    :param entity_uris: (:py:class:`dict`) Entity VS their URI
    :param test: (:py:class:`bool`, optional, default: ``True``) -- If ``True``, Nakala test server will be used to retrieve valid URI ; if ``False``, Nakala production (*ie.* "real") server will be used.
    :return: List of all URI valid for Nakala.
    :rtype: :py:class:`list` of :py:class:`str`
    """  # nopep8: E501
    DEFAULT = 'http://purl.org/ontology/bibo/Collection'
    type_uri = 'http://nakala.fr/terms#type'
    for m in metas:
        if m.get('propertyUri', None) == type_uri:
            return [m.get('value', None), ]
    ACCEPTED_TYPES = get_accepted_types(test)
    types = list(filter(lambda uri: uri in ACCEPTED_TYPES, entity_uris))
    if len(types) < 1:
        # [[NKLQUIRK]] Nakala does NOT expect /vocabularies/dcmitypes,
        # but expects /vocabularies/datatypes instead
        types.append(DEFAULT)
    for value in types:
        # [[NKLQUIRK]] warning: Nakala will refuse metadata with more than
        # one type ; so if you iterate this more than once, upload will fail
        metas.append({
            'lang': None,
            'value': value,
            'typeUri': _uri2typeUri(type_uri),
            'propertyUri': type_uri,
            })
    return types


def getValues(item, **options):
    r"""Return an Item's values, by language

    :return: All Metadata values of ``item`` found by ``filter``, as a :py:class:`dict`: keys are language codes (``None`` if missing), values are metadata text.
    :rtype: :py:class:`dict`
    """  # nopep8: E501
    from heimdall.util import get_nodes, get_language
    filter = options['filter']  # TODO
    nodes = get_nodes(item, 'metadata', filter)
    values = dict()
    for n in nodes:
        language_code = get_language(n)
        languages = values.get(language_code, list())
        if n.text is not None:
            languages.append(n.text)
        else:
            languages.append('')
        values[language_code] = languages
    return values


def _create_metas(item, uris, meta_creator):
    metadata = list()
    for uri, ids in uris.items():
        aids = ids.get('aid', list())
        pids = ids.get('pid', list())

        def _filter(m):
            return m.get('pid') in pids or m.get('aid') in aids
        languages_vs_values = getValues(item, filter=_filter)

        for language, values in languages_vs_values.items():
            for value in values:
                metas = meta_creator(uri, value, language)
                if type(metas) is list:
                    metadata.extend(metas)
                else:
                    metadata.append(metas)
    return metadata


def upload_item(metas, hashes, collections,
                api_key, doi=None, private=True, test=True
                ):
    d = Data(
            doi=doi,
            collections=collections,
            metadata=metas, files=hashes,
            private=private, test=test,
            )
    doi = d.upload(api_key)
    return doi


def _uri2typeUri(uri):
    if uri == 'http://nakala.fr/terms#type':
        return 'http://purl.org/dc/terms/URI'
    return None  # 'http://www.w3.org/2001/XMLSchema#string'


def create_nakala_metadata(uri, value, language=None):
    r"""Converts a metadata value to the format expected by Nakala.

    The format expected by Nakala is a :py:class:`dict` containing:
        * always, a value for the ``propertyUri`` key (which should be ``uri``, if legal for Nakala);
        * always, a value for the ``value`` key (which precise format depends on ``uri``, but should be derived from ``value``);
        * sometimes, a value for the ``typeUri`` is required, sometimes not;
        * if ``language`` is not ``None``, it should be a value for the ``lang`` key.

    This behaviours are specific to each version of Nakala and, at the time of writing, have yet to be clearly specified.

    :param uri: (:py:class:`str`) Metadata URI. In HERA terms, it would be the URI of the property or attribute ``value`` is an instance of.
    :param value: (:py:class:`str`) Metadata value.
    :param language: (:py:class:`str`, optional, default: ``None``) Language in which ``value`` is conveyed.
    :return: Parameters, but in a format Nakala understands.
    :rtype: :py:class:`dict`
    :see also: :py:class:`heimdall.connectors.nakala.models.get_accepted_uris`
    """  # nopep8: E501
    if uri == 'http://nakala.fr/terms#creator':
        result = {
            'value': {'surname': value, 'givenname': ".", },
            'propertyUri': uri,
            'lang': language,
            }
    else:
        result = {
            'value': value,
            'typeUri': _uri2typeUri(uri),
            'propertyUri': uri,
            'lang': language,
            }
    return result


def upload_files(paths, api_key, test=True):
    r"""Upload a list of files to Nakala, given their paths

    NOTE: if some of the ``paths`` point to identical files (according to their
    respective SHAs), the upload of the dups will fail.
    """
    hashes = list()
    for path in paths:
        f = File(path, test=test)
        h = f.upload(api_key)
        hashes.append(h)
    return hashes


def _must_reupload_files(remote, local):
    return _must_reupload(remote, local, ['sha1', ])


def _must_reupload_metas(remote, local):
    keys = ['lang', 'propertyUri', 'typeUri', 'value', ]
    return _must_reupload(remote, local, keys)


def _must_reupload(remote, local, keys):
    r"""Compare ``remote`` and ``local`` dicts, but only for ``keys``

    If there is any difference in any value corresponding to elements of ``keys``,
    this function will return ``True``.

    :param remote: (:py:class:`list` of :py:class:`dict`) Old data
    :param local: (:py:class:`list` of :py:class:`dict`) Current data
    :param keys: (:py:class:`list` of :py:class:`str`) Key we're interested in
    :return: ``True`` if there is any difference between ``remote`` and ``local``
    :rtype: :py:class:`bool`
    """  # nopep8: E501
    if len(remote) is not len(local):
        return True
    for elocal in local:
        found = False
        for eremote in remote:
            found = True
            for key in keys:
                if eremote[key] != elocal[key]:
                    found = False
                    break
            if found:
                break
        if not found:
            return True
    return False
