from copr import *

COPR = API.init()

def test_entitySelection():
  assert len(COPR.entities(label='Tower Bridge', unique=False, hasFiles=True)) > 0

def test_entityClass():
  for entity in COPR.entities():
    assert isinstance(entity, COPREntity)

def test_entityGeneral():
  for entity in COPR.entities():
    assert entity.howToCite()

def test_entityParameters():
  for entity in COPR.entities():
    assert entity.id()
    assert entity.label()
    assert entity.description() != None
    assert entity.manifestationKind()
    assert entity.unique() != None

def test_entityFiles():
  for entity in COPR.entities():
    for file in entity.files():
      assert file.filename()
      assert file.isTheFile() != None

def test_entitySelections():
  for entity in COPR.entities():
    for selection in entity.selections():
      assert selection.x()
      assert selection.file().filename()
      assert selection.file().isTheFile() != None
