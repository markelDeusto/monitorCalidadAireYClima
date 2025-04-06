import unittest
import sys
import os

if __name__ == '__main__':
    # Asegurarse de que el directorio raíz del proyecto esté en el path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Descubrir y ejecutar todas las pruebas
    test_suite = unittest.defaultTestLoader.discover('.', pattern='test_*.py')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Salir con código de estado basado en el resultado de las pruebas
    sys.exit(not result.wasSuccessful())