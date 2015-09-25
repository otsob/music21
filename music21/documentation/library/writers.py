# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         documentation/library/writers.py
# Purpose:      music21 documentation IPython notebook to ReST converter
#
# Authors:      Josiah Wolf Oberholtzer
#               Michael Scott Cuthbert
#
# Copyright:    Copyright © 2013-15 Michael Scott Cuthbert and the music21 Project
# License:      LGPL or BSD, see license.txt
#-------------------------------------------------------------------------------

import codecs
import os
import re
import shutil

from music21.ext import six
from music21 import common
from music21 import exceptions21

from music21 import environment
environLocal = environment.Environment('documentation.library.writers')


class DocumentationWritersException(exceptions21.Music21Exception):
    pass

class DocumentationWriter(object):
    '''
    Abstract base class for writers.
    
    Call .run() on the object to make it work.
    '''
    def __init__(self):
        from music21 import documentation # @UnresolvedImport
        self.outputDirectory = None
        self.docBasePath = documentation.__path__[0]
        self.docSourcePath = os.path.join(self.docBasePath,
                                          'source')
        self.docGeneratedPath = os.path.join(self.docBasePath,
                                          'autogenerated')
    def run(self):
        raise NotImplementedError

    ### PUBLIC METHODS ###
    def sourceToAutogenerated(self, sourcePath):
        '''
        converts a sourcePath to an outputPath
        
        generally speaking, substitutes "source" for "autogenerated"        
        '''
        outputPath = os.path.abspath(sourcePath).replace(self.docSourcePath, self.docGeneratedPath)
        return outputPath
    
    
    def setupOutputDirectory(self, outputDirectory=None):
        '''
        creates outputDirectory if it does not exist.
        
        Looks at self.outputDirectory if not there.
        '''
        if outputDirectory is None:
            outputDirectory = self.outputDirectory
            if outputDirectory is None:
                raise DocumentationWritersException("Cannot setup output directory without guidance")
        if os.path.exists(outputDirectory):
            return 
        
        os.makedirs(outputDirectory)

class StaticFileCopier(DocumentationWriter):
    '''
    Copies static files into the autogenerated directory.
    '''
    def run(self):
        excludedFiles = ['.ipynb', '__pycache__', '.pyc', '.gitignore', '.DS_Store']
        for directoryPath, unused, fileNames in os.walk(self.docSourcePath):
            self.setupOutputDirectory(self.sourceToAutogenerated(directoryPath))
            for fileName in fileNames:
                runIt = True
                for ex in excludedFiles:
                    if fileName.endswith(ex):
                        runIt = False
                if runIt is False:
                    continue
                inputFilePath = os.path.join(directoryPath, fileName)
                outputFilePath = self.sourceToAutogenerated(inputFilePath)
                if os.path.exists(outputFilePath) and os.path.getmtime(outputFilePath) > os.path.getmtime(inputFilePath):
                    print('\tSKIPPED {0}'.format(common.relativepath(outputFilePath)))
                else:
                    shutil.copyfile(inputFilePath, outputFilePath)
                    print('\tWROTE   {0}'.format(common.relativepath(outputFilePath)))



class ReSTWriter(DocumentationWriter):
    '''
    Abstract base class for all ReST writers.
    '''
    def run(self):
        raise NotImplementedError
    
    def write(self, filePath, rst): #
        '''
        Write ``rst`` (a unicode string) to ``filePath``, 
        only overwriting an existing file if the content differs.
        '''
        shouldWrite = True
        if os.path.exists(filePath):
            oldRst = common.readFileEncodingSafe(filePath, firstGuess='utf-8')
            if rst == oldRst:
                shouldWrite = False
            else:
                pass
                ## uncomment for  help in figuring out why a file keeps being different...
                #import difflib
                #print(common.relativepath(filePath))
                #print('\n'.join(difflib.ndiff(rst.split('\n'), oldRst.split('\n'))))
                
        if shouldWrite:
            with codecs.open(filePath, 'w', 'utf-8') as f:
                try:
                    f.write(rst)
                except UnicodeEncodeError as uee:
                    six.raise_from(DocumentationWritersException("Could not write %s with rst:\n%s" % (filePath, rst)), uee)
            print('\tWROTE   {0}'.format(common.relativepath(filePath)))
        else:
            print('\tSKIPPED {0}'.format(common.relativepath(filePath)))

