from tempfile import NamedTemporaryFile

import orgparse
import pytest

from resumaker import resumaker


@pytest.fixture
def meta_resume():
    return {}


class TestLoadFromOrg:
    def test_org_formatted_str(self):
        org = "* Heading"

        result = resumaker._load_from_org(org)

        assert isinstance(result, orgparse.node.OrgRootNode)
        assert str(result[1]) == org

    def test_filepath(self):
        org = "* Heading"

        with NamedTemporaryFile(mode="w+") as f:
            f.write(org)
            f.flush()

            result = resumaker._load_from_org(f.name)

        assert isinstance(result, orgparse.node.OrgRootNode)
        assert str(result[1]) == org

    def test_file_like_org(self):
        org = "* Heading"

        with NamedTemporaryFile(mode="w+") as f:
            f.write(org)
            f.flush()
            with open(f.name) as g:
                result = resumaker._load_from_org(g)

        assert isinstance(result, orgparse.node.OrgRootNode)
        assert str(result[1]) == org

    def test_invalid_type_arg(self):
        with pytest.raises(TypeError):
            resumaker._load_from_org(0)


def test_foo(org_resume):
    context = resumaker._parse_context_from_org(org_resume)
    assert context["name"] == "John Doe"
