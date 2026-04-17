from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol

@dataclass(frozen=True) #frozen data inmutable
class Evento:
    nombre:str
    data:dict[str, Any] | None = None

class Observador (Protocol ): #Cualquier objeto que tenga estos metodos sirve
    def update (self, subject: Any, evento : Evento) -> None:
        ... # <--- ELLIPSIS EN PYTHON, CUALQUIER CLASE QUE TENGA ESTE METODO CUMPLE PROTOCOL

class Sujeto:
    def __init__ (self) ->None:
        self._observadores: list[Observador] =[]

    def conectar(self, obs:Observador) -> None:
        if obs not in self._observadores:
            self._observadores.append(obs)
    
    def desconectar(self,obs:Observador) ->None:
        if obs in  self._observadores:
            self._observadores.remove(obs)
    
    def notificar (self,evento:Evento) -> None:
        for obs in list (self._observadores):
            obs.update(self, evento)