class ModuleReferenceReSTWriter(ReSTWriter):
    '''
    Writes module reference ReST files, and their index.rst file.
    '''
    def __init__(self):
        super(ModuleReferenceReSTWriter, self).__init__()
        self.outputDirectory = os.path.join(
            self.docGeneratedPath,
            'moduleReference',
            )
        self.setupOutputDirectory()
    
    def run(self):
        from music21 import documentation # @UnresolvedImport
        moduleReferenceDirectoryPath = self.outputDirectory
        referenceNames = []
        for module in [x for x in documentation.ModuleIterator()]:
            moduleDocumenter = documentation.ModuleDocumenter(module)
            if not moduleDocumenter.classDocumenters \
                   and not moduleDocumenter.functionDocumenters:
                continue
            rst = '\n'.join(moduleDocumenter.run())
            referenceName = moduleDocumenter.referenceName
            referenceNames.append(referenceName)
            fileName = '{0}.rst'.format(referenceName)
            rstFilePath = os.path.join(
                moduleReferenceDirectoryPath,
                fileName,
                )
            try:
                self.write(rstFilePath, rst)
            except TypeError as te:
                raise TypeError("File failed: " + rstFilePath + ", reason: " + str(te))

        self.writeIndexRst(referenceNames)

    def writeIndexRst(self, referenceNames):
        '''
        Write the index.rst file from the list of reference names
        '''
        lines = []
        lines.append('.. moduleReference:')
        lines.append('')
        lines.append('.. WARNING: DO NOT EDIT THIS FILE:')
        lines.append('   AUTOMATICALLY GENERATED.')
        lines.append('')
        lines.append('Module Reference')
        lines.append('================')
        lines.append('')
        lines.append('.. toctree::')
        lines.append('   :maxdepth: 1')
        lines.append('')
        for referenceName in sorted(referenceNames):
            lines.append('   {0}'.format(referenceName))
        rst = '\n'.join(lines)
        indexFilePath = os.path.join(
            self.outputDirectory,
            'index.rst',
            )
        self.write(indexFilePath, rst)
        


class CorpusReferenceReSTWriter(ReSTWriter):
    '''
    Write the corpus reference ReST file: referenceCorpus.rst
    into about/
    '''
    def __init__(self):
        super(CorpusReferenceReSTWriter, self).__init__()
        self.outputDirectory = os.path.join(
            self.docGeneratedPath,
            'about',
            )
        self.setupOutputDirectory()

    
    def run(self):
        from music21 import documentation # @UnresolvedImport
        corpusReferenceFilePath = os.path.join(
            self.outputDirectory,
            'referenceCorpus.rst',
            )
        lines = documentation.CorpusDocumenter().run()
        rst = '\n'.join(lines)
        self.write(corpusReferenceFilePath, rst)


