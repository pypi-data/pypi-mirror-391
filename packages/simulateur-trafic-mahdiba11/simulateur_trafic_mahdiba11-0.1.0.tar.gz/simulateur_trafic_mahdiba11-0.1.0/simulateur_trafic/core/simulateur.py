
"""
class Simulateur

used to initialise configurations for vehicals , routes and intersections  add them to a reseau and launch the simulation

exemple usage
    sim = Simulateur("data\config.json")
    sim.lancer_simulation()

"""

import json
import sys
import os

from ..models.vehicule import Vehicule
from ..models.route import Route
from ..models.reseau import ReseauRoutier

import random

class Simulateur:
    def __init__(self,fichier_config):
        """
        reads the config file and creates the network
        """
        try:
            with (open(fichier_config)) as f:
                data = json.load(f)
        except FileNotFoundError:
            print("fichier de configuration introuvable")
            sys.exit()
        
        self.routes = [Route(data['Routes'][i]['nom'], data['Routes'][i]['longeur'], data['Routes'][i]['limite_vitesse']) for i in range(len(data['Routes']))]
        self.routes_routing = {self.routes[i].nom: self.routes[i] for i in range(len(self.routes))}
        self.intersections = {}
        for key in data["Intersections"].keys():
            route = self.routes_routing[key]
            self.intersections[route] = []
            for next_route in data["Intersections"][key]:
                self.intersections[route].append(self.routes_routing[next_route])
        
        self.vehicules = [Vehicule(data["Vehicules"][i]["position"] , data["Vehicules"][i]["vitesse"] ,self.routes_routing[data["Vehicules"][i]["route_actual"]] , data["Vehicules"][i]["id"]) for i in range(len(data["Vehicules"]))]
        self.reseau = ReseauRoutier(self.routes, self.intersections)
        for route in self.routes:
            route.vehicules_presents = [vehicule for vehicule in self.vehicules if vehicule.route_actuelle == route]

    def lancer_simulation(self ,ntour = 60 , delta = 0.5):
        """
        update the network for n tour of delta seconds 
        arg :
            ntour : number of tour
            delta : time passed between each tour
        output:
            None
        """
        if not isinstance(ntour , int) or not isinstance(delta , float) or ntour<0 or delta<0:
            raise ValueError("ntour and delta must be positive integers")
        for tour in range(ntour):
            self.reseau.simulateur_de_trafic(delta)

if __name__ == "__main__":
    import os

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))   
    CONFIG_PATH = os.path.join(BASE_DIR, "data", "config_reseau.json")

    sim = Simulateur(CONFIG_PATH)
    sim.lancer_simulation(ntour=500)
    
