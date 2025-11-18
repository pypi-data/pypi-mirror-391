"""
Pruebas unitarias para el módulo LaplaceSolver2D.
"""
import unittest
import numpy as np
from campo_estatico_mdf.laplace_solver import LaplaceSolver2D


class TestLaplaceSolver2D(unittest.TestCase):
    """Pruebas unitarias para la clase LaplaceSolver2D."""
    
    def test_inicializacion(self):
        """Prueba la correcta inicialización del solver."""
        solver = LaplaceSolver2D(n=10, tolerancia=1e-4)
        self.assertEqual(solver.n, 10)
        self.assertEqual(solver.tolerancia, 1e-4)
        self.assertEqual(solver.v.shape, (10, 10))
        self.assertEqual(solver.iteraciones, 0)
    
    def test_inicializacion_invalida(self):
        """Prueba que se rechacen parámetros inválidos."""
        with self.assertRaises(ValueError):
            LaplaceSolver2D(n=2)  # Muy pequeño
        
        with self.assertRaises(ValueError):
            LaplaceSolver2D(n=10, tolerancia=-0.1)  # Tolerancia negativa
    
    def test_condiciones_contorno(self):
        solver = LaplaceSolver2D(n=5)
        solver.establecer_condiciones_contorno(
        izquierda=0.0,
        derecha=10.0,
        superior=5.0,
        inferior=2.0
    )

        # Verificar bordes sin incluir esquinas
        np.testing.assert_array_equal(solver.v[1:-1, 0], 0.0)   # Izquierda
        np.testing.assert_array_equal(solver.v[1:-1, -1], 10.0) # Derecha
        np.testing.assert_array_equal(solver.v[0, 1:-1], 5.0)   # Superior
        np.testing.assert_array_equal(solver.v[-1, 1:-1], 2.0)  # Inferior
        
    def test_caso_trivial_jacobi(self):
        """
        Prueba el caso trivial: todas las fronteras a 0V.
        El resultado debe ser V=0 en toda la región interior.
        """
        solver = LaplaceSolver2D(n=10, tolerancia=1e-6)
        solver.establecer_condiciones_contorno(0, 0, 0, 0)
        
        iteraciones = solver.resolver_jacobi()
        
        # Verificar que el potencial es cero en toda la región
        np.testing.assert_array_almost_equal(solver.v, 0.0, decimal=5)
        
        # Verificar que convergió rápidamente
        self.assertLess(iteraciones, 10)
    
    def test_caso_trivial_gauss_seidel(self):
        """
        Prueba el caso trivial con Gauss-Seidel.
        """
        solver = LaplaceSolver2D(n=10, tolerancia=1e-6)
        solver.establecer_condiciones_contorno(0, 0, 0, 0)
        
        iteraciones = solver.resolver_gauss_seidel()
        
        # Verificar que el potencial es cero
        np.testing.assert_array_almost_equal(solver.v, 0.0, decimal=5)
        
        # Gauss-Seidel debe converger más rápido que Jacobi
        self.assertLess(iteraciones, 10)
    
    def test_convergencia_caso_simple(self):
        """
        Prueba la convergencia para un caso simple:
        Izquierda y superior a 0V, derecha e inferior a 10V.
        """
        solver = LaplaceSolver2D(n=20, tolerancia=1e-4)
        solver.establecer_condiciones_contorno(
            izquierda=0.0,
            derecha=10.0,
            superior=0.0,
            inferior=10.0
        )
        
        iteraciones = solver.resolver_jacobi()
        
        # Verificar que convergió
        self.assertGreater(iteraciones, 0)
        self.assertLess(iteraciones, 10000)
        
        # Verificar que los valores interiores están entre 0 y 10
        self.assertTrue(np.all(solver.v >= 0))
        self.assertTrue(np.all(solver.v <= 10))
        
        # El centro debe tener un valor intermedio
        centro = solver.v[solver.n // 2, solver.n // 2]
        self.assertGreater(centro, 2.0)
        self.assertLess(centro, 8.0)
    
    def test_gauss_seidel_converge_mas_rapido(self):
        """
        Prueba que Gauss-Seidel converge más rápido que Jacobi.
        """
        # Configuración idéntica para ambos métodos
        n = 30
        tol = 1e-5
        
        # Jacobi
        solver_jacobi = LaplaceSolver2D(n=n, tolerancia=tol)
        solver_jacobi.establecer_condiciones_contorno(0, 10, 0, 10)
        iter_jacobi = solver_jacobi.resolver_jacobi()
        
        # Gauss-Seidel
        solver_gs = LaplaceSolver2D(n=n, tolerancia=tol)
        solver_gs.establecer_condiciones_contorno(0, 10, 0, 10)
        iter_gs = solver_gs.resolver_gauss_seidel()
        
        # Gauss-Seidel debe usar menos iteraciones
        self.assertLess(iter_gs, iter_jacobi)
    
    def test_calculo_campo_potencial_lineal(self):
        """
        Prueba el cálculo del campo eléctrico para un potencial lineal.
        Si V es lineal en x, E_x debe ser aproximadamente constante.
        """
        solver = LaplaceSolver2D(n=21, tolerancia=1e-6)
        
        # Crear un potencial lineal en x: V(x,y) = x
        # Esto simula un campo eléctrico uniforme en dirección x
        for i in range(solver.n):
            for j in range(solver.n):
                solver.v[i, j] = j / (solver.n - 1) * 10.0
        
        # Establecer condiciones de contorno consistentes
        solver.establecer_condiciones_contorno(
            izquierda=0.0,
            derecha=10.0,
            superior=0.0,
            inferior=0.0
        )
        
        # Reconstruir el potencial lineal en el interior
        for i in range(1, solver.n - 1):
            for j in range(solver.n):
                solver.v[i, j] = j / (solver.n - 1) * 10.0
        
        # Calcular campo eléctrico
        e_x, e_y = solver.calcular_campo_e()
        
        # Para un potencial lineal V = kx, E_x = -k (constante)
        # E_y debe ser aproximadamente cero
        
        # Verificar que E_x es aproximadamente constante en el interior
        e_x_interior = e_x[5:-5, 5:-5]
        std_ex = np.std(e_x_interior)
        self.assertLess(std_ex, 0.1)  # Baja variación
        
        # Verificar que E_y es aproximadamente cero
        e_y_interior = e_y[5:-5, 5:-5]
        mean_ey = np.mean(np.abs(e_y_interior))
        self.assertLess(mean_ey, 0.1)
    
    def test_campo_electrico_direccion_correcta(self):
        """
        Prueba que el campo eléctrico apunta en la dirección correcta.
        El campo debe apuntar de mayor a menor potencial.
        """
        solver = LaplaceSolver2D(n=15, tolerancia=1e-5)
        solver.establecer_condiciones_contorno(
            izquierda=10.0,
            derecha=0.0,
            superior=5.0,
            inferior=5.0
        )
        
        solver.resolver_gauss_seidel()
        e_x, e_y = solver.calcular_campo_e()
        
        # En el centro, E_x debe ser positivo (apunta hacia la derecha,
        # de mayor a menor potencial)
        centro_x = solver.n // 2
        centro_y = solver.n // 2
        
        self.assertGreater(e_x[centro_x, centro_y], 0)
    
    def test_obtener_potencial(self):
        """Prueba el método para obtener el potencial."""
        solver = LaplaceSolver2D(n=10)
        solver.establecer_condiciones_contorno(0, 5, 0, 5)
        solver.resolver_jacobi()
        
        v = solver.obtener_potencial()
        
        # Debe ser una copia, no la misma referencia
        self.assertIsNot(v, solver.v)
        np.testing.assert_array_equal(v, solver.v)
    
    def test_obtener_iteraciones(self):
        """Prueba el método para obtener el número de iteraciones."""
        solver = LaplaceSolver2D(n=10, tolerancia=1e-4)
        solver.establecer_condiciones_contorno(0, 10, 0, 10)
        
        self.assertEqual(solver.obtener_iteraciones(), 0)
        
        solver.resolver_jacobi()
        
        self.assertGreater(solver.obtener_iteraciones(), 0)
        self.assertEqual(solver.obtener_iteraciones(), solver.iteraciones)
    
    def test_max_iteraciones_excedido(self):
        """Prueba que se lance una excepción si se excede el máximo de iteraciones."""
        solver = LaplaceSolver2D(n=50, tolerancia=1e-10)  # Tolerancia muy exigente
        solver.establecer_condiciones_contorno(0, 10, 0, 10)
        
        with self.assertRaises(RuntimeError):
            solver.resolver_jacobi(max_iteraciones=10)  # Muy pocas iteraciones


if __name__ == '__main__':
    unittest.main()