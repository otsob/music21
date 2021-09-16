# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         musicxml/helpers.py
# Purpose:      Helper routines for musicxml export
#
# Authors:      Michael Scott Cuthbert
#               Jacob Tyler Walls
#
# Copyright:    Copyright © 2013-2021 Michael Scott Cuthbert and the music21 Project
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
import copy
from typing import List

from xml.etree.ElementTree import tostring as et_tostring
from xml.etree.ElementTree import Element  # for typing

def dumpString(obj, *, noCopy=False) -> str:
    r'''
    wrapper around xml.etree.ElementTree that returns a string
    in every case and indents tags and sorts attributes.

    >>> from music21.musicxml.m21ToXml import Element
    >>> from music21.musicxml.helpers import dumpString
    >>> e = Element('accidental')

    >>> dumpString(e)
    '<accidental />'

    >>> e.text = '∆'
    >>> e.text == '∆'
    True
    >>> dumpString(e)
    '<accidental>∆</accidental>'
    '''
    if noCopy is False:
        xmlEl = copy.deepcopy(obj)  # adds 5% overhead
    else:
        xmlEl = obj
    indent(xmlEl)  # adds 5% overhead

    for el in xmlEl.iter():
        attrib = el.attrib
        if len(attrib) > 1:
            # adjust attribute order, e.g. by sorting
            attribs = sorted(attrib.items())
            attrib.clear()
            attrib.update(attribs)
    xStr = et_tostring(xmlEl, encoding='unicode')
    xStr = xStr.rstrip()
    return xStr


def dump(obj):
    r'''
    wrapper around xml.etree.ElementTree that prints a string
    in every case and indents tags and sorts attributes.  (Prints, does not return)

    >>> from music21.musicxml.helpers import dump
    >>> from xml.etree.ElementTree import Element
    >>> e = Element('accidental')

    >>> dump(e)
    <accidental />

    >>> e.text = '∆'
    >>> e.text == '∆'
    True
    >>> dump(e)
    <accidental>∆</accidental>
    '''
    print(dumpString(obj))


def indent(elem, level=0):
    '''
    helper method, indent an element in place:
    '''
    i = '\n' + level * '  '
    lenL = len(elem)
    if lenL:
        if not elem.text or not elem.text.strip():
            elem.text = i + '  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i

        subElem = None
        for subElem in elem:
            indent(subElem, level + 1)
        if subElem is not None:  # last el...
            subElem.tail = i

        if not elem.tail or not elem.tail.strip():
            elem.tail = '\n' + level * '  '
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def insertBeforeElements(root, insert, tagList=None):
    # noinspection PyShadowingNames
    '''
    Insert element `insert` into element `root` at the earliest position
    of any instance of a child tag given in `tagList`. Append the element
    if `tagList` is `None`.

    >>> from xml.etree.ElementTree import fromstring as El
    >>> from music21.musicxml.helpers import insertBeforeElements, dump
    >>> root = El('<clef><sign>G</sign><line>4</line></clef>')
    >>> insert = El('<foo/>')

    >>> insertBeforeElements(root, insert, tagList=['line'])
    >>> dump(root)
    <clef>
        <sign>G</sign>
        <foo />
        <line>4</line>
    </clef>

    Now insert another element at the end by not specifying a tag list:

    >>> insert2 = El('<bar/>')
    >>> insertBeforeElements(root, insert2)
    >>> dump(root)
    <clef>
        <sign>G</sign>
        <foo />
        <line>4</line>
        <bar />
    </clef>
    '''
    if not tagList:
        root.append(insert)
        return
    insertIndices = {len(root)}
    # Iterate children only, not grandchildren
    for i, child in enumerate(root.findall('*')):
        if child.tag in tagList:
            insertIndices.add(i)
    root.insert(min(insertIndices), insert)


def measureNumberComesBefore(mNum1: str, mNum2: str) -> bool:
    '''
    Determine whether `measureNumber1` strictly precedes
    `measureNumber2` given that they could involve suffixes.
    Equal values return False.

    >>> from music21.musicxml.helpers import measureNumberComesBefore
    >>> measureNumberComesBefore('23', '24')
    True
    >>> measureNumberComesBefore('23', '23')
    False
    >>> measureNumberComesBefore('23', '23a')
    True
    >>> measureNumberComesBefore('23a', '23b')
    True
    >>> measureNumberComesBefore('23b', '23a')
    False
    >>> measureNumberComesBefore('23b', '24a')
    True
    >>> measureNumberComesBefore('23b', '23b')
    False
    '''
    def splitSuffix(measureNumber):
        number = ''
        for char in measureNumber:
            if char.isnumeric():
                number += char
            else:
                break
        suffix = measureNumber[len(number):]
        return number, suffix

    if mNum1 == mNum2:
        return False
    m1Numeric, m1Suffix = splitSuffix(mNum1)
    m2Numeric, m2Suffix = splitSuffix(mNum2)
    if int(m1Numeric) != int(m2Numeric):
        return int(m1Numeric) < int(m2Numeric)
    else:
        sortedSuffixes = sorted([m1Suffix, m2Suffix])
        return m1Suffix is sortedSuffixes[0]

def childrenEqual(e1: Element, e2: Element, children: List[str]) -> bool:
    '''
    Tests whether the given child tags exist under each given element
    and the texts of those child tags compare equal.

    >>> from xml.etree.ElementTree import fromstring as El
    >>> from xml.etree.ElementTree import SubElement
    >>> a = El('<clef />')
    >>> b = El('<clef />')
    >>> a_sign = SubElement(a, 'sign')
    >>> a_sign.text = 'G'
    >>> b_sign = SubElement(b, 'sign')
    >>> b_sign.text = 'F'

    >>> from music21.musicxml.helpers import childrenEqual
    >>> childrenEqual(a, b, children=['sign'])
    False

    >>> b_sign.text = 'G'
    >>> childrenEqual(a, b, children=['sign'])
    True

    >>> childrenEqual(a, b, children=['sign', 'line'])
    False
    '''
    for child in children:
        e1_child = e1.find(child)
        if e1_child is None:
            return False
        e2_child = e2.find(child)
        if e2_child is None:
            return False
        if e1_child.text != e2_child.text:
            return False
    return True


if __name__ == '__main__':
    import music21
    music21.mainTest()

