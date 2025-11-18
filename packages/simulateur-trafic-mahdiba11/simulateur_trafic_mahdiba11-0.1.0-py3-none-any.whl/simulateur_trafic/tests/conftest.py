
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


import pytest
from simulateur_trafic.models.route import Route
from simulateur_trafic.models.vehicule import Vehicule
from simulateur_trafic.models.reseau import ReseauRoutier


@pytest.fixture
def route_simple():
    return Route("A1", longeur=1000, limite_vitesse=30)


@pytest.fixture
def vehicule_exemple(route_simple):
    return Vehicule(identifiant="V1", route_actuelle=route_simple, position=0, vitesse=10)


@pytest.fixture
def reseau_simple(route_simple, vehicule_exemple):
    reseau = ReseauRoutier()
    reseau.ajouter_route(route_simple)
    route_simple.ajouter_vehicule(vehicule_exemple)
    return reseau


if __name__ == "__main__":
    print("worked")




