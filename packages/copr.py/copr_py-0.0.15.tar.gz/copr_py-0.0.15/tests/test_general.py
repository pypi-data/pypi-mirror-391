from copr import *

COPR = API.init()

def test_versionAPI():
  assert COPR.versionAPI()

def test_dataset():
  assert COPR.dataset()

def test_stats():
  assert isinstance(COPR.stats(), dict)