class IPythonNotebookReSTWriter(ReSTWriter):
    '''
    Converts IPython notebooks into ReST, and handles their associated image
    files.

    This class wraps the 3rd-party ``nbconvert`` Python script.
    '''
    def __init__(self):
        super(IPythonNotebookReSTWriter, self).__init__()
        # Do not run self.setupOutputDirectory()

    def run(self):
        from music21 import documentation # @UnresolvedImport
        ipythonNotebookFilePaths = [x for x in
            documentation.IPythonNotebookIterator()]
        for ipythonNotebookFilePath in ipythonNotebookFilePaths:
            nbConvertReturnCode = self.convertOneNotebook(ipythonNotebookFilePath)
            if nbConvertReturnCode is True:
                self.cleanupNotebookAssets(ipythonNotebookFilePath)
                print('\tWROTE   {0}'.format(common.relativepath(
                    ipythonNotebookFilePath)))
            else:
                if '-checkpoint' not in ipythonNotebookFilePath:
                    print('\tSKIPPED {0}'.format(common.relativepath(
                        ipythonNotebookFilePath)))
                # do not print anything for skipped -checkpoint files
    ### PRIVATE METHODS ###

    def cleanupNotebookAssets(self, ipythonNotebookFilePath):
        '''
        Deletes all .text files in the _files directory.
        '''
        notebookFileNameWithoutExtension = os.path.splitext(
            os.path.basename(ipythonNotebookFilePath))[0]
        notebookParentDirectoryPath = os.path.abspath(
            os.path.dirname(ipythonNotebookFilePath),
            )
        imageFileDirectoryName = notebookFileNameWithoutExtension# + '_files'
        imageFileDirectoryPath = os.path.join(
            notebookParentDirectoryPath,
            imageFileDirectoryName,
            )
        imageFileDirectoryPath = self.sourceToAutogenerated(imageFileDirectoryPath)
        if os.path.exists(imageFileDirectoryPath) is False:
            return
        for fileName in os.listdir(imageFileDirectoryPath):
            if fileName.endswith('.text'):
                filePath = os.path.join(
                    imageFileDirectoryPath,
                    fileName,
                    )
                os.remove(filePath)

    @property
    def rstEditingWarningFormat(self):
        result = []
        result.append('.. WARNING: DO NOT EDIT THIS FILE:')
        result.append('   AUTOMATICALLY GENERATED.')
        result.append('   PLEASE EDIT THE .py FILE DIRECTLY.')
        result.append('')
        return result


    def convertOneNotebook(self, ipythonNotebookFilePath):
        '''
        converts one .ipynb file to .rst using nbconvert.

        returns True if IPythonNotebook was converted.
        returns False if IPythonNotebook's converted .rst file is newer than the .ipynb file.

        sends AssertionError if ipythonNotebookFilePath does not exist.
        '''
        if '-checkpoint' in ipythonNotebookFilePath:
            return False
        
        if not os.path.exists(ipythonNotebookFilePath):
            raise DocumentationWritersException('No iPythonNotebook with filePath %s' % ipythonNotebookFilePath)
        notebookFileNameWithoutExtension = os.path.splitext(
            os.path.basename(ipythonNotebookFilePath))[0]
        notebookParentDirectoryPath = os.path.abspath(
            os.path.dirname(ipythonNotebookFilePath),
            )
        rstFileName = notebookFileNameWithoutExtension + '.rst'
        rstFilePath = self.sourceToAutogenerated(os.path.join(
            notebookParentDirectoryPath,
            rstFileName,
            ))

        if os.path.exists(rstFilePath):
            # rst file is newer than .ipynb file, do not convert.
            
            if os.path.getmtime(rstFilePath) > os.path.getmtime(ipythonNotebookFilePath):
                return False

        self.runNBConvert(ipythonNotebookFilePath)
        with open(rstFilePath, 'r', encoding='utf8') as f:
            oldLines = f.read().splitlines()
        lines = self.cleanConvertedNotebook(oldLines, ipythonNotebookFilePath)
        with open(rstFilePath, 'w') as f:
            f.write('\n'.join(lines))

        return True


    def cleanConvertedNotebook(self, oldLines, ipythonNotebookFilePath):
        '''
        Take a notebook directly as parsed and make it look better for HTML
        '''
        notebookFileNameWithoutExtension = os.path.splitext(
            os.path.basename(ipythonNotebookFilePath))[0]
        #imageFileDirectoryName = self.sourceToAutogenerated(notebookFileNameWithoutExtension)

        ipythonPromptPattern = re.compile(r'^In\[[\d ]+\]:')
        mangledInternalReference = re.compile(
            r'\:(class|ref|func|meth)\:\`\`?(.*?)\`\`?')
        newLines = ['.. _' + notebookFileNameWithoutExtension + ":" , ''] + self.rstEditingWarningFormat
        currentLineNumber = 0
        
        while currentLineNumber < len(oldLines):
            currentLine = oldLines[currentLineNumber]
            # Remove all IPython prompts and the blank line that follows:
            if ipythonPromptPattern.match(currentLine) is not None:
                currentLineNumber += 2
                continue
            # Correct the image path in each ReST image directive:
            elif currentLine.startswith('.. image:: '):
                imageFileName = currentLine.partition('.. image:: ')[2]
                imageFileShort = imageFileName.split(os.path.sep)[-1]
                if notebookFileNameWithoutExtension in currentLine:
                    newImageDirective = '.. image:: {0}'.format(
                        imageFileShort,
                        )
                    newLines.append(newImageDirective)
                else:
                    newLines.append(currentLine)
                currentLineNumber += 1
            elif "# ignore this" in currentLine:
                if '.. code:: python' in newLines[-2]:
                    newLines.pop() # remove blank line
                    newLines.pop() # remove '.. code:: python'
                
                currentLineNumber += 2  #  # ignore this
                                        #  %load_ext music21.ipython21.ipExtension
                # TODO: Skip all % lines, without looking for "#ignore this"
            # Otherwise, nothing special to do, just add the line to our results:
            else:
                # fix cases of inline :class:`~music21.stream.Stream` being
                # converted by markdown to :class:``~music21.stream.Stream``
                newCurrentLine = mangledInternalReference.sub(
                    r':\1:`\2`',
                    currentLine
                    )
                newLines.append(newCurrentLine)
                currentLineNumber += 1

        lines = self.blankLineAfterLiteral(newLines)

        return lines

    def blankLineAfterLiteral(self, oldLines):
        '''
        Guarantee a blank line after literal blocks.
        '''
        lines = [oldLines[0]] # start with first line...
        for first, second in self.iterateSequencePairwise(oldLines):
            if len(first.strip()) \
                    and first[0].isspace() \
                    and len(second.strip()) \
                    and not second[0].isspace():
                lines.append('')
            lines.append(second)
            if '.. parsed-literal::' in second:
                lines.append('   :class: ipython-result')
        return lines

    def iterateSequencePairwise(self, sequence):
        prev = None
        for x in sequence:
            cur = x
            if prev is not None:
                yield prev, cur
            prev = cur

    def runNBConvert(self, ipythonNotebookFilePath):
        try:
            from nbconvert import nbconvertapp as nb
        except ImportError:
            environLocal.warn("Using music21.ext.nbconvert -- this will stop working in IPython4. use pip3 install nbconvert")        
            from music21.ext.nbconvert import nbconvertapp as nb # @UnresolvedImport

        outputPath = os.path.splitext(self.sourceToAutogenerated(ipythonNotebookFilePath))[0]
        
        app = nb.NbConvertApp.instance() # @UndefinedVariable
        app.initialize(argv=['--to', 'rst', '--output', outputPath, ipythonNotebookFilePath])
        app.writer.build_directory = os.path.dirname(ipythonNotebookFilePath)
        app.start()

