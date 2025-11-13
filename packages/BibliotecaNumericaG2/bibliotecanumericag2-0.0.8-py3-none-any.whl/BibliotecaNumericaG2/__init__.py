from .interpolacao import (
  linear, 
  linear_partes,
  polinomial_hermite,
  polinomial
)

from .aproximacao import (
  minimos_quadrados, 
  theil_sen, 
  ajuste_polinomial_min_quadrados
)

from .erros import (
  erro_absoluto,
  erro_relativo
)

from .raizes import (
  bisseccao,
  newton_raphson,
  secante
)

from .integracao import (
  integral_componentes,
  integral_retangulo,
  integral_trapezio
)


__all__= [
  "linear",
  "linear_partes", 
  "polinomial",
  "polinomial_hermite",
  "minimos_quadrados", 
  "theil_sen",
  "ajuste_polinomial_min_quadrados",
  "erro_absoluto",
  "erro_relativo",
  "bisseccao",
  "secante",
  "newton_raphson",
  "integral_componentes",
  "integral_retangulo",
  "integral_trapezio"
]