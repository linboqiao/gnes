import os
import unittest
from shutil import rmtree

from src.nes import PipelineEncoder
from src.nes.base import TrainableType
from src.nes.encoder.bert_binary import BertBinaryEncoder
from src.nes.encoder.lopq import LOPQEncoder
from src.nes.encoder.pq import PQEncoder


class foo(metaclass=TrainableType):
    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass


class foo1(foo):
    def __init__(self, a, b=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


class foo2(foo1):
    def __init__(self, c, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


class dummyPipeline(PipelineEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipeline = [foo1(*args, **kwargs),
                         foo2(*args, **kwargs), ]


class TestYaml(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.dump_path = os.path.join(dirname, 'dump.yml')
        self.db_path = './test_leveldb'

    def tearDown(self):
        if os.path.exists(self.db_path):
            rmtree(self.db_path)
        if os.path.exists(self.db_path1):
            rmtree(self.db_path1)
        if os.path.exists(self.dump_path):
            os.remove(self.dump_path)

    def test_siganature(self):
        a = foo1(2)
        self.assertEqual(a._init_kwargs_dict, {'a': 2, 'b': 1})
        a = foo2(2, 3)
        self.assertEqual(a._init_kwargs_dict, {'c': 2, 'a': 3, 'b': 1})
        a = foo2(2, 3, wee=4)
        self.assertEqual(a._init_kwargs_dict, {'c': 2, 'a': 3, 'b': 1, 'wee': 4})
        a = foo2(b=1, wee=4, a=3, c=2)
        self.assertEqual(a._init_kwargs_dict, {'c': 2, 'a': 3, 'b': 1, 'wee': 4})

    def test_dump(self):
        pe0 = PipelineEncoder(10, a=23, b='32', c=['123', '456'])
        pe0.dump_yaml(self.dump_path)
        self.assertTrue(os.path.exists(self.dump_path))
        pe = PipelineEncoder.load_yaml(self.dump_path)
        self.assertEqual(type(pe), PipelineEncoder)
        self.assertEqual(pe0._init_kwargs_dict, pe._init_kwargs_dict)

    def test_load(self):
        with open(self.dump_path, 'w') as fp:
            fp.write("!PipelineEncoder\n\
                                parameter:\n\
                                  a: 23\n\
                                  b: '32'\n\
                                  c: ['123', '456']")
        pe = PipelineEncoder.load_yaml(self.dump_path)
        self.assertEqual(type(pe), PipelineEncoder)
        self.assertEqual(pe._init_kwargs_dict, {'a': 23, 'b': '32', 'c': ['123', '456']})

    def test_nest_pipeline(self):
        self._test_different_encoder_yamlize(dummyPipeline, a=1, b=2, c=3, wee=4)
        self._test_different_encoder_yamlize(PQEncoder, 10)
        self._test_different_encoder_yamlize(LOPQEncoder, num_bytes=10, cluster_per_byte=11, pca_output_dim=20)
        self._test_different_encoder_yamlize(BertBinaryEncoder, 8, pca_output_dim=32,
                                             cluster_per_byte=8,
                                             port=1,
                                             port_out=2, ignore_all_checks=True)

    def _test_different_encoder_yamlize(self, cls, *args, **kwargs):
        a = cls(*args, **kwargs)
        a.dump_yaml(self.dump_path)
        a.close()
        self.assertTrue(os.path.exists(self.dump_path))
        b = cls.load_yaml(self.dump_path)
        self.assertEqual(type(b), cls)
        self.assertEqual(a._init_kwargs_dict, b._init_kwargs_dict)
        b.close()

    def test_NES_yaml_dump(self):
        self._test_different_encoder_yamlize(DummyNES, num_bytes=8,
                                             pca_output_dim=32,
                                             cluster_per_byte=8,
                                             port=1,
                                             port_out=2,
                                             data_path=self.db_path,
                                             ignore_all_checks=True)


from src.nes import PipelineEncoder, DummyNES
b = DummyNES(num_bytes=8,
             pca_output_dim=32,
             cluster_per_byte=8,
             port=1,
             port_out=2,
             data_path='./test-path',
             ignore_all_checks=True)
