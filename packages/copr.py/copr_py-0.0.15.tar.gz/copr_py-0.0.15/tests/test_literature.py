from copr import *

COPR = API.init()

def test_literatureSelection():
  assert len(COPR.literature(author='Mocnik')) > 0

def test_literatureClass():
  for literature in COPR.literature():
    assert isinstance(literature, COPRLiterature)

def test_literatureParameters():
  for literature in COPR.literature():
    assert literature.author() or literature.editor() or literature.institution()
    assert literature.title()
