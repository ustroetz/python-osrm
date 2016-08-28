# -*- coding: utf-8 -*-
import unittest
try:
    from unittest import mock
except:
    import mock

try:
    from urllib.request import URLError
except:
    from urllib2 import URLError

from pandas import DataFrame
from geopandas import GeoDataFrame
import numpy

import osrm


class MockReadable:
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content.encode('utf-8')


class TestOsrmWrapper(unittest.TestCase):
    def setUp(self):
        pass

    def test_helpers(self):
        _list = [i for i in osrm._chain([789, 45], [78, 96], [7878, 789, 36])]
        self.assertEqual(_list, [789, 45, 78, 96, 7878, 789, 36])

        p1 = osrm.Point(latitude=10.00, longitude=53.55)
        self.assertEqual(p1.latitude, p1[0])
        self.assertEqual(p1.longitude, p1[1])

    def test_RequestConfig(self):
        default_host = osrm.RequestConfig.host

        # Make a new RequestConfig object
        MyConfig = osrm.RequestConfig()
        MyConfig.host = "http://0.0.0.0:5000"  # Only change the host
        # ..so the profile and the version should remain unchanged
        self.assertEqual(str(MyConfig), "http://0.0.0.0:5000/*/v1/driving")

        # Make a new one by writing directly the pattern to use :
        MyOtherConfig = MyConfig("192.168.1.1/v1/biking")
        self.assertEqual(MyOtherConfig.profile, "biking")

        # Two equivalent ways are available to write the url pattern :
        MyOtherConfig2 = MyConfig("192.168.1.1/*/v1/biking")
        self.assertEqual(str(MyOtherConfig), str(MyOtherConfig2))

        # Parameters from the original RequestConfig object haven't changed:
        self.assertEqual(osrm.RequestConfig.host, default_host)

    @mock.patch('osrm.core.urlopen')
    def test_nearest(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u"""{"waypoints":[{"distance":22064.816067,"hint":"YtOXh5LYdIgAAAAAAAAAAH0FAAAAAAAA-1IAAD2o_wUlqP8FbrcAAC6OdgIrck4BEL95AngUTwEAAAEBfDhq3w==","name":"","location":[41.324078,21.918251]}],"code":"Ok"}"""
            )
        result = osrm.nearest((41.5332, 21.9598))
        # nearest only return the parsed JSON response
        self.assertEqual(result["waypoints"][0]["distance"], 22064.816067)

    @mock.patch('osrm.core.urlopen')
    def test_simple_route(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","routes":[{"legs":[{"steps":[],"summary":"","duration":14821.6,"distance":256884.8}],"geometry":"a|wdCobf{F}|@h]}pC`dAmpAbh@qTvTob@d_@sJfEcQvBeJtJcGjNiM~Hqe@~Mcn@`P{i@vFgPn@}HtBeGz@{Md@gGxAoGhCwEh@y_@lBmM|@ac@dLsc@nJmh@|Jot@zEeUXoWtEsRpBmRd@o`@`Eab@fGka@nDYB|a@va@gDAyEmCoFqC}K_FkHqCy_@iNsLmEiFuB}EuBgHgDwC_BwCaBwFmD_@UqMcJkJ}H_JmImI_JiJyLwIgMaTm\\\\waBqiCqaAqxAwfDq`FszFeuH_tCyaEuVs[alAgtAoTcV`AcA|FsGl@k@dK{KxE_FzGoHb^k^lFgGxMkQxGwKjpAksBlGoKnNyW~Xyj@fh@gdAzRka@hCsGlJwVxGuVlL{g@|Jae@pS{~@jCqJfCuGnFwLxDuGtDaGvCwDtDyEfEcElzA{sAxKmKtH_IvFcInHuM`EgKjDuLxB_LxAgNx@uPA{U@sGJgGFiAAcDdA}KtBqLbGcS`m@ydBzTmk@hz@uqBnOm]~LeVlM_TfXcc@ncAe`BlKsQ|GuNnSyn@`]_gAfUis@tI}SjLgTzv@ccAv@W`LiNbh@ip@nOcSlK{Plr@}zA|Tmf@lTye@nUqf@jz@u{AfTk`@rGqObH}TdYyeAzRiu@vE_QbHsSfF_M`f@yiAvoAexCrTog@hOy_@rFgR`GwW?aBdp@{xCvlAsvDnJi\\\\|Fo\\\\xDs`@xRqiClBaW~Fio@Fg@bCaRpUmpAbDcR`EoUPuAdAyHtB}P\\\\qEf@_DZqDvCv@`rAl^fPnEbT`Hh@`@BBBBB?DBF?D?FCZDxtAbf@`GnBzt@lUbZjJvWfIvAd@~d@`ObEjA|JlEfAd@h~Ap{@dUrLjTzJb\\\\bIdNnBxTtA|\\\\Zds@mCbZj@j[bEvTtHn`@hMx}@nUjk@lPd^zNrcCleAl`@jOhYrFxpC`WbWnEhNfDfM~HjaAnn@nPdJvRdG|bDnx@nUtMxd@jYnw@ng@pr@j\\\\dRhKzNpIrKnL~Zx_@bW|\\\\fMpI|NjHnP`FhuC~j@~O`F~IhKpEpIr`@x|@vNb\\\\NXjLfU^r@`KxN`Q`MtQdJvvAxg@hC~@FBVH~DnArj@dQ~`@vJr_Bd[vc@tJle@`PfXfNfwBbqAhY|Rn`@|\\\\lZzUt\\\\bTnf@zU`VjRdL~OxMlYpUl`@vR`Wd]dQ~iCzz@hShKbb@`^fc@hUt\\\\pSbyA`cA`KlEvRlE|HiAzHaFjrBclB`PcJbQuFfRyDhS}ApPb@zMbCdR`FfRbJjSjRdLvQpEnLjHbTrKpd@pEhKlI~HvLdGtKpBlnHra@rP`CxMvCbiBjj@nOvJrPfN`K|R~IpSnDdQdA`WdQhjFjClOrEnLzHtJnOjHtl@hNjNb@nOgD~Id@bK|Hjn@`XjIrEdFlBpEnBbD|AvDnB`F|CnCfBbC`BfDnCfBvAxCjCfFzD|EhDfEjCxGrDrF|CfL|FhSnJfDjBvBf@~A^n@Vp@ThBd@x@\\\\`@Pj@Vt@`@X\\\\JNh@b@\\\\VxBhBx@l@d@Zp@f@|@jAxAnBbArAx@xAHRr@zAXp@CTBRLLNHR?BABCb@FhAPrE|@dJbB~FdBjBj@dGhBnA^rA`@pA`@h@JTD\\\\FxBj@fF|Aj@PzAb@rNhEPDxEvAlF~AVHrDdA~FfBt@XL]lq@afBdBaGb@qBtAuGFc@DKBMIY}BeBaXqZoB_FYyE@kHi@kE_Jg_@EkG?aKvAcRbAgFbDkHfCcIrQsg@dBwHvCmZjB}JpAqGNqF]oLc@}C_BkC{BwAwDgAwCqC{@}CaCoVUaYo@yFyCqPoBoDiHeIcBcDyCwM}CkOmBgGoCqG}EkJoX_h@_Qy[yAaHsDgWe@}CoAgDgDqEkb@}b@oB}CkGePgV}f@{CiEkF{E{XiPgHkFcBuCs@qCKyEjF{w@VyE?sIk@iG_CwV{Kmy@g@mEKsGvAktAbBc~Ar@u~@jAwfACwF_@cHg@wGsBqIcEsRsBuGoBiEeCoD}[o[uEiFiCgEwBgFo@{CsAcGoByJwFu[w@eDcB_HiDeMaBaHaCqNyAeJkAmM@kIVuUb@_[b@oSLaWr@_[d@oJrAaFI}X^kMTqLo@yHqCaMmAeG{@qJDcIZqGv@qKfE_p@V_DQ{BCcAiGi[g@gCc@oEMeEOiGiAsg@]{PeAek@","duration":14821.6,"distance":256884.8}],"waypoints":[{"hint":"YtOXh5LYdIgAAAAAAAAAAH0FAAAAAAAA-1IAAD2o_wUlqP8FbrcAAC6OdgIrck4BEL95AngUTwEAAAEBfDhq3w==","name":"","location":[41.324078,21.918251]},{"hint":"apH5jEvnv40AAAAAYAEAAAAAAAC_LQAA42gAAHZ5UQZhQk4IbrcAAFxqgAK9REQBFHOAAqgvRQFOAAEBfDhq3w==","name":"","location":[41.970268,21.251261]}]}'''
            )
        result = osrm.simple_route((41.5332, 21.9598), (41.9725, 21.3114),
                                   output="routes",
                                   geometry="wkt")

        # Only the "routes" part from the response should have be returned :
        self.assertIsInstance(result, list)

        # ... with geometry field transformed to WKT :
        self.assertIn("LINESTRING", result[0]["geometry"])

    @mock.patch('osrm.core.urlopen')
    def test_table_only_origins(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
        u'''{"code":"Ok","durations":[[0,1559.9,4192.8,9858.4,7679.7],[1579.3,0,5300.6,8735.2,6507.6],[4214.7,5334,0,5671.5,3972.1],[9496.8,8354.6,5689.7,0,2643.2],[7270.1,6127.9,3971.5,2624.5,0]],"destinations":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}],"sources":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}]}'''
        )
        names = ['name1', 'name2', 'name3', 'name4', 'name5']
        coords = [[21.0566163803209, 42.004088575972],
                  [21.3856064050746, 42.0094518118189],
                  [20.9574645547597, 41.5286973392856],
                  [21.1477394809847, 41.0691482795275],
                  [21.5506463080973, 41.3532256406286]]
        durations, new_coords, _ = osrm.table(coords,
                                              ids_origin=names,
                                              output="pandas")
        self.assertIsInstance(durations, DataFrame)
        durations2, new_coords2, _ = osrm.table(coords,
                                                ids_origin=names,
                                                output="np")
        self.assertIsInstance(durations2, numpy.ndarray)
        self.assertEqual(durations.values.tolist(), durations2.tolist())

    @mock.patch('osrm.core.urlopen')
    def test_table_OD(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","durations":[[10785.3,9107,14619.6,5341.2],[9546.8,7934.9,15473,4054.3],[14559.4,12440.7,18315.9,9115.3],[14463.4,10768.4,22202.6,9904],[12236.7,8541.7,19975.9,7677.3]],"destinations":[{"hint":"XAiehPiqpY4_JQUAZQAAAA0BAACzBQAAVwEAALxM2gRcSLAIbrcAABnMXwGE7IAC2NBfASDugAINAAEBfDhq3w==","name":"1061","location":[23.055385,42.003588]},{"hint":"qdjCi1mz-4wAAAAAFgAAAAAAAABzEgAAKQgAABae8wfvnfMHbrcAAHmQVQErD4ECwJNVATgDgQK6AAEBfDhq3w==","name":"","location":[22.384761,42.012459]},{"hint":"lfafieL2n4kAAAAAAAAAADIAAABbAAAAPQYAAEz6EwdiWKIFbrcAADTGPwF-M5gC2Mg_AZgxmAIDAAEBfDhq3w==","name":"","location":[20.956724,43.529086]},{"hint":"8gQxizUOMYsAAAAAAAAAABsAAAAAAAAAQRkAANIcvgd1Hb4HbrcAADQQSQEqrn0CCNZIAdinfQIAAAEBfDhq3w==","name":"","location":[21.565492,41.791018]}],"sources":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}]}'''
            )
        origins = [[21.0566163803209, 42.004088575972],
                   [21.3856064050746, 42.0094518118189],
                   [20.9574645547597, 41.5286973392856],
                   [21.1477394809847, 41.0691482795275],
                   [21.5506463080973, 41.3532256406286]]
        destinations = [[23.0566, 42.004], [22.3856, 42.0094],
                        [20.9574, 43.5286], [21.5506, 41.7894]]

        durations, snapped_origins, snapped_destinations = \
            osrm.table(origins, destinations)

        self.assertIsInstance(durations, numpy.ndarray)

        expected_shape = (len(origins), len(destinations))
        self.assertEqual(durations.shape, expected_shape)
        self.assertTrue(durations.any())

    def test_non_existing_host(self):
        Profile = osrm.RequestConfig("localhost/v1/flying")
        self.assertEqual(Profile.host, "localhost")
        with self.assertRaises(URLError):
            osrm.nearest((12.36, 45.36), url_config=Profile)
        with self.assertRaises(URLError):
            osrm.trip(
                [(13.38886, 52.51703), (10.00, 53.55), (52.374444, 9.738611)],
                url_config=Profile)
        with self.assertRaises(URLError):
            osrm.simple_route(
                (13.38886, 52.51703), (10.00, 53.55), url_config=Profile)
        with self.assertRaises(URLError):
            osrm.AccessIsochrone(
                (13.38886, 52.51703), points_grid=100, url_config=Profile)
        with self.assertRaises(URLError):
            osrm.match(
                [(10.00, 53.55), (52.374444, 9.738611)], url_config=Profile)
        with self.assertRaises(URLError):
            osrm.table(
                [(10.00, 53.55), (52.374444, 9.738611)],
                [(10.00, 53.55), (52.374444, 9.738611)],
                url_config=Profile)

    @mock.patch('osrm.core.urlopen')
    def test_accessibility(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","durations":[[6924.8,6389.6,7313.6,8356.7,9011,6253.4,6054.6,4462.2,6133.3,6779.8,6138.5,2289.3,2414.2,2472.8,3920.2,4375.4,5580.1,6506.5,5472.3,1657.7,1648.1,2197.3,2938.4,4451.1,4721.7,4198.7,5044.5,1034.4,729.7,2290.2,4911.3,4353.3,4244.2,3712.6,1610.5,676,704.2,3083.6,6121.6,6132.9,3625.2,3131.4,2042.5,1637.5,1635.3,5396.5,7891.1,5753.5,4248.4,4272.6,3064.2,2459.2,2090.2,4464.3,9555.2,6675.5,4861.1,4776.1,3054.2,2336.8,3072.6,4258.5,6444.1,9452.4]],"destinations":[{"hint":"K9UHiUTVB4nG6PIAAAAAAA4AAADtAAAAHAAAAMD7xAZl_MQGE_sAADbpOwF-RIYCOPU7AahFhgIJAAEB9TrYrw==","name":"Retij\xc3\xab - Opterush\xc3\xab","location":[20.703542,42.35379]},{"hint":"9PGug7rB-4gAAAAAFQAAAAoAAABXAwAAewAAAJ9sigdmVb8GE_sAAArvOwFOt4QCOPU7AQi_hAIZAAEB9TrYrw==","name":"","location":[20.705034,42.25211]},{"hint":"S4wXiVaMF4kAAAAAAAAAAA8AAAAAAAAAEAAAAPLlzQbz5c0GE_sAAHbtOwH_TIMCOPU7AWg4gwIAAAEB9TrYrw==","name":"","location":[20.70463,42.159359]},{"hint":"eFX9iO3_lIsAAAAAAAAAABIAAAAAAAAAHwAAAAwNwAb7DMAGE_sAADffOwHzsYECOPU7AcixgQIAAAEB9TrYrw==","name":"","location":[20.700983,42.054131]},{"hint":"m4QXiaD1OY4AAAAAFgAAAAAAAAALAQAAAAAAABbizQaW4c0GE_sAAO8HPAGEVIACOPU7ASgrgAIHAAEB9TrYrw==","name":"","location":[20.711407,41.964676]},{"hint":"f9wYi4HcGIsAAAAAMQAAAAAAAABZCAAAAAAAAES9tAc8vbQHE_sAAAP6OgHErH4COPU7AYikfgJlAAEB9TrYrw==","name":"","location":[20.642307,41.856196]},{"hint":"CmwBig1sAYoAAAAAEQAAAAoAAAB7NgAAZgAAAAE2BQTo6T4HE_sAAO_iOwFmLH0COPU7AegdfQJNAQEB9TrYrw==","name":"","location":[20.701935,41.757798]},{"hint":"REauhG7WqIlUUp4AEAAAAAAAAAAQCQAABxsAAKeNMgEdx-4DE_sAAG4IPAGil3sCOPU7AUiXewIAAQEB9TrYrw==","name":"R2238","location":[20.711534,41.654178]},{"hint":"63_iie1_4okAAAAAEQAAABAAAAAfAAAAQwAAAFwwMQc_MDEHE_sAAOh9PQGGP4YC2Hs9AahFhgIBAAEB9TrYrw==","name":"","location":[20.807144,42.352518]},{"hint":"6bLaiQiz2okAAAAAAAAAAAkAAAAAAAAAjQAAADq3LQexty0HE_sAAP1dPQH_yYQC2Hs9AQi_hAIAAAEB9TrYrw==","name":"","location":[20.798973,42.256895]},{"hint":"FD8NikM_DYoAAAAAAAAAABUAAACVCgAArwkAALmjRAeao0QHE_sAAPOAPQGYNoMC2Hs9AWg4gwKwAAEB9TrYrw==","name":"","location":[20.807923,42.153624]},{"hint":"akb8iYWPAYoAAAAAAAAAABUAAACVCQAAAAAAADYNQgM9IHkBE_sAAPTNPQFetIEC2Hs9AcixgQJQAAEB9TrYrw==","name":"","location":[20.827636,42.05475]},{"hint":"_9D0iS6HAYoAAAAAFQAAAAAAAACGBAAAAAAAAOZaOQeu-D4HE_sAALNJPgEHB4AC2Hs9ASgrgAJLAAEB9TrYrw==","name":"","location":[20.859315,41.944839]},{"hint":"E4cBihiHAYoAAAAAAAAAACoAAAAAAAAAvQEAAMX4PgfE-D4HE_sAAM9ePgHBk34C2Hs9AYikfgIAAAEB9TrYrw==","name":"","location":[20.864719,41.849793]},{"hint":"B3QBinegG48AAAAAAAAAABEAAADJBQAAfQAAADv1xAg89cQIE_sAANJ3PQEBNX0C2Hs9AegdfQI2AAEB9TrYrw==","name":"","location":[20.805586,41.760001]},{"hint":"4ThEjuI4RI4AAAAAAAAAAAQAAAAWAAAAfAAAAK-srgKurK4CE_sAAGYHPQEA6HsC2Hs9AUiXewIBAAEB9TrYrw==","name":"","location":[20.776806,41.674752]},{"hint":"Jc3uiV3N7okAAAAACgAAAAAAAADOAAAA6gAAAISXNgf8ljYHE_sAAFj1PgEqVIYCeAI_AahFhgINAAEB9TrYrw==","name":"","location":[20.903256,42.357802]},{"hint":"OYTiidYe54kAAAAALwAAAAAAAACpAQAAAAAAAK4yMQf3KAMGE_sAAHk0PwHHJ4UCeAI_AQi_hAIXAAEB9TrYrw==","name":"","location":[20.919417,42.280903]},{"hint":"6hg2iiE1lo8AAAAAFwAAAAAAAACVAgAAAAAAAGd5KgM8oc0BE_sAAMrTPgFGdIMCeAI_AWg4gwIhAAEB9TrYrw==","name":"","location":[20.894666,42.169414]},{"hint":"AUD8iYKPAYp7gf8AAAAAAAwAAABuAwAA_AUAAOt5PAd8eTwHE_sAAO_wPgGaq4ECeAI_AcixgQJKAAEB9TrYrw==","name":"R29275","location":[20.902127,42.052506]},{"hint":"6cb0iYLH9IkAAAAAAAAAAAkAAACVDQAAdQUAAIxWOQfmVTkHE_sAAE0DPwG4KoACeAI_ASgrgAJsAQEB9TrYrw==","name":"","location":[20.906829,41.953976]},{"hint":"ZlPliQxCMIwAAAAAJQAAAAAAAACjBAAATAMAAP-OFwj6jhcIE_sAAC0BPwE1oH4CeAI_AYikfgIiAAEB9TrYrw==","name":"","location":[20.906285,41.852981]},{"hint":"5zwQisOwNYwAAAAAGAAAAAAAAADcCQAAaAYAAB_9RQfr_UUHE_sAAJbNPgF7MH0CeAI_AegdfQJQAAEB9TrYrw==","name":"","location":[20.893078,41.758843]},{"hint":"Q696i-NmOY4AAAAAHAAAAAAAAADLBwAAAAAAAJyzmQiis5kIE_sAANAMPwEYXXsCeAI_AUiXewJAAAEB9TrYrw==","name":"","location":[20.909264,41.639192]},{"hint":"IFKwh0PdGougcQsBCgAAAAAAAAC3HgAAiAUAAETAWwQ6kbUHE_sAANKTQAHHVoYCGIlAAahFhgKpAQEB9TrYrw==","name":"R-206 (206)","location":[21.009362,42.358471]},{"hint":"RYkii5OJIosAAAAACAAAAAAAAABnAAAAAAAAADaXuAdOlrgHE_sAAAO-QAFjn4QCGIlAAQi_hAILAAEB9TrYrw==","name":"","location":[21.020163,42.245987]},{"hint":"y6LrirscNYsAAAAAPAAAAAAAAABTBAAAAAAAANxQiAJidCUDE_sAAK4AQAHASYMCGIlAAWg4gwIJAAEB9TrYrw==","name":"","location":[20.971694,42.158528]},{"hint":"FbJ_i9TrgosAAAAAAAAAABIAAACwBQAA6AkAAH87LQMXOdsHE_sAAOuFQAGesoECGIlAAcixgQKHAAEB9TrYrw==","name":"","location":[21.005803,42.054302]},{"hint":"idevhZobsIUAAAAAAAAAACQAAAB2CAAA9gUAAMqxwARzTsUEE_sAAOegQAGrLYACGIlAASgrgAJGAAEB9TrYrw==","name":"","location":[21.012711,41.954731]},{"hint":"npeRjFCYkYwAAAAAAAAAABIAAAB4AwAAkwEAABWUdQfbXDIIE_sAACJ2QAFagH4CGIlAAYikfgIMAAEB9TrYrw==","name":"","location":[21.001762,41.844826]},{"hint":"ajW4i7KPHo8AAAAAAAAAADYAAADRNgAAmyYAAN_27wem-O8HE_sAAMesQAGyOn0CGIlAAegdfQK8AgEB9TrYrw==","name":"","location":[21.015751,41.761458]},{"hint":"Ls3fid5Z5YkAAAAAHAAAAAAAAAA-FAAAjwUAAIp6MgeDejIHE_sAAAmTQAFap3sCGIlAAUiXewLZAAEB9TrYrw==","name":"","location":[21.009161,41.658202]},{"hint":"OrLrijHyKY4AAAAANQAAAAAAAABhAAAAlQIAAA79ogcX_aIHE_sAADEOQgHnJ4YCuA9CAahFhgICAAEB9TrYrw==","name":"","location":[21.106225,42.346471]},{"hint":"eMOhj4vDoY8AAAAAMgAAAAAAAAAbAQAAkwEAAFq3qgQ9k5kDE_sAAI8RQgFCyoQCuA9CAQi_hAIHAAEB9TrYrw==","name":"","location":[21.107087,42.256962]},{"hint":"eqQrhKqkK4QAAAAAAAAAACgAAAASAwAAhwAAALB_ggOyv4EDE_sAAC_0QQEUFoMCuA9CAWg4gwILAAEB9TrYrw==","name":"","location":[21.099567,42.1453]},{"hint":"upohhIiZ54wAAAAAHAAAAAAAAACLAgAAfgAAAFRvSQhJvfoAE_sAAD4cQgFyr4ECuA9CAcixgQILAAEB9TrYrw==","name":"","location":[21.109822,42.05349]},{"hint":"FoLljEuC5YwAAAAAAAAAADQAAADRBQAAKwQAAHdKyQUplwQDE_sAAP_8QQE_PYACuA9CASgrgAIcAAEB9TrYrw==","name":"","location":[21.101823,41.958719]},{"hint":"xYzljMiM5YwAAAAAAAAAADQAAAC9AgAAAQQAANHoSAjpCI4DE_sAAC0EQgH_n34CuA9CAYikfgIUAAEB9TrYrw==","name":"","location":[21.103661,41.852927]},{"hint":"azm4i9GJHY8AAAAAAAAAAA4AAACyBwAAxQAAAK3tSAhv-O8HE_sAAHT0QQHsDn0CuA9CAegdfQI_AAEB9TrYrw==","name":"","location":[21.099636,41.750252]},{"hint":"HojmjC6I5owAAAAAFwAAAAAAAAC5GAAAcgAAAE41SQhMNEkIE_sAAM1uQgGUqHsCuA9CAUiXewLQAAEB9TrYrw==","name":"","location":[21.130957,41.658516]},{"hint":"opfEjovLz46xMpEAPgAAADwAAAB5AgAAHQMAAFFVGgN0aI8DE_sAAMacQwHoOoYCWJZDAahFhgIHAAEB9TrYrw==","name":"KFORIT","location":[21.208262,42.351336]},{"hint":"VAmgj1cJoI8AAAAAMgAAAAAAAAAAAwAAAAAAAJ9tmANsqbIHE_sAABiJQwF_vIQCWJZDAQi_hAIOAAEB9TrYrw==","name":"","location":[21.203224,42.253439]},{"hint":"EmmsjxRprI8AAAAADAAAAAAAAADPAAAAAAAAAOpqWQPpalkDE_sAAHZfQwEjXIMCWJZDAWg4gwIHAAEB9TrYrw==","name":"","location":[21.192566,42.163235]},{"hint":"oVIUi6VSFIsAAAAAAAAAADYAAAAAAAAA6QAAAELtsgeu67IHE_sAAMfOQwGWFYICWJZDAcixgQIAAAEB9TrYrw==","name":"","location":[21.221063,42.079638]},{"hint":"ZRspi3QbKYsAAAAAAAAAAAkAAABrAAAA8Q4AAD39ugc3_LoHE_sAAJemQwG8KYACWJZDASgrgAIHAAEB9TrYrw==","name":"","location":[21.210775,41.953724]},{"hint":"5thjiSwHnIkAAAAAAAAAAAoAAADwBAAA0TEAADTH9gZrSEQGE_sAAF6JQwH3-H4CWJZDAYikfgI-AAEB9TrYrw==","name":"","location":[21.203294,41.875703]},{"hint":"mHpYi78puIsAAAAAAAAAAAYAAABxHwAAawcAAI2jzAeOpcwHE_sAAHfAQwEEAX0CWJZDAegdfQInAgEB9TrYrw==","name":"","location":[21.217399,41.746692]},{"hint":"hYN1itSEdYr0FpQABgAAAAAAAAA7AAAACAQAAC10cQc8dHEHE_sAAP6SQwFgonsCWJZDAUiXewIFAAEB9TrYrw==","name":"R2132","location":[21.205758,41.656928]},{"hint":"QYU4i4aO440AAAAAAQAAAA4AAABCAAAAKgAAADnCwAdCwsAHE_sAAKkcRQGuRoYC-BxFAahFhgIEAAEB9TrYrw==","name":"","location":[21.306537,42.35435]},{"hint":"gh8Dj0EkA49J9asAGgAAAAAAAAClAAAAAAAAAN_mEwBchOACE_sAAHQlRQE-tYQC-BxFAQi_hAIJAAEB9TrYrw==","name":"Kulla","location":[21.308788,42.251582]},{"hint":"iV43i51eN4snqgwBDAAAAAQAAABbAgAAAgEAAFw6wAdNOsAHE_sAAHEcRQGeOIMC-BxFAWg4gwIoAAEB9TrYrw==","name":"Isen Suma","location":[21.306481,42.154142]},{"hint":"k4vJhDEcLosAAAAALQAAAEYAAAAcBAAA7gAAAIhyXwSBxcgGE_sAAA4eRQG_s4EC-BxFAcixgQIqAAEB9TrYrw==","name":"","location":[21.306894,42.054591]},{"hint":"y8UIic7FCIkAAAAADAAAAAAAAADQAQAABQAAADOKxQYvisUGE_sAABr9RAFAJIAC-BxFASgrgAIYAAEB9TrYrw==","name":"","location":[21.298458,41.95232]},{"hint":"fyrkiYUq5IkAAAAAFAAAAAAAAADJEQAA6woAALn2SgOy9koDE_sAAHtbRQHclX4C-BxFAYikfgIsAQEB9TrYrw==","name":"","location":[21.322619,41.850332]},{"hint":"PwKciRnJnYkAAAAALwAAAAAAAAA8LgAAAAAAAKegRgAMcxIHE_sAAH9rRAGaJ30C-BxFAegdfQJnAgEB9TrYrw==","name":"","location":[21.261183,41.75657]},{"hint":"ANDaiGlECI4AAAAAAAAAADYAAAAaEwAAnwwAAJjTrgb-Yo4IE_sAAGfNRAF2cHsC-BxFAUiXewJDAAEB9TrYrw==","name":"","location":[21.286247,41.64415]},{"hint":"4ok4i-OJOIsAAAAAAAAAAAoAAAD8BQAA_AAAAL7EwAdQxMAHE_sAAHO1RgHWUoYCmKNGAahFhgIxAAEB9TrYrw==","name":"","location":[21.411187,42.357462]},{"hint":"9Csai5y5RosAAAAACwAAAAAAAAATAwAAZwUAAKfTfADibssCE_sAAMujRgGHv4QCmKNGAQi_hAI6AAEB9TrYrw==","name":"","location":[21.406667,42.254215]},{"hint":"NHRBiT8AwIkAAAAAFgAAAAAAAAAzAQAAAAAAAF-aIQdpmiEHE_sAAKTDRgH744ICmKNGAWg4gwIQAAEB9TrYrw==","name":"","location":[21.41482,42.132475]},{"hint":"pmk-hP___3_Vq5AAxQAAAH4BAADuAAAAtAEAAMVHkAPAR5ADE_sAAKOjRgEhroECmKNGAcixgQIHAAEB9TrYrw==","name":"\xd0\x9c\xd0\xb0\xd1\x98\xd0\xba\xd0\xb0 \xd0\xa2\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb7\xd0\xb0 (A2;A4)","location":[21.406627,42.053153]},{"hint":"uGU8hLxlPIQlqJUAAAAAAAUAAAAQAgAAZgEAAP1AkAPYQJADE_sAAFOqRgEqGYACmKNGASgrgAIrAAEB9TrYrw==","name":"R2134","location":[21.408339,41.949482]},{"hint":"QTXyjEw18owAAAAAAAAAAAwAAABsAAAAbgAAAKpxTAjWcEwIE_sAAJOpRgEKs34CmKNGAYikfgIGAAEB9TrYrw==","name":"","location":[21.408147,41.857802]},{"hint":"HTTaiCA02ogAAAAAAAAAADEAAAAAAAAAGA8AAJGHrgZkiK4GE_sAAHjtRgFxsX0CmKNGAegdfQIAAAEB9TrYrw==","name":"","location":[21.425528,41.791857]},{"hint":"h1jaiIhY2ogAAAAADgAAAAAAAAABEAAAWwAAAD-crgZCnK4GE_sAAASRRgFwTnsCmKNGAUiXewJyAAEB9TrYrw==","name":"","location":[21.40186,41.63544]}],"sources":[{"hint":"ZVKXhLuOHY8AAAAAAQAAAAoAAAAAAAAANwUAAE4HKQNNBykDE_sAAGdMQQF37oACaExBAXjugAIAAAEB9TrYrw==","name":"","location":[21.056615,42.004087]}]}'''
                )

        center_pt = osrm.Point(latitude=21.0566163, longitude=42.0040885)
        n_class = 8

        Accessibility = osrm.AccessIsochrone(center_pt, points_grid=100)
        snapped_center_point = Accessibility.center_point
        gdf = Accessibility.render_contour(n_class=n_class)

        self.assertIsInstance(snapped_center_point, osrm.Point)
        self.assertIsInstance(gdf, GeoDataFrame)
        self.assertEqual(n_class, len(gdf))

        n_class = 5
        gdf = Accessibility.render_contour(n_class=n_class)
        self.assertEqual(n_class, len(gdf))

        n_class = 10
        gdf = Accessibility.render_contour(n_class=n_class)
        self.assertEqual(n_class, len(gdf))

    @mock.patch('osrm.core.urlopen')
    def test_trips(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","trips":[{"legs":[{"steps":[],"summary":"","duration":507739.7,"distance":10016386.4},{"steps":[],"summary":"","duration":10035.7,"distance":281576.6},{"steps":[],"summary":"","duration":517625,"distance":10320096.1}],"geometry":"qbs~@ebywHjyiDnl_Ltt_Dwlj@nf_AhqhDuymBbdeM_eiFhr}Ff{tBbplCikVln|Bfw`BpgrEcre@jrjEz~dDne|KwnjAv`aBac~Ci{N}}mFbtnJqf{@fzOkqgDmitD{wpAtgaAahRv{kDeirGbmkFaxMfyeHqdmK|z}Joz~GjptAstxDlsjDgieIm~Oaf`ArvaAgwpHiecGq}xB`pe@kliFiupG}|nHtscAusyBekk@otaCqplFm}dPhe{HkyjAabr@ogE_tfBdxzBatrIiwwCwtmDagnRoacBkufCkjdBirvKtvEck~@ljnBcvqAg`Di~KxsmF_j|Brym@xIvlhAywrF|rtCixhAx~yBaj|GfpsC~{IzsyJohgAxobJig~EfppR{vXhmvF{vlDnmtGs~XdpeCazkFxj_DsbxCrnwFajnFzwdAandHn|`MgogIvsyBcb{FyiyAsxdChsyOklxCpgyCyvuCx|aGe_r@d}qK`zq@iiqKjcfBwluCtlr@wtrDnyiGi@ckKq|jCta~DuzgGxddB`q@vgjE}ljFtc~Culr@~nwFkm}K`dnFgrdArhxCgtwFlwkFyg~CfaYesfCdylDqrtG|}X_nvFp~}EejpRdhgAkkbJwwIk~yJlf|G{isCjwhAc~yB~jtFg}uCs|@ubgA`o|Bc}m@`zKqpmFhuqAteDbk}@sxmBhrwKamFxnfCbhdB`inR`acBn{wCvumDywzBporIp}D|{fBbbkA`gr@b{dPk_{HrwaCrblFtsyBvjk@||nHuscAjliFhupGp}xBape@fwpHhecG`f`AsvaAfieIl~OrtxDmsjDnz~GkptApdmK}z}J`xMgyeHdirGcmkF`hRw{kDzwpAugaAjqgDlitDpf{@gzOj}mFssnJre~Cd|NvljAcbaB{~dDoe|Kbre@krjEgw`BqgrEhkVmn|Bg{tBcplC~diFir}FtymBcdeMof_AiqhDut_Dvlj@","duration":1035400.4,"distance":20618059}],"waypoints":[{"waypoint_index":1,"location":[13.388799,52.517033],"name":"Friedrichstra\xc3\x9fe","hint":"eCEKgHudrorU0AAAEAAAABgAAAAGAAAAAAAAAF-UMQdJgZUDE_sAAP9LzACpWCEDPEzMAK1YIQMBAAEB9TrYrw==","trips_index":0},{"waypoint_index":2,"location":[10.000001,53.549986],"name":"Steinstra\xc3\x9fe","hint":"bb6sgjcQRYPD5wAACQAAABsAAAAAAAAAAAAAAL_wBApIJj8KE_sAAIGWmACiGzEDgJaYALAbMQMAAAEB9TrYrw==","trips_index":0},{"waypoint_index":0,"location":[51.251707,10.424888],"name":"","hint":"YgjCifUIwokAAAAA-wAAAAAAAADIuwAAAAAAADqQIgf4IoMBE_sAAPsJDgM4Ep8ArCsfA3OZlACJAAEB9TrYrw==","trips_index":0}]}'''
            )
        coords = [(13.388860,52.517037), (10.00,53.55), (52.374444,9.738611)]
        result = osrm.trip(coords, output = "only_index")
        self.assertIsInstance(result, list)
        self.assertIn("waypoint", result[0])
        self.assertIn("trip", result[0])

        result2 = osrm.trip(coords, geometry="WKT")
        self.assertIsInstance(result2, dict)
        self.assertIn("LINESTRING", result2['trips'][0]["geometry"])

    @mock.patch('osrm.core.urlopen')
    def test_matches(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            u'''{"code":"Ok","matchings":[{"confidence":0,"distance":8,"duration":1.1,"geometry":"g|j_Goro_CEO","legs":[{"steps":[],"summary":"","duration":1.1,"distance":8}]}],"tracepoints":[{"waypoint_index":0,"location":[21.05656,42.004042],"name":"","hint":"_BmZBOtFnIQAAAAABQAAABUAAAAAAAAAbQoAAIGx7AN-sewDbrcAADBMQQFK7oACWExBASDugAIAAAEBfDhq3w==","matchings_index":0},{"waypoint_index":1,"location":[21.056638,42.004072],"name":"","hint":"-xmZhP8ZmQQAAAAAAAAAABsAAAAAAAAAXwYAAAOkLAMBpCwDbrcAAH5MQQFo7oACnkxBAYTugAIAAAEBfDhq3w==","matchings_index":0}]}'''
            )
        coords = [[21.0566, 42.0040], [21.05667, 42.0041]]
        result = osrm.match(coords)
        self.assertIn("matchings", result)

    @unittest.expectedFailure
    def test_sending_polyline(self):
        osrm.RequestConfig.host = "router.project-osrm.org"
        result1 = osrm.simple_route((41.5332, 21.9598), (41.9725, 21.3114),
                           output="routes",
                           geometry="wkt",
                           send_as_polyline=False)
        result2 = osrm.simple_route((41.5332, 21.9598), (41.9725, 21.3114),
                           output="routes",
                           geometry="wkt",
                           send_as_polyline=True)
        self.assertEqual(result1, result2)

if __name__ == "__main__":
    unittest.main()
