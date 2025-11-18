"""
 vehicule class represents the attributes and functions aloud for vehiculs objects

 exemple usage :

 v1 = vehicule(position = 0 , vitesse = 10 , route_actuelle = route1 , identifiant = 1)

 v1.change_de_route(route2)
 v1.avancer(0.5)


"""

class Position_Error(Exception):
    """Raised when the position is not valid."""
    pass

class Vehicule:
    def __init__(self, position, vitesse ,route_actuelle , identifiant):
        self.position = position
        self.vitesse = vitesse
        self.route_actuelle = route_actuelle
        self.identifiant = identifiant 
    def changer_de_route(self, route):
        """
        change the rout of a car

        args:
            route (Route): the new route

        output:
            None
        """

        self.route_actuelle = route

    def avancer(self,time):
        """
        advances the car forward based on the minimum between its speed and the route speed and the time passed

        args : 
            time (int): the time passed since the last update

        output:
            None

        """

        self.position += min(self.route_actuelle.limite_vitesse , self.vitesse) * time


