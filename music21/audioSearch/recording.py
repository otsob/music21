# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         audioSearch.recording.py
# Purpose:      routines for making recordings from microphone input
#
# Authors:      Jordi Bartolome
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2011 Michael Scott Asato Cuthbert and the music21 Project
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
modules for audio searching that directly record from the microphone.

Requires PyAudio and portaudio to be installed (http://www.portaudio.com/download.html)

To download pyaudio for windows 64-bit go to https://www.lfd.uci.edu/~gohlke/pythonlibs/

users of 64-bit windows but 32-bit python should download the win32 port

users of 64-bit windows and 64-bit python should download the amd64 port
'''
from importlib.util import find_spec
import unittest
import wave

from music21 import exceptions21
from music21.common.types import DocOrder

from music21 import environment
environLocal = environment.Environment('audioSearch.recording')


###
# to download pyaudio for windows 64-bit go to https://www.lfd.uci.edu/~gohlke/pythonlibs/
# users of 64-bit windows but 32-bit python should download the win32 port
# users of 64-bit windows and 64-bit python should download the amd64 port
# requires portaudio to be installed http://www.portaudio.com/download.html

default_recordChannels = 1
default_recordSampleRate = 44100
default_recordChunkLength = 1024


def samplesFromRecording(seconds=10.0, storeFile=True,
                         recordFormat=None,
                         recordChannels=default_recordChannels,
                         recordSampleRate=default_recordSampleRate,
                         recordChunkLength=default_recordChunkLength):  # pragma: no cover
    '''
    records `seconds` length of sound in the given format (default Wave)
    and optionally stores it to disk using the filename of `storeFile`

    Returns a list of samples.
    '''
    # noinspection PyPackageRequirements
    import pyaudio  # type: ignore  # pylint: disable=import-error
    recordFormatDefault = pyaudio.paInt16

    if recordFormat is None:
        recordFormat = recordFormatDefault

    if recordFormat == pyaudio.paInt8:
        raise RecordingException("cannot perform samplesFromRecording on 8-bit samples")

    p_audio = pyaudio.PyAudio()
    st = p_audio.open(format=recordFormat,
                      channels=recordChannels,
                      rate=recordSampleRate,
                      input=True,
                      frames_per_buffer=recordChunkLength)

    recordingLength = int(recordSampleRate * float(seconds) / recordChunkLength)

    storedWaveSampleList = []

    # time_start = time.time()
    for i in range(recordingLength):
        data = st.read(recordChunkLength)
        storedWaveSampleList.append(data)
    # print('Time elapsed: %.3f s\n' % (time.time() - time_start))
    st.close()
    p_audio.terminate()

    if storeFile is not False:
        if isinstance(storeFile, str):
            waveFilename = storeFile
        else:
            waveFilename = str(environLocal.getRootTempDir() / 'recordingTemp.wav')
        # write recording to disk
        data = b''.join(storedWaveSampleList)
        try:
            # wave.open does not take a path-like object as of 3.9
            wf = wave.open(waveFilename, 'wb')
            wf.setnchannels(recordChannels)
            wf.setsampwidth(p_audio.get_sample_size(recordFormat))
            wf.setframerate(recordSampleRate)
            wf.writeframes(data)
            wf.close()
        except IOError:
            raise RecordingException(f"Cannot open {waveFilename} for writing.")
    return storedWaveSampleList


class RecordingException(exceptions21.Music21Exception):
    pass


# -----------------------------------------
class Test(unittest.TestCase):
    pass




class TestExternal(unittest.TestCase):  # pragma: no cover
    loader = find_spec('pyaudio')
    if loader is not None:  # pragma: no cover
        pyaudio_installed = True
    else:
        pyaudio_installed = False

    @unittest.skipUnless(pyaudio_installed, 'pyaudio must be installed')
    def testRecording(self):
        '''
        record one second of data and print 10 records
        '''
        sampleList = samplesFromRecording(seconds=1, storeFile=False)
        print(sampleList[30:40])


# ------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER: DocOrder = []


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
