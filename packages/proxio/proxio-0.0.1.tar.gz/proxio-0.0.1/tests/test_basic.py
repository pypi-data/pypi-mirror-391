from proxio import version

def test_version():
    # Test case 1: check the basic format of the version
    v = version()

    assert len(v.split(".")) == 3
