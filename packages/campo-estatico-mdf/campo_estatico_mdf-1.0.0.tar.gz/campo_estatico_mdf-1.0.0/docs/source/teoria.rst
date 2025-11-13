Teoría y fundamentos
====================

Ecuación de Laplace y método de diferencias finitas
---------------------------------------------------

La ecuación de Laplace en 2D se expresa como:

.. math::

   \frac{\partial^2 V}{\partial x^2} + \frac{\partial^2 V}{\partial y^2} = 0

En una malla uniforme con paso :math:`h`, la aproximación por diferencias finitas da:

.. math::

   V_{i,j} = \frac{1}{4} \left(V_{i+1,j} + V_{i-1,j} + V_{i,j+1} + V_{i,j-1}\right)

Este esquema es conocido como *stencil de cinco puntos*.

Métodos iterativos
------------------

**Jacobi:** usa los valores de la iteración anterior:

.. math::
   V_{i,j}^{(k+1)} = \frac{1}{4}(V_{i+1,j}^{(k)} + V_{i-1,j}^{(k)} + V_{i,j+1}^{(k)} + V_{i,j-1}^{(k)})

**Gauss-Seidel:** actualiza en el mismo paso los valores recién calculados:

.. math::
   V_{i,j}^{(k+1)} = \frac{1}{4}(V_{i+1,j}^{(k)} + V_{i-1,j}^{(k+1)} + V_{i,j+1}^{(k)} + V_{i,j-1}^{(k+1)})

Criterio de convergencia
------------------------

Se detiene cuando:

.. math::

   \max |V^{(k+1)} - V^{(k)}| < \varepsilon
