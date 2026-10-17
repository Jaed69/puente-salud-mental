from puente.guardian.resources import COMMUNITY_MENTAL_HEALTH_NOTE, CRISIS_RESOURCES


def test_resources_include_verified_linea_113_option_5():
    line = next(r for r in CRISIS_RESOURCES if r.number == "113")

    assert line.option == "5"
    assert line.free is True
    assert line.availability == "24/7"
    assert line.verified is True
    assert "MINSA" in line.source


def test_resources_include_emergency_and_violence_lines():
    numbers = {r.number for r in CRISIS_RESOURCES}

    assert {"106", "105", "116", "100"} <= numbers


def test_resources_do_not_include_whatsapp_channels():
    for resource in CRISIS_RESOURCES:
        assert "whatsapp" not in resource.model_dump_json().lower()


def test_community_mental_health_note_cites_gob_pe():
    assert "gob.pe/10942" in COMMUNITY_MENTAL_HEALTH_NOTE.source
    assert "sin referencia" in COMMUNITY_MENTAL_HEALTH_NOTE.text
