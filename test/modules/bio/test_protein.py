from events import EventMessage


def test_protein_simple(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"bio"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "protein ATTCATCGATCGCTA"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "ile-his-arg-ser-leu" in data[0].text.lower(), "Protein construction failed."


def test_protein_start(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"bio"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "protein ATTCATCGAATGTCGCTA"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "start-ser-leu" in data[0].text.lower(), "Protein construction with start codon failed."


def test_protein_stop(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"bio"})
    hallo.function_dispatcher.dispatch(EventMessage(test_server, None, test_user, "protein ATTCATCGATAGTCGCTA"))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "ile-his-arg-stop" in data[0].text.lower(), "Protein construction with stop codon failed."


def test_protein_many_start(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"bio"})
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, None, test_user, "protein ATTCATCGAATGTCGCTATGCATGCAGCATAUGCAGTCG"
    ))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "start-gln-ser" in data[0].text.lower(), "Protein construction with multiple start codons failed."


def test_protein_invalid(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"bio"})
    hallo.function_dispatcher.dispatch(EventMessage(
        test_server, None, test_user, "protein ATGCATCGAATGTCGFTCAGCATAUGCAGTCG"
    ))
    data = test_server.get_send_data(1, test_user, EventMessage)
    assert "error" in data[0].text.lower(), "Protein construction should fail with non-base characters."


def test_protein_passive(hallo_getter):
    hallo, test_server, test_chan, test_user = hallo_getter({"bio"})
    hallo.function_dispatcher.dispatch_passive(EventMessage(
        test_server, test_chan, test_user, "ATTCATCGATCGCTA"
    ))
    data = test_server.get_send_data(1, test_chan, EventMessage)
    assert"ile-his-arg-ser-leu" in data[0].text.lower(), "Passive protein construction failed."
