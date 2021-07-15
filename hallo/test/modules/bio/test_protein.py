from hallo.events import EventMessage


def test_protein_simple(hallo_getter):
    test_hallo = hallo_getter({"bio"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "protein ATTCATCGATCGCTA")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "ile-his-arg-ser-leu" in data[0].text.lower(), "Protein construction failed."


def test_protein_start(hallo_getter):
    test_hallo = hallo_getter({"bio"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "protein ATTCATCGAATGTCGCTA")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "start-ser-leu" in data[0].text.lower()
    ), "Protein construction with start codon failed."


def test_protein_stop(hallo_getter):
    test_hallo = hallo_getter({"bio"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "protein ATTCATCGATAGTCGCTA")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "ile-his-arg-stop" in data[0].text.lower()
    ), "Protein construction with stop codon failed."


def test_protein_many_start(hallo_getter):
    test_hallo = hallo_getter({"bio"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server,
            None,
            test_hallo.test_user,
            "protein ATTCATCGAATGTCGCTATGCATGCAGCATAUGCAGTCG",
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "start-gln-ser" in data[0].text.lower()
    ), "Protein construction with multiple start codons failed."


def test_protein_invalid(hallo_getter):
    test_hallo = hallo_getter({"bio"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(
            test_hallo.test_server, None, test_hallo.test_user, "protein ATGCATCGAATGTCGFTCAGCATAUGCAGTCG"
        )
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert (
        "error" in data[0].text.lower()
    ), "Protein construction should fail with non-base characters."


def test_protein_passive(hallo_getter):
    test_hallo = hallo_getter({"bio"})
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "ATTCATCGATCGCTA")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert (
        "ile-his-arg-ser-leu" in data[0].text.lower()
    ), "Passive protein construction failed."
