def test_application_create(application):
    assert application, "Приложение не создано"


def test_application_get_token(application):
    assert application.id_token, "Токен не получен"


def test_application_get_metadata(application):
    assert len(application.channels) > 0, "Каналы не получены"


def test_application_get_runtime_channels(application):
    assert application.receiver, "Receiver канал не получен"
    assert application.sender, "Sender канал не получен"


def test_application_get_amqp_url(application):
    assert application.amqp_url, "AMQP URL не получен"
