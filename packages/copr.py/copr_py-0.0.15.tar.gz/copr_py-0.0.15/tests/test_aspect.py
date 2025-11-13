from copr import *

COPR = API.init()

def test_aspectSelection():
  assert len(COPR.aspects(qualityKind='colour')) > 0

def test_aspectClass():
  for entity in COPR.aspects():
    assert isinstance(entity, COPRAspect)
