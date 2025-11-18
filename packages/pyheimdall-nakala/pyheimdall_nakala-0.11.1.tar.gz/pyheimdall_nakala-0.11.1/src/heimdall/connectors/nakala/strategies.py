# -*- coding: utf-8 -*-
import heimdall


def FilterItemsByEntityId(eids):
    r"""Item filtering strategy

    This function returns a filter function filtering items belonging to one of the specified entity identifiers ``eids``.

    :param eids: (:py:class:`list`) -- List of :py:class:`str` entity identifiers.
    :return: Filtering function
    :rtype: :py:class:`function`
    """  # nopep8: E501
    def _filter(item):
        return item.get('eid') in eids
    return _filter


def FilterPathsByPointers(target_pid, id_pid, path_pid):
    r"""File path filtering strategy

    This function returns a filter function whose job is to return absolute paths of files to upload for a source item.
    Each path will be found in the metadata of property ID ``path_pid`` found in any target item uniquely identified by a metadata of property ID ``id_pid`` and pointed by the metadata of property ID ``target_pid`` in the source item.

    :param target_pid: (:py:class:`str`) -- Pointer metadata in source item.
    :param id_pid: (:py:class:`str`) -- Unique identifier for target items.
    :param path_pid: (:py:class:`str`) -- Metadata of target items containing a file path.
    :return: Filtering function
    :rtype: :py:class:`function`
    """  # nopep8: E501

    def _filter(item, tree):
        r"""Filtering function

        :param item: (:py:class:`xml.etree.ElementTree.Element`) HERA Item
        :param tree: (:py:class:`xml.etree.ElementTree.Element`) HERA elements tree
        :return: List of file paths :py:class:`str` absolute file paths
        :rtype: :py:class:`list`
        """  # nopep8: E501
        pointers = heimdall.getValues(item, pid=target_pid)

        def get_target(item):
            nonlocal pointer
            if heimdall.getValue(item, pid=id_pid) == pointer:
                return True
            return False

        paths = list()
        for pointer in pointers:
            p_item = heimdall.getItem(tree, get_target)
            paths.append(heimdall.getValue(p_item, pid=path_pid))
        return paths

    return _filter
