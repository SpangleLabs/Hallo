from hallo.events import EventMessage


def test_calc_simple(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2+2")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text == "4", "2+2 != 4"


def test_calc_multiply(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 21*56")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text == "1176", "21*56 != 1176"


def test_calc_divide(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 1/5")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text == "0.2", "1/5 != 0.2"


def test_calc_subtract(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 13-17")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text == "-4", "13-17 != -4"


def test_calc_div_zero(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 1/0")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower(), "division by zero should fail"
    assert (
        "no division by zero" in data[0].text
    ), "division by zero response did no specify problem"


def test_cos(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc cos(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1 == float(data[0].text), "cos(0) != 1"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc cos(pi/2)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "cos(pi/2) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc cos(pi)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert -1 == float(data[0].text), "cos(pi) != -1"


def test_sin(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sin(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "sin(0) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sin(pi/2)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1 == float(data[0].text), "sin(pi/2) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sin(pi)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "sin(pi) != 0"


def test_order_of_operations(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 6+7*8")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 62 == float(data[0].text), "6+7*8 != 62"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 16/8-2")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "16/8-2 != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 9-5/(8-3)*2+6")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 13 == float(data[0].text), "9-5/(8-3)*2+6 != 13"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 150/(6+3*8)-5")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), " 150/(6+3*8)-5 != 0"


def test_brackets(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc (25-11)*3")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 42 == float(data[0].text), "(25-11)*3 != 42"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 4+(-1(-2-1))^2")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 13 == float(data[0].text), "4+(-1(-2-1))^2 != 13"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2(3+4)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 14 == float(data[0].text), "2(3+4) != 14"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc (3+4)3")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 21 == float(data[0].text), "(3+4)3 != 21"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc (((17*3)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower(), "(((17*3) should fail"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc (21/3))+2))*5")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower(), "(21/3))+2))*5 should fail"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc ((15*(3))())")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower(), "((15*(3))()) should fail"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc (3)-(7)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert -4 == float(data[0].text), "(3)-(7) != -4"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc e(3+4)pi")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 59.778 == float(data[0].text[:6]), "e(3+4)pi != 59.778"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc cos(acos(0.7))")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0.7 == round(float(data[0].text), 5), "cos(acos(0.7)) != 0.7"


def test_pi(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc pi")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "3.141" == data[0].text[:5], "pi != 3.141"


def test_e(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc e")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "2.718" == data[0].text[:5], "e != 2.718"


def test_tan(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc tan(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "tan(0) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc tan(pi)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "tan(pi) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc tan(pi/2)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 10 ** 6 < abs(float(data[0].text)), "abs(tan(pi/2)) < 1,000,000"


def test_acos(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc acos(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "acos(1) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc acos(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "1.570" == data[0].text[:5], "acos(0) != pi/2"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc acos(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "3.141" == data[0].text[:5], "acos(-1) != pi"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc acos(2)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text, "acos(2) should fail"


def test_asin(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc asin(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "asin(0) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc asin(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1.5707 == float(data[0].text[:6]), "asin(1) != pi/2"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc asin(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert -1.5707 == float(data[0].text[:7]), "asin(-1) != -pi/2"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc asin(2)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text, "asin(2) should fail"


def test_atan(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atan(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "atan(0) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atan(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0.785 == float(data[0].text[:5]), "atan(1) != pi/4"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atan(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert -0.785 == float(data[0].text[:6]), "atan(-1) != -pi/4"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atan(1000000)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1.5707 == float(data[0].text[:6]), "atan(1000000) != pi/2"


def test_sqrt(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sqrt(4)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 2 == float(data[0].text), "sqrt(4) != 2"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sqrt(2)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "1.414" == data[0].text[:5], "sqrt(2) != 1.414"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sqrt(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1 == float(data[0].text), "sqrt(1) != 1"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sqrt(2.25)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1.5 == float(data[0].text), "sqrt(2.25) != 1.5"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sqrt(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower(), "negative root should fail"


def test_power(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2^2")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 4 == float(data[0].text), "2^2 != 4"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2**2")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 4 == float(data[0].text), "** should work alongside ^"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2^-1")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0.5 == float(data[0].text), "2^-1 != 1/2"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2^0.5")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1.414 == float(data[0].text[:5]), "2^0.5 != 1.414"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2^0")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1 == float(data[0].text), "2^0 != 1"


def test_hyperbolics(hallo_getter):
    test_hallo = hallo_getter({"math"})
    # Cosh
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc cosh(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1 == float(data[0].text), "cosh(0) != 1"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc cosh(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1.543 == float(data[0].text[:5]), "cosh(1) != 1.543"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc cosh(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1.543 == float(data[0].text[:5]), "cosh(-1) != 1.543"
    # Sinh
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sinh(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "sinh(0) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sinh(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1.175 == float(data[0].text[:5]), "sinh(1) != 1.175"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc sinh(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert -1.175 == float(data[0].text[:6]), "sinh(-1) != -1.175"
    # Tanh
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc tanh(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "tanh(0) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc tanh(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0.761 == float(data[0].text[:5]), "tanh(1) != 0.761"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc tanh(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert -0.761 == float(data[0].text[:6]), "tanh(-1) != -0.761"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc tanh(1000000)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1 == float(data[0].text), "tanh(1000000) != 1"
    # Acosh
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc acosh(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower(), "acosh(0) should fail"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc acosh(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "acosh(1) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc acosh(4)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 2.063 == float(data[0].text[:5]), "acosh(4) != 2.063"
    # Asinh
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc asinh(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "asinh(0) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc asinh(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0.881 == float(data[0].text[:5]), "asinh(1) != 0.881"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc asinh(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert -0.881 == float(data[0].text[:6]), "asinh(-1) != -0.881"
    # Atanh
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atanh(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0 == float(data[0].text), "atanh(0) != 0"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atanh(0.5)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 0.549 == float(data[0].text[:5]), "atanh(0.5) != 0.549"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atanh(-0.5)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert -0.549 == float(data[0].text[:6]), "atanh(-0.5) != -0.549"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atanh(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower(), "atanh(1) should fail"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc atanh(2)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text.lower(), "atanh(2) should fail"


def test_gamma(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc gamma(1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 1 == float(data[0].text), "gamma(1) != 1"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc gamma(5)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert 24 == float(data[0].text), "gamma(5) != 24"
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc gamma(0)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "error" in data[0].text, "gamma(0) should fail"


def test_passive(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "25")
    )
    data = test_hallo.test_server.get_send_data(0)
    assert len(data) == 0, "No response should have happened."
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "23.47")
    )
    data = test_hallo.test_server.get_send_data(0)
    assert len(data) == 0, "No response should have happened."
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "2+2")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert data[0].text == "4", "2+2 = 4, hallo should have responded"
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "pie")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert 8.539 == float(data[0].text[:5]), "Response should have been received."
    evt_msg = EventMessage(
        test_hallo.test_server,
        test_hallo.test_chan,
        test_hallo.test_user,
        "cos(acos(sin(asin(tan(atan(acosh(cosh(sinh(asinh(tanh(atanh(0))))))))))))",
    )
    test_hallo.function_dispatcher.dispatch_passive(evt_msg)
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
    assert len(data) != 0, "Response should have been received."
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "acos(2)")
    )
    data = test_hallo.test_server.get_send_data(0)
    assert len(data) == 0, "No response should have been received"
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, " 97")
    )
    data = test_hallo.test_server.get_send_data(0)
    assert len(data) == 0, "No response should have been received"
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "9 7")
    )
    data = test_hallo.test_server.get_send_data(0)
    assert len(data) == 0, "No response should have been received"


def test_passive_ip_error(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch_passive(
        EventMessage(test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "127.0.0.1")
    )
    data = test_hallo.test_server.get_send_data(0)
    assert len(data) == 0, "No response should have happened."


def test_ee(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc ee")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text != "0", "Improper processing of constants."
    assert data[0].text[:5] == "7.389", "Incorrect answer produced by e*e calculation."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc pipi")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert data[0].text != "0", "Improper processing of constants."
    assert (
        data[0].text[:5] == "9.869"
    ), "Incorrect answer produced by pi*pi calculation."


def test_equals(hallo_getter):
    test_hallo = hallo_getter({"math"})
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2+2=4")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "4=4" in data[0].text, "Answer was not correctly found."
    assert "not right" not in data[0].text, "This calculation (2+2=4) is right."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc 2+2=5")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "4=5" in data[0].text, "Answer was not correctly calculated."
    assert "not right" in data[0].text, "This calculation (2+2=5) is not right."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc pi=acos(-1)")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "3.141" in data[0].text, "Pi should be in response."
    assert "=3.141" in data[0].text, "Answer should be pi."
    assert "not right" not in data[0].text, "This calculation (pi=acos(-1)) is right."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc circle constant=pi")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "3.141" in data[0].text, "Pi should have been evaluated."
    assert (
        "circle constant=3.141" in data[0].text
    ), "Text should have been left unchanged."
    assert "not right" not in data[0].text, "Numbers are not incorrect here."
    assert "no calculation" not in data[0].text, "There is a calculation here."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc hello=goodbye")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "hello=goodbye" in data[0].text, "Text should not be changed."
    assert "no calculation" in data[0].text, "There is no calculation here."
    assert (
        "not right" not in data[0].text
    ), "Should not say a user's non-calculation text is not right."
    test_hallo.function_dispatcher.dispatch(
        EventMessage(test_hallo.test_server, None, test_hallo.test_user, "calc x=2+2=y=5")
    )
    data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
    assert "x=4=y=5" in data[0].text, "Calculation should have been parsed and ran."
    assert "no calculation" not in data[0].text, "There is a calculation here."
    assert (
        "not right" in data[0].text
    ), "Not all numbers here are the same, they are not equal."
