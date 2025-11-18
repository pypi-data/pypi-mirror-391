# campo_estatico_mdf

Solución de la ecuación de Laplace en 2D usando el Método de Diferencias Finitas (MDF).

## Descripción

Este paquete proporciona una implementación eficiente para resolver la ecuación de Laplace en dos dimensiones:

```
∂²V/∂x² + ∂²V/∂y² = 0
```

Es útil para calcular distribuciones de potencial electroestático en regiones 2D con condiciones de contorno fijas.

## Instalación

```bash
pip install campo_estatico_mdf
```

## Uso Básico

```python
from campo_estatico_mdf import LaplaceSolver2D

# Crear el solver con una malla de 50x50 puntos
solver = LaplaceSolver2D(n=50, tolerancia=1e-4)

# Establecer condiciones de contorno (voltajes en los bordes)
solver.establecer_condiciones_contorno(
    izquierda=0.0,
    derecha=10.0,
    superior=0.0,
    inferior=0.0
)

# Resolver usando el método de Gauss-Seidel
iteraciones = solver.resolver_gauss_seidel()

# Obtener el potencial
potencial = solver.obtener_potencial()

# Calcular el campo eléctrico
e_x, e_y = solver.calcular_campo_e()

print(f"Convergió en {iteraciones} iteraciones")
```

## Características

- **Dos métodos iterativos**: Jacobi y Gauss-Seidel
- **Criterio de convergencia automático**: Se detiene cuando se alcanza la tolerancia
- **Cálculo del campo eléctrico**: Obtiene E = -∇V automáticamente
- **Eficiente**: Usa NumPy para operaciones matriciales optimizadas

## Métodos Disponibles

### LaplaceSolver2D

#### `__init__(n, tolerancia=1e-4)`
Inicializa el solver con una malla de N×N puntos.

#### `establecer_condiciones_contorno(izquierda, derecha, superior, inferior)`
Define los voltajes en los cuatro bordes de la región.

#### `resolver_jacobi(max_iteraciones=10000)`
Resuelve usando el método de Jacobi. Retorna el número de iteraciones.

#### `resolver_gauss_seidel(max_iteraciones=10000)`
Resuelve usando el método de Gauss-Seidel (más rápido). Retorna el número de iteraciones.

#### `calcular_campo_e()`
Calcula el campo eléctrico E = -∇V. Retorna las componentes (E_x, E_y).

#### `obtener_potencial()`
Retorna la matriz de potencial V(x,y).

#### `obtener_iteraciones()`
Retorna el número de iteraciones realizadas.

## Ejemplo Avanzado

```python
import matplotlib.pyplot as plt
from campo_estatico_mdf import LaplaceSolver2D

# Configuración
solver = LaplaceSolver2D(n=100, tolerancia=1e-5)
solver.establecer_condiciones_contorno(
    izquierda=0.0,
    derecha=100.0,
    superior=50.0,
    inferior=50.0
)

# Resolver
iteraciones = solver.resolver_gauss_seidel()
print(f"Convergió en {iteraciones} iteraciones")

# Visualizar potencial
v = solver.obtener_potencial()
plt.figure(figsize=(10, 8))
plt.imshow(v, cmap='viridis', origin='lower')
plt.colorbar(label='Potencial (V)')
plt.title('Distribución de Potencial Eléctrico')
plt.xlabel('x')
plt.ylabel('y')
plt.show()

# Visualizar campo eléctrico
e_x, e_y = solver.calcular_campo_e()
x = np.arange(0, solver.n)
y = np.arange(0, solver.n)
X, Y = np.meshgrid(x, y)

plt.figure(figsize=(10, 8))
plt.quiver(X[::5, ::5], Y[::5, ::5], 
           e_x[::5, ::5], e_y[::5, ::5])
plt.title('Campo Eléctrico')
plt.xlabel('x')
plt.ylabel('y')
plt.show()
```

## Requisitos

- Python >= 3.8
- NumPy >= 1.20.0
- SciPy >= 1.7.0

## Licencia

MIT License

## Autor

Maria Moreno - maamorenor@udistrital.edu.co
Sebastian Sanche - zolarpunk@gmail.com

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request en GitHub.

## Documentación

Para documentación completa, visita: https://almarm-r.github.io/campo_estatico_mdf