# encoding: utf-8
# Copyright (C) 2014-2015 John Törnblom

import unittest
import os
import uuid

import xtuml.load


def load(fn):
    def load_wrapper(self, *args, **kwargs):
        self.loader.input(fn.__doc__)
        metamodel = self.loader.build_metamodel()
        fn(self, metamodel)
    
    return load_wrapper


class TestLoader(unittest.TestCase):

    def setUp(self):
        self.loader = xtuml.load.ModelLoader()
        self.loader.build_parser()

    def tearDown(self):
        del self.loader

    def testFileInput(self):
        resources = os.path.dirname(__file__) + os.sep + '..' + os.sep + 'resources'
        schema = resources + os.sep + 'ooaofooa_schema.sql'
        globs = resources + os.sep + 'Globals.xtuml'

        metamodel = xtuml.load_metamodel([globs, schema])
        self.assertTrue(metamodel.select_any('S_DT', lambda inst: inst.Name == 'integer') is not None)
        
    @load
    def testTableNamedCREATE(self, m):
        '''
        CREATE TABLE CREATE (Id UNIQUE_ID);
        INSERT INTO CREATE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('CREATE') is not None)
        
    @load
    def testTableNamedTABLE(self, m):
        '''
        CREATE TABLE TABLE (Id UNIQUE_ID);
        INSERT INTO TABLE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('TABLE') is not None)
        
    @load
    def testTableNamedINSERT(self, m):
        '''
        CREATE TABLE INSERT (Id UNIQUE_ID);
        INSERT INTO INSERT VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('INSERT') is not None)
        
    @load
    def testTableNamedINTO(self, m):
        '''
        CREATE TABLE INTO (Id UNIQUE_ID);
        INSERT INTO INTO VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('INTO') is not None)
        
    @load
    def testTableNamedVALUES(self, m):
        '''
        CREATE TABLE VALUES (Id UNIQUE_ID);
        INSERT INTO VALUES VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('VALUES') is not None)
        
    @load
    def testTableNamedROP(self, m):
        '''
        CREATE TABLE ROP (Id UNIQUE_ID);
        INSERT INTO ROP VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('ROP') is not None)
        
    @load
    def testTableNamedREF_ID(self, m):
        '''
        CREATE TABLE REF_ID (Id UNIQUE_ID);
        INSERT INTO REF_ID VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('REF_ID') is not None)
        
    @load
    def testTableNamedFROM(self, m):
        '''
        CREATE TABLE FROM (Id UNIQUE_ID);
        INSERT INTO FROM VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('FROM') is not None)
        
    @load
    def testTableNamedTO(self, m):
        '''
        CREATE TABLE TO (Id UNIQUE_ID);
        INSERT INTO TO VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('TO') is not None)
        
    @load
    def testTableNamedPHRASE(self, m):
        '''
        CREATE TABLE PHRASE (Id UNIQUE_ID);
        INSERT INTO PHRASE VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        self.assertTrue(m.select_any('PHRASE') is not None)
        
    @load
    def testEmptyAttributeList(self, m):
        '''
        CREATE TABLE X ();
        INSERT INTO X VALUES ();
        '''
        self.assertTrue(m.select_any('X') is not None)

    @load
    def testInsertSTRING(self, m):
        '''
        CREATE TABLE X (Id STRING);
        INSERT INTO X VALUES ('TEST');
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 'TEST')
        
    @load
    def testInsertUNIQUE_ID_Null(self, m):
        '''
        CREATE TABLE X (Id UNIQUE_ID);
        INSERT INTO X VALUES ("00000000-0000-0000-0000-000000000000");
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, uuid.UUID(int=0))
        
    @load
    def testInsertREAL_Positive(self, m):
        '''
        CREATE TABLE X (Id REAL);
        INSERT INTO X VALUES (1.1);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 1.1)
        
    @load
    def testInsertREAL_Negative(self, m):
        '''
        CREATE TABLE X (Id REAL);
        INSERT INTO X VALUES (-5.2);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, -5.2)

    @load
    def testInsertINTEGER_Positive(self, m):
        '''
        CREATE TABLE X (Id INTEGER);
        INSERT INTO X VALUES (5);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, 5)
        
    @load
    def testInsertINTEGER_Negative(self, m):
        '''
        CREATE TABLE X (Id INTEGER);
        INSERT INTO X VALUES (-1000);
        '''
        val = m.select_any('X')
        self.assertTrue(val is not None)
        self.assertEqual(val.Id, -1000) 

class TestPersist(unittest.TestCase):

    def testPersist(self):
        
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID);
        '''
        
        loader = xtuml.load.ModelLoader()
        loader.build_parser()
        loader.input(schema)
        
        m = loader.build_metamodel()
        m.new('X', BOOLEAN=True,
                   INTEGER=1,
                   REAL=-5.5,
                   UNIQUE_ID=uuid.UUID(int=0))
        
        s = xtuml.serialize_metamodel(m)
        
        loader = xtuml.load.ModelLoader()
        loader.build_parser()
        loader.input(schema)
        loader.input(s)
        
        m = loader.build_metamodel()
        x = m.select_any('X')
        self.assertEqual(x.BOOLEAN, True)
        self.assertEqual(x.INTEGER, 1)
        self.assertEqual(x.REAL, -5.5)
        self.assertEqual(x.UNIQUE_ID, uuid.UUID(int=0))
        
    def testPersistDefaultValues(self):
        
        schema = '''
            CREATE TABLE X (BOOLEAN BOOLEAN,
                            INTEGER INTEGER,
                            REAL REAL,
                            STRING STRING,
                            UNIQUE_ID UNIQUE_ID);
        '''
        
        loader = xtuml.load.ModelLoader()
        loader.build_parser()
        loader.input(schema)
        
        id_generator = xtuml.IdGenerator(readfunc=lambda: 0)
        m = loader.build_metamodel(id_generator)
        m.new('X')
        
        s = xtuml.serialize_metamodel(m)
        
        loader = xtuml.load.ModelLoader()
        loader.build_parser()
        loader.input(schema)
        loader.input(s)
        
        m = loader.build_metamodel(id_generator)
        x = m.select_any('X')
        self.assertEqual(x.BOOLEAN, False)
        self.assertEqual(x.INTEGER, 0)
        self.assertEqual(x.REAL, 0.0)
        self.assertEqual(x.UNIQUE_ID, 0)


if __name__ == "__main__":
    unittest.main()
