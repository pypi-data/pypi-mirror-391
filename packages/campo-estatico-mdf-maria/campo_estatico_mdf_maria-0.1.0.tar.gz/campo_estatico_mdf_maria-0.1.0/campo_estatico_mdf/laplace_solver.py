"""
Módulo para resolver la ecuación de Laplace en 2D usando el Método de Diferencias Finitas.
"""
import numpy as np
from typing import Tuple


class LaplaceSolver2D:
    """
    Clase para resolver la ecuación de Laplace en 2D usando diferencias finitas.
    
    La ecuación de Laplace en 2D es:
        ∂²V/∂x² + ∂²V/∂y² = 0
    """

    def __init__(self, n: int, tolerancia: float = 1e-4):
        """
        Inicializa el solver con una malla cuadrada de tamaño n x n.
        """
        if n < 3:
            raise ValueError("El tamaño de la malla debe ser al menos 3x3")
        if tolerancia <= 0:
            raise ValueError("La tolerancia debe ser positiva")

        self.n = n
        self.tolerancia = tolerancia
        self.v = np.zeros((n, n), dtype=float)
        self.iteraciones = 0

    def establecer_condiciones_contorno(
        self,
        izquierda: float = 0.0,
        derecha: float = 0.0,
        superior: float = 0.0,
        inferior: float = 0.0,
):
        """
        Establece las condiciones de contorno (voltajes en los bordes).
        Cumple con la convención usada en los tests:
        - El borde superior e inferior dominan en las esquinas.
        """
        n = self.n

        # Primero establecemos los bordes laterales
        self.v[:, 0] = izquierda      # Izquierda
        self.v[:, -1] = derecha       # Derecha

        # Luego los bordes horizontales (dominantes en las esquinas)
        self.v[0, :] = superior       # Superior
        self.v[-1, :] = inferior      # Inferior

  


    def resolver_jacobi(self, max_iteraciones: int = 10000) -> int:
        """
        Resuelve la ecuación de Laplace usando el método iterativo de Jacobi.
        """
        v_old = self.v.copy()

        for iteracion in range(max_iteraciones):
            # Actualizar puntos interiores
            for i in range(1, self.n - 1):
                for j in range(1, self.n - 1):
                    self.v[i, j] = 0.25 * (
                        v_old[i+1, j] + v_old[i-1, j] +
                        v_old[i, j+1] + v_old[i, j-1]
                    )

            diferencia_maxima = np.max(np.abs(self.v - v_old))
            if diferencia_maxima < self.tolerancia:
                self.iteraciones = iteracion + 1
                return self.iteraciones

            v_old = self.v.copy()

        raise RuntimeError(
            f"No se alcanzó convergencia después de {max_iteraciones} iteraciones. "
            f"Diferencia máxima: {diferencia_maxima:.2e}"
        )

    def resolver_gauss_seidel(self, max_iteraciones: int = 10000) -> int:
        """
        Resuelve la ecuación de Laplace usando el método de Gauss-Seidel.
        """
        for iteracion in range(max_iteraciones):
            v_old = self.v.copy()

            for i in range(1, self.n - 1):
                for j in range(1, self.n - 1):
                    self.v[i, j] = 0.25 * (
                        self.v[i+1, j] + self.v[i-1, j] +
                        self.v[i, j+1] + self.v[i, j-1]
                    )

            diferencia_maxima = np.max(np.abs(self.v - v_old))
            if diferencia_maxima < self.tolerancia:
                self.iteraciones = iteracion + 1
                return self.iteraciones

        raise RuntimeError(
            f"No se alcanzó convergencia después de {max_iteraciones} iteraciones. "
            f"Diferencia máxima: {diferencia_maxima:.2e}"
        )

    def calcular_campo_e(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula el campo eléctrico E = -∇V a partir del potencial.
        """
        grad_y, grad_x = np.gradient(self.v)
        e_x = -grad_x
        e_y = -grad_y
        return e_x, e_y

    def obtener_potencial(self) -> np.ndarray:
        """Devuelve una copia del potencial actual."""
        return self.v.copy()

    def obtener_iteraciones(self) -> int:
        """Devuelve el número de iteraciones realizadas."""
        return self.iteraciones
