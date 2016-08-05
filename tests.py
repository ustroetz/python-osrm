# -*- coding: utf-8 -*-
import unittest
from unittest import mock
from pandas import DataFrame
import numpy

import osrm


class MockReadable:
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content.encode()


class TestOsrmWrapper(unittest.TestCase):
    def setUp(self):
        self.MyConfig1 = osrm.RequestConfig()

    def test_helper(self):
        _list = [i for i in osrm._chain([789, 45], [78, 96], [7878, 789, 36])]
        self.assertEqual(_list, [789, 45, 78, 96, 7878, 789, 36])

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
            """{"waypoints":[{"distance":22064.816067,"hint":"YtOXh5LYdIgAAAAAAAAAAH0FAAAAAAAA-1IAAD2o_wUlqP8FbrcAAC6OdgIrck4BEL95AngUTwEAAAEBfDhq3w==","name":"","location":[41.324078,21.918251]}],"code":"Ok"}"""
            )
        result = osrm.nearest((41.5332, 21.9598))
        # nearest only return the parsed JSON response
        self.assertEqual(result["waypoints"][0]["distance"], 22064.816067)

    @mock.patch('osrm.core.urlopen')
    def test_simple_route(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            '''{"code":"Ok","routes":[{"legs":[{"steps":[],"summary":"","duration":14821.6,"distance":256884.8}],"geometry":"a|wdCobf{F}|@h]}pC`dAmpAbh@qTvTob@d_@sJfEcQvBeJtJcGjNiM~Hqe@~Mcn@`P{i@vFgPn@}HtBeGz@{Md@gGxAoGhCwEh@y_@lBmM|@ac@dLsc@nJmh@|Jot@zEeUXoWtEsRpBmRd@o`@`Eab@fGka@nDYB|a@va@gDAyEmCoFqC}K_FkHqCy_@iNsLmEiFuB}EuBgHgDwC_BwCaBwFmD_@UqMcJkJ}H_JmImI_JiJyLwIgMaTm\\\\waBqiCqaAqxAwfDq`FszFeuH_tCyaEuVs[alAgtAoTcV`AcA|FsGl@k@dK{KxE_FzGoHb^k^lFgGxMkQxGwKjpAksBlGoKnNyW~Xyj@fh@gdAzRka@hCsGlJwVxGuVlL{g@|Jae@pS{~@jCqJfCuGnFwLxDuGtDaGvCwDtDyEfEcElzA{sAxKmKtH_IvFcInHuM`EgKjDuLxB_LxAgNx@uPA{U@sGJgGFiAAcDdA}KtBqLbGcS`m@ydBzTmk@hz@uqBnOm]~LeVlM_TfXcc@ncAe`BlKsQ|GuNnSyn@`]_gAfUis@tI}SjLgTzv@ccAv@W`LiNbh@ip@nOcSlK{Plr@}zA|Tmf@lTye@nUqf@jz@u{AfTk`@rGqObH}TdYyeAzRiu@vE_QbHsSfF_M`f@yiAvoAexCrTog@hOy_@rFgR`GwW?aBdp@{xCvlAsvDnJi\\\\|Fo\\\\xDs`@xRqiClBaW~Fio@Fg@bCaRpUmpAbDcR`EoUPuAdAyHtB}P\\\\qEf@_DZqDvCv@`rAl^fPnEbT`Hh@`@BBBBB?DBF?D?FCZDxtAbf@`GnBzt@lUbZjJvWfIvAd@~d@`ObEjA|JlEfAd@h~Ap{@dUrLjTzJb\\\\bIdNnBxTtA|\\\\Zds@mCbZj@j[bEvTtHn`@hMx}@nUjk@lPd^zNrcCleAl`@jOhYrFxpC`WbWnEhNfDfM~HjaAnn@nPdJvRdG|bDnx@nUtMxd@jYnw@ng@pr@j\\\\dRhKzNpIrKnL~Zx_@bW|\\\\fMpI|NjHnP`FhuC~j@~O`F~IhKpEpIr`@x|@vNb\\\\NXjLfU^r@`KxN`Q`MtQdJvvAxg@hC~@FBVH~DnArj@dQ~`@vJr_Bd[vc@tJle@`PfXfNfwBbqAhY|Rn`@|\\\\lZzUt\\\\bTnf@zU`VjRdL~OxMlYpUl`@vR`Wd]dQ~iCzz@hShKbb@`^fc@hUt\\\\pSbyA`cA`KlEvRlE|HiAzHaFjrBclB`PcJbQuFfRyDhS}ApPb@zMbCdR`FfRbJjSjRdLvQpEnLjHbTrKpd@pEhKlI~HvLdGtKpBlnHra@rP`CxMvCbiBjj@nOvJrPfN`K|R~IpSnDdQdA`WdQhjFjClOrEnLzHtJnOjHtl@hNjNb@nOgD~Id@bK|Hjn@`XjIrEdFlBpEnBbD|AvDnB`F|CnCfBbC`BfDnCfBvAxCjCfFzD|EhDfEjCxGrDrF|CfL|FhSnJfDjBvBf@~A^n@Vp@ThBd@x@\\\\`@Pj@Vt@`@X\\\\JNh@b@\\\\VxBhBx@l@d@Zp@f@|@jAxAnBbArAx@xAHRr@zAXp@CTBRLLNHR?BABCb@FhAPrE|@dJbB~FdBjBj@dGhBnA^rA`@pA`@h@JTD\\\\FxBj@fF|Aj@PzAb@rNhEPDxEvAlF~AVHrDdA~FfBt@XL]lq@afBdBaGb@qBtAuGFc@DKBMIY}BeBaXqZoB_FYyE@kHi@kE_Jg_@EkG?aKvAcRbAgFbDkHfCcIrQsg@dBwHvCmZjB}JpAqGNqF]oLc@}C_BkC{BwAwDgAwCqC{@}CaCoVUaYo@yFyCqPoBoDiHeIcBcDyCwM}CkOmBgGoCqG}EkJoX_h@_Qy[yAaHsDgWe@}CoAgDgDqEkb@}b@oB}CkGePgV}f@{CiEkF{E{XiPgHkFcBuCs@qCKyEjF{w@VyE?sIk@iG_CwV{Kmy@g@mEKsGvAktAbBc~Ar@u~@jAwfACwF_@cHg@wGsBqIcEsRsBuGoBiEeCoD}[o[uEiFiCgEwBgFo@{CsAcGoByJwFu[w@eDcB_HiDeMaBaHaCqNyAeJkAmM@kIVuUb@_[b@oSLaWr@_[d@oJrAaFI}X^kMTqLo@yHqCaMmAeG{@qJDcIZqGv@qKfE_p@V_DQ{BCcAiGi[g@gCc@oEMeEOiGiAsg@]{PeAek@","duration":14821.6,"distance":256884.8}],"waypoints":[{"hint":"YtOXh5LYdIgAAAAAAAAAAH0FAAAAAAAA-1IAAD2o_wUlqP8FbrcAAC6OdgIrck4BEL95AngUTwEAAAEBfDhq3w==","name":"","location":[41.324078,21.918251]},{"hint":"apH5jEvnv40AAAAAYAEAAAAAAAC_LQAA42gAAHZ5UQZhQk4IbrcAAFxqgAK9REQBFHOAAqgvRQFOAAEBfDhq3w==","name":"","location":[41.970268,21.251261]}]}'''
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
        '''{"code":"Ok","durations":[[0,1559.9,4192.8,9858.4,7679.7],[1579.3,0,5300.6,8735.2,6507.6],[4214.7,5334,0,5671.5,3972.1],[9496.8,8354.6,5689.7,0,2643.2],[7270.1,6127.9,3971.5,2624.5,0]],"destinations":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}],"sources":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}]}'''
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

    @mock.patch('osrm.core.urlopen')
    def test_table_OD(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            '''{"code":"Ok","durations":[[10785.3,9107,14619.6,5341.2],[9546.8,7934.9,15473,4054.3],[14559.4,12440.7,18315.9,9115.3],[14463.4,10768.4,22202.6,9904],[12236.7,8541.7,19975.9,7677.3]],"destinations":[{"hint":"XAiehPiqpY4_JQUAZQAAAA0BAACzBQAAVwEAALxM2gRcSLAIbrcAABnMXwGE7IAC2NBfASDugAINAAEBfDhq3w==","name":"1061","location":[23.055385,42.003588]},{"hint":"qdjCi1mz-4wAAAAAFgAAAAAAAABzEgAAKQgAABae8wfvnfMHbrcAAHmQVQErD4ECwJNVATgDgQK6AAEBfDhq3w==","name":"","location":[22.384761,42.012459]},{"hint":"lfafieL2n4kAAAAAAAAAADIAAABbAAAAPQYAAEz6EwdiWKIFbrcAADTGPwF-M5gC2Mg_AZgxmAIDAAEBfDhq3w==","name":"","location":[20.956724,43.529086]},{"hint":"8gQxizUOMYsAAAAAAAAAABsAAAAAAAAAQRkAANIcvgd1Hb4HbrcAADQQSQEqrn0CCNZIAdinfQIAAAEBfDhq3w==","name":"","location":[21.565492,41.791018]}],"sources":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]},{"hint":"P7yyg-Xnvo-GOH0ALAAAACYAAAAAAAAA-QAAAMut1QNf1AgDbrcAAIZRRgFrA4EChlFGAWsDgQIAAAEBfDhq3w==","name":"\xd0\x91\xd1\x83\xd0\xbb\xd0\xb5\xd0\xb2\xd0\xb0\xd1\x80 \xd0\x98\xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb4\xd0\xb5\xd0\xbd","location":[21.385606,42.009451]},{"hint":"SzHlia8HEorwPf4AAQAAAFYAAAAAAAAA8wAAAIPVMgcv1TIHbrcAABfJPwF4rXkCGMk_AXmteQIAAAEBfDhq3w==","name":"R2231","location":[20.957463,41.528696]},{"hint":"VktjiIkUGY_-bPEACgAAAA8AAAAXAQAAWwQAAGHfwwb1cVUGbrcAAFqwQgFcqnICW7BCAVyqcgIJAAEBfDhq3w==","name":"R2347","location":[21.147738,41.069148]},{"hint":"dku7jXlLu43E7icBcQAAABYAAAAAAAAAAAAAAK8RqA-tEagPbrcAADXWSAEJAHcCNtZIAQkAdwIAAAEBfDhq3w==","name":"\xd0\xa2\xd1\x80\xd0\xb8\xd0\xb7\xd0\xbb\xd0\xb0","location":[21.550645,41.353225]}]}'''
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
        with self.assertRaises(ValueError):
            osrm.nearest((12.36, 45.36), url_config=Profile)

    @mock.patch('osrm.core.urlopen')
    def test_accessibility(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            '''{"code":"Ok","durations":[[6924.8,6389.6,7313.6,8356.7,9011,5414.9,5216.1,3623.7,6133.3,6779.8,6138.5,2155.3,2098.8,2042.5,3081.7,3536.9,5580.1,6506.5,5472.3,1523.7,1331.1,1476.4,2117.3,3612.6,4721.7,4198.7,5044.5,1034.4,729.7,2015.4,4029.5,3471.5,4244.2,3712.6,1610.5,676,704.3,2808.8,5239.8,5251.1,3625.2,3131.4,2042.5,1637.5,1443.2,4748,7009.3,4871.7,4248.4,4272.6,4075.4,1810.7,1565.3,3815.8,8673.4,5793.7,4861.1,4776.1,2405.7,1688.3,2424.1,3610,5795.6,8128.5]],"destinations":[{"hint":"PBYNiVUWDYkAAAAAAAAAAA4AAADtAAAAHAAAAPZYyAbTWMgGbrcAADbpOwF-RIYCOPU7AahFhgIJAAEBfDhq3w==","name":"","location":[20.703542,42.35379]},{"hint":"YzCwg8X7AIkAAAAAFQAAAAoAAABXAwAAewAAAME4jQcitsIGbrcAAArvOwFOt4QCOPU7AQi_hAIZAAEBfDhq3w==","name":"","location":[20.705034,42.25211]},{"hint":"GtUciSXVHIkAAAAAAAAAAA8AAAAAAAAAEAAAAFA10QZRNdEGbrcAAHbtOwH_TIMCOPU7AWg4gwIAAAEBfDhq3w==","name":"","location":[20.70463,42.159359]},{"hint":"eJACiXnKm4sAAAAAAAAAABIAAAAAAAAAHwAAAIxtwwZ7bcMGbrcAADffOwHzsYECOPU7AcixgQIAAAEBfDhq3w==","name":"","location":[20.700983,42.054131]},{"hint":"Y80ciVXaQY4AAAAAFgAAAAAAAAALAQAAAAAAAHYx0Qb2MNEGbrcAAO8HPAGEVIACOPU7ASgrgAIHAAEBfDhq3w==","name":"","location":[20.711407,41.964676]},{"hint":"EmYfixRmH4sAAAAAMQAAAAAAAABZCAAAAAAAACBqtwcYarcHbrcAAAP6OgHErH4COPU7AYikfgJlAAEBfDhq3w==","name":"","location":[20.642307,41.856196]},{"hint":"PFEHij9RB4oAAAAAEQAAAAoAAAB7NgAAZgAAAF84CQRa3kEHbrcAAO_iOwFmLH0COPU7AegdfQJNAQEBfDhq3w==","name":"","location":[20.701935,41.757798]},{"hint":"6BywhFR-ronqZJ4AEAAAAAAAAAAQCQAABxsAAKnbNAHbxPIDbrcAAG4IPAGil3sCOPU7AUiXewIAAQEBfDhq3w==","name":"R2238","location":[20.711534,41.654178]},{"hint":"Y0roiWVK6IkAAAAAEQAAABAAAAAfAAAAQwAAAPolNAelJjQHbrcAAOh9PQGGP4YC2Hs9AahFhgIBAAEBfDhq3w==","name":"","location":[20.807144,42.352518]},{"hint":"1HfgifN34IkAAAAAAAAAAAkAAAAAAAAAjQAAAPiuMAdvrzAHbrcAAP1dPQH_yYQC2Hs9AQi_hAIAAAEBfDhq3w==","name":"","location":[20.798973,42.256895]},{"hint":"Ay4TijIuE4oAAAAAAAAAABUAAACVCgAArwkAAC-SRwcQkkcHbrcAAPOAPQGYNoMC2Hs9AWg4gwKwAAEBfDhq3w==","name":"","location":[20.807923,42.153624]},{"hint":"_iQCiqJ0B4oAAAAAAAAAABUAAACVCQAAAAAAAO29RQMHmnsBbrcAAPTNPQFetIEC2Hs9AcixgQJQAAEBfDhq3w==","name":"","location":[20.827636,42.05475]},{"hint":"nan6iUlsB4oAAAAAFQAAAAAAAACGBAAAAAAAALZNPAeL7EEHbrcAALNJPgEHB4AC2Hs9ASgrgAJLAAEBfDhq3w==","name":"","location":[20.859315,41.944839]},{"hint":"LGwHijFsB4oAAAAAAAAAACoAAAAAAAAAvQEAAKPsQQei7EEHbrcAAM9ePgHBk34C2Hs9AYikfgIAAAEBfDhq3w==","name":"","location":[20.864719,41.849793]},{"hint":"PlkHikIlJI8AAAAAAAAAABEAAADJBQAAfQAAALl8xQi6fMUIbrcAANJ3PQEBNX0C2Hs9AegdfQI2AAEBfDhq3w==","name":"","location":[20.805586,41.760001]},{"hint":"-yBMjvwgTI4AAAAAAAAAAAQAAAAWAAAAfAAAAOnDsQLow7ECbrcAAGYHPQEA6HsC2Hs9AUiXewIBAAEBfDhq3w==","name":"","location":[20.776806,41.674752]},{"hint":"cqD0iaqg9IkAAAAACgAAAAAAAADOAAAA6gAAABiLOQeQijkHbrcAAFj1PgEqVIYCeAI_AahFhgINAAEBfDhq3w==","name":"","location":[20.903256,42.357802]},{"hint":"uU7oiSTt7IkAAAAALwAAAAAAAACpAQAAAAAAAE4oNAfV1gYGbrcAAHk0PwHHJ4UCeAI_AQi_hAIXAAEBfDhq3w==","name":"","location":[20.919417,42.280903]},{"hint":"YSQ8irX7o48AAAAAFwAAAAAAAACVAgAAAAAAAPkWLgM_J9ABbrcAAMrTPgFGdIMCeAI_AWg4gwIhAAEBfDhq3w==","name":"","location":[20.894666,42.169414]},{"hint":"jx4Cip90B4r6ev8AAAAAAAwAAABuAwAA_AUAAPtsPweMbD8HbrcAAO_wPgGaq4ECeAI_AcixgQJKAAEBfDhq3w==","name":"R29275","location":[20.902127,42.052506]},{"hint":"hJ_6iR2g-okAAAAAAAAAAAkAAACVDQAAdQUAAFRJPAeuSDwHbrcAAE0DPwG4KoACeAI_ASgrgAJsAQEBfDhq3w==","name":"","location":[20.906829,41.953976]},{"hint":"dSDriUlWN4wAAAAAJQAAAAAAAACjBAAATAMAAAvbGQgI2xkIbrcAAC0BPwE1oH4CeAI_AYikfgIiAAEBfDhq3w==","name":"","location":[20.906285,41.852981]},{"hint":"Ky4Wih7JPIwAAAAAAAAAABIAAAD0CQAAVgYAAIfpSAdT6kgHbrcAAJbNPgF7MH0CeAI_AegdfQJRAAEBfDhq3w==","name":"","location":[20.893078,41.758843]},{"hint":"0myBi29LQY4AAAAAHAAAAAAAAADLBwAAAAAAAEzemghS3poIbrcAANAMPwEYXXsCeAI_AUiXewJAAAEBfDhq3w==","name":"","location":[20.909264,41.639192]},{"hint":"8bK0h5VnIYuQYwsBCgAAAAAAAAC3HgAAiAUAAAS0XwS8PrgHbrcAANKTQAHHVoYCGIlAAahFhgKpAQEBfDhq3w==","name":"R-206 (206)","location":[21.009362,42.358471]},{"hint":"1RUpiyMWKYsAAAAACAAAAAAAAABnAAAAAAAAACBAuwc4P7sHbrcAAAO-QAFjn4QCGIlAAQi_hAILAAEBfDhq3w==","name":"","location":[21.020163,42.245987]},{"hint":"vgvyitSxO4sAAAAAPAAAAAAAAABTBAAAAAAAAPYWiwKqDykDbrcAAK4AQAHASYMCGIlAAWg4gwIJAAEBfDhq3w==","name":"","location":[20.971694,42.158528]},{"hint":"cXGGi5qsiYsAAAAAAAAAABIAAACwBQAA6AkAADvdMAOJtd0HbrcAAOuFQAGesoECGIlAAcixgQKHAAEBfDhq3w==","name":"","location":[21.005803,42.054302]},{"hint":"njuyhfF_soUAAAAAAAAAACQAAAB2CAAA9gUAAJ6exARNPckEbrcAAOegQAGrLYACGIlAASgrgAJGAAEBfDhq3w==","name":"","location":[21.012711,41.954731]},{"hint":"HNaYjM7WmIwAAAAAAAAAABIAAAB4AwAAkwEAAGNgeAcrhzQIbrcAACJ2QAFagH4CGIlAAYikfgIMAAEBfDhq3w==","name":"","location":[21.001762,41.844826]},{"hint":"sxW_i3QWJ48AAAAAAAAAADYAAADRNgAAmyYAAA1c8gcOXfIHbrcAAMesQAGyOn0CGIlAAegdfQK8AgEBfDhq3w==","name":"","location":[21.015751,41.761458]},{"hint":"yZXlifMm64kAAAAAHAAAAAAAAAA-FAAAjwUAAPBwNQfpcDUHbrcAAAmTQAFap3sCGIlAAUiXewLZAAEBfDhq3w==","name":"","location":[21.009161,41.658202]},{"hint":"IhvyiubQMY4AAAAANQAAAAAAAABhAAAAlQIAAIaupQePrqUHbrcAADEOQgHnJ4YCuA9CAahFhgICAAEBfDhq3w==","name":"","location":[21.106225,42.346471]},{"hint":"0Iyvj-OMr48AAAAAMgAAAAAAAAAbAQAAkwEAAPAGbwYjDp0DbrcAAI8RQgFCyoQCuA9CAQi_hAIHAAEBfDhq3w==","name":"","location":[21.107087,42.256962]},{"hint":"fy8thK8vLYQAAAAAGwAAAAAAAAD3AgAArwAAAAxPhgNKjYUDbrcAAC_0QQEUFoMCuA9CAWg4gwIKAAEBfDhq3w==","name":"","location":[21.099567,42.1453]},{"hint":"DyEjhKb27owAAAAAHAAAAAAAAACLAgAAfgAAALZRSwjh8_wAbrcAAD4cQgFyr4ECuA9CAcixgQILAAEBfDhq3w==","name":"","location":[21.109822,42.05349]},{"hint":"Ot7sjHHe7IwAAAAAAAAAADQAAADRBQAAKwQAALcKzQUlFQgDbrcAAP_8QQE_PYACuA9CASgrgAIcAAEBfDhq3w==","name":"","location":[21.101823,41.958719]},{"hint":"_ejsjADp7IwAAAAAAAAAADQAAAC9AgAAAQQAAD_PSggF3pEDbrcAAC0EQgH_n34CuA9CAYikfgIUAAEBfDhq3w==","name":"","location":[21.103661,41.852927]},{"hint":"thm_i5gPJo8AAAAAAAAAAA4AAACyBwAAxQAAAJvTSgifXfIHbrcAAHT0QQHsDn0CuA9CAegdfQI_AAEBfDhq3w==","name":"","location":[21.099636,41.750252]},{"hint":"3uTtjO7k7YwAAAAAFwAAAAAAAAC5GAAAcgAAAOIYSwgYF0sIbrcAAM1uQgGUqHsCuA9CAUiXewLQAAEBfDhq3w==","name":"","location":[21.130957,41.658516]},{"hint":"C8DMjsYJ2I4MTZEAPgAAADwAAAB5AgAAHQMAANnnHQM0PpMDbrcAAMacQwHoOoYCWJZDAahFhgIHAAEBfDhq3w==","name":"KFORIT","location":[21.208262,42.351336]},{"hint":"bdKtj3DSrY8AAAAAMgAAAAAAAAAAAwAAAAAAAGoB0gP0VbUHbrcAABiJQwF_vIQCWJZDAQi_hAIOAAEBfDhq3w==","name":"","location":[21.203224,42.253439]},{"hint":"LjS6jzA0uo8AAAAADAAAAAAAAADPAAAAAAAAALIkXQOxJF0DbrcAAHZfQwEjXIMCWJZDAWg4gwIHAAEBfDhq3w==","name":"","location":[21.192566,42.163235]},{"hint":"vtoai8LaGosAAAAAAAAAADYAAAAAAAAA6QAAAAyatQd4mLUHbrcAAMfOQwGWFYICWJZDAcixgQIAAAEBfDhq3w==","name":"","location":[21.221063,42.079638]},{"hint":"XKwvi2usL4sAAAAAAAAAAAkAAABrAAAA8Q4AAGWjvQdfor0HbrcAAJemQwG8KYACWJZDASgrgAIHAAEBfDhq3w==","name":"","location":[21.210775,41.953724]},{"hint":"BFdpiV-ooYkAAAAAAAAAAAoAAADwBAAA0TEAAF7--QYV60cGbrcAAF6JQwH3-H4CWJZDAYikfgI-AAEBfDhq3w==","name":"","location":[21.203294,41.875703]},{"hint":"7CdfiwQKv4sAAAAABgAAAAAAAABrHwAAcQcAAJMxzweYM88HbrcAAHfAQwEEAX0CWJZDAegdfQImAgEBfDhq3w==","name":"","location":[21.217399,41.746692]},{"hint":"lbR7iuS1e4qaJZQABgAAAAAAAAA7AAAACAQAAElDdAdYQ3QHbrcAAP6SQwFgonsCWJZDAUiXewIFAAEBfDhq3w==","name":"R2132","location":[21.205758,41.656928]},{"hint":"3hs_iwBE640AAAAAAQAAAA4AAABCAAAAKgAAAOtkwwf0ZMMHbrcAAKkcRQGuRoYC-BxFAahFhgIEAAEBfDhq3w==","name":"","location":[21.306537,42.35435]},{"hint":"XJYLjxybC4_lDawAGgAAAAAAAAClAAAAAAAAAOJNvAZ41-MCbrcAAHQlRQE-tYQC-BxFAQi_hAIJAAEBfDhq3w==","name":"Kulla","location":[21.308788,42.251582]},{"hint":"qvQ9i730PYvpmQwBDAAAAAQAAABbAgAAAgEAAB7dwgfX3cIHbrcAAHEcRQGeOIMC-BxFAWg4gwIoAAEBfDhq3w==","name":"Isen Suma","location":[21.306481,42.154142]},{"hint":"tHHLhIKuNIsAAAAALQAAAEYAAAAcBAAA7gAAAMpkYwQRG8wGbrcAAA4eRQG_s4EC-BxFAcixgQIqAAEBfDhq3w==","name":"","location":[21.306894,42.054591]},{"hint":"PQcOiUAHDokAAAAADAAAAAAAAADQAQAABQAAAHvmyAZ35sgGbrcAABr9RAFAJIAC-BxFASgrgAIYAAEBfDhq3w==","name":"","location":[21.298458,41.95232]},{"hint":"7PbpifL26YkAAAAAFAAAAAAAAADJEQAA6woAAGmsTgP-lPYDbrcAAHtbRQHclX4C-BxFAYikfgIsAQEBfDhq3w==","name":"","location":[21.322619,41.850332]},{"hint":"baOhiU1ro4kAAAAALwAAAAAAAAA8LgAAAAAAAKv6RwAciBUHbrcAAH9rRAGaJ30C-BxFAegdfQJnAgEBfDhq3w==","name":"","location":[21.261183,41.75657]},{"hint":"wfffiNIMEI4AAAAAAAAAADYAAAAaEwAAnwwAAOZCsgaWm48IbrcAAGfNRAF2cHsC-BxFAUiXewJDAAEBfDhq3w==","name":"","location":[21.286247,41.64415]},{"hint":"gyA_i4QgP4sAAAAAAAAAAAoAAAD8BQAA_AAAAJ5mwwf4ZsMHbrcAAHO1RgHWUoYCmKNGAahFhgIxAAEBfDhq3w==","name":"","location":[21.411187,42.357462]},{"hint":"ArYgi4BZTYsAAAAACwAAAAAAAAATAwAAZwUAAEOhfgB8q84CbrcAAMujRgGHv4QCmKNGAQi_hAI6AAEBfDhq3w==","name":"","location":[21.406667,42.254215]},{"hint":"TNlGiVa0xYkAAAAAFgAAAAAAAAAzAQAAAAAAABOVJAcdlSQHbrcAAKTDRgH744ICmKNGAWg4gwIQAAEBfDhq3w==","name":"","location":[21.41482,42.132475]},{"hint":"fv0_hP___3-fvZAAxQAAAH4BAADuAAAAtAEAAGMelANeHpQDbrcAAKOjRgEhroECmKNGAcixgQIHAAEBfDhq3w==","name":"\xd0\x9c\xd0\xb0\xd1\x98\xd0\xba\xd0\xb0 \xd0\xa2\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb7\xd0\xb0 (A2;A4)","location":[21.406627,42.053153]},{"hint":"v_g9hMP4PYSyxpUAAAAAAAUAAAAQAgAAZgEAANUWlAN4F5QDbrcAAFOqRgEqGYACmKNGASgrgAIrAAEBfDhq3w==","name":"R2134","location":[21.408339,41.949482]},{"hint":"xJX5jM-V-YwAAAAAAAAAAAwAAABsAAAAbgAAADpFTghWRE4IbrcAAJOpRgEKs34CmKNGAYikfgIGAAEBfDhq3w==","name":"","location":[21.408147,41.857802]},{"hint":"zVvfiNBb34gAAAAAAAAAADEAAAAAAAAAGA8AAL32sQaQ97EGbrcAAHjtRgFxsX0CmKNGAegdfQIAAAEBfDhq3w==","name":"","location":[21.425528,41.791857]},{"hint":"U4DfiFSA34gAAAAADgAAAAAAAAABEAAAWwAAAGMLsgZmC7IGbrcAAASRRgFwTnsCmKNGAUiXewJyAAEBfDhq3w==","name":"","location":[21.40186,41.63544]}],"sources":[{"hint":"-hmZhIIUJo8AAAAAAQAAAAoAAAAAAAAANwUAAP6jLAP9oywDbrcAAGdMQQF37oACaExBAXjugAIAAAEBfDhq3w==","name":"","location":[21.056615,42.004087]}]}'''
            )
        gdf, new_pt = osrm.access_isocrone((21.0566163803209, 42.004088575972),
                                           precision=0.1)
        self.assertIsInstance(new_pt, list)

#    @mock.patch('osrm.core.urlopen')
#    def test_trips(self, mock_urlopen):
#        result = osrm.trip(coords, output = "only_index")
#        self.assertIsInstance(result, dict)
#        self.assertIn("waypoint", result)
#        self.assertIn("trip", result)

    @mock.patch('osrm.core.urlopen')
    def test_matches(self, mock_urlopen):
        mock_urlopen.return_value = MockReadable(
            '''{"code":"Ok","matchings":[{"confidence":0,"distance":8,"duration":1.1,"geometry":"g|j_Goro_CEO","legs":[{"steps":[],"summary":"","duration":1.1,"distance":8}]}],"tracepoints":[{"waypoint_index":0,"location":[21.05656,42.004042],"name":"","hint":"_BmZBOtFnIQAAAAABQAAABUAAAAAAAAAbQoAAIGx7AN-sewDbrcAADBMQQFK7oACWExBASDugAIAAAEBfDhq3w==","matchings_index":0},{"waypoint_index":1,"location":[21.056638,42.004072],"name":"","hint":"-xmZhP8ZmQQAAAAAAAAAABsAAAAAAAAAXwYAAAOkLAMBpCwDbrcAAH5MQQFo7oACnkxBAYTugAIAAAEBfDhq3w==","matchings_index":0}]}'''
            )
        coords = [[21.0566, 42.0040], [21.05667, 42.0041]]
        result = osrm.match(coords)
        self.assertIn("matchings", result)


if __name__ == "__main__":
    unittest.main()
