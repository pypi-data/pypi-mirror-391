"""
class ReseauRoutier

represents the network of roads and intersections  , used to simulate trafic and print states

exemple usage : 
    reseau = ReseauRoutier(routes,intersections)
    reseau.simulateur_de_trafic(1)


"""

import json
import random
import time
from simulateur_trafic.models.route import Route

from simulateur_trafic.models.vehicule import Vehicule

class ReseauRoutier:
    def __init__(self, routes =[], intersections={}):
        self.routes = routes
        self.intersections = intersections # {a : [b , c ] , c : [a , e],,,}
    def ajouter_route(self, route , intersections = []):
        if not isinstance(route , Route):
            raise TypeError("route must be an instance of Route")
        self.routes.append(route)
        self.intersections[route] = [route] if intersections == [] else intersections
    def simulateur_de_trafic(self , time_passed):
        """
        simulates trafic by updating route status and and all the vehicules change in route

        arg : 
            time_passed (float or it )  : time passed since the last update

        output:
            None

        """

        for route in self.routes:
            route.metter_a_jour_vehicules(time_passed)
            for vehicule in route.vehicules_presents:
                if vehicule.position >= route.longeur: 
                    
                    next_route = random.choice(self.intersections[route])
                    vehicule.position = vehicule.position - route.longeur                        
                    vehicule.changer_de_route(next_route)
                    next_route.vehicules_presents.append(vehicule)
                    route.vehicules_presents.remove(vehicule)
        self.current_stats()


    def current_stats(self):
        """
        prints the current state of the network
        
        """
        state = ""
        print("-----------------------------------------------------------------------------------------------")
        for route in self.routes:
            print( f"state of route {route.nom} \n")
            
            for vehicule in route.vehicules_presents:
                vehicule_state = f"vehicule {vehicule.identifiant} at position {vehicule.position} with speed {vehicule.vitesse} \n"
                print(vehicule_state)


        