## UNUSED
#     def processNotebook(self, ipythonNotebookFilePath):
#         from music21 import documentation # @UnresolvedImport
#         with open(ipythonNotebookFilePath, 'r') as f:
#             contents = f.read()
#             contentsAsJson = json.loads(contents)
#         directoryPath, unused_sep, baseName = ipythonNotebookFilePath.rpartition(
#             os.path.sep)
#         baseNameWithoutExtension = os.path.splitext(baseName)[0]
#         imageFilesDirectoryPath = os.path.join(
#             directoryPath,
#             '{0}_files'.format(baseNameWithoutExtension),
#             )
#         rstFilePath = os.path.join(
#             directoryPath,
#             '{0}.rst'.format(baseNameWithoutExtension),
#             )
#         lines, imageData = documentation.IPythonNotebookDocumenter(
#             contentsAsJson)()
#         rst = '\n'.join(lines)
#         self.write(rstFilePath, rst)
#         if not imageData:
#             return
#         if not os.path.exists(imageFilesDirectoryPath):
#             os.mkdir(imageFilesDirectoryPath)
#         for imageFileName, imageFileData in imageData.iteritems():
#             imageFilePath = os.path.join(
#                 imageFilesDirectoryPath,
#                 imageFileName,
#                 )
#             shouldOverwriteImage = True
#             with open(imageFilePath, 'rb') as f:
#                 oldImageFileData = f.read()
#                 if oldImageFileData == imageFileData:
#                     shouldOverwriteImage = False
#             if shouldOverwriteImage:
#                 with open(imageFilePath, 'wb') as f:
#                     f.write(imageFileData)


if __name__ == '__main__':
    import music21
    music21.mainTest()

