# Using py.test framework
from service import Intro, MNIST


def test_example_message(client):
    """Example message should be returned"""
    client.app.add_route('/mnist', Intro())

    result = client.simulate_get('/mnist')
    assert result.json == {
        'message': 'This service verifies a model using the MNIST Test data set. '
                   'Invoke using the form /mnist/<index of test sample>. For example, /mnist/24'}, \
        "The service test will fail until a trained model has been approved"


def test_classification_request(client):
    """Expected classification for Iris sample should be returned"""
    client.app.add_route('/mnist/{index:int(min=0)}', MNIST())

    result = client.simulate_get('/mnist/1')
    assert result.status == "200 OK", "The service test will fail until a trained model has been approved"
    assert all(k in result.json for k in (
        "index", "predicted_label", "predicted")), "The service test will fail until a trained model has been approved"
