from model.chart import Chart


def test_chart():
    c1 = Chart('eric-enm-pre-deploy-integration', 'some_url')
    c2 = Chart('some_other_chart', 'some_url')
    assert c1.alias == 'pre-deploy'
    assert c2.alias == 'some_other_chart'
