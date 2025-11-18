"""
Route class 

represents the attribute and functunality of a route


exemple of use
route : Route(nom = "route1" , longeur = 100 , limite_vitesse = 50 , vehicules_presents = [vehicule1 , vehicule2])

route.ajouter_vehicule(vehicule3)
route.mettre_a_jour_vehicules(0.5)
"""

from simulateur_trafic.models.vehicule import Vehicule

class Position_Error(Exception):
    """Raised when the position is not valid."""
    pass
class VehiculeDejaPresentError(Exception):
    """Raised when the vehicle is already on the road."""
    pass

class Route:
    def __init__(self, nom  , longeur , limite_vitesse , vehicules_presents=[]):
        self.nom = nom
        self.longeur = longeur
        self.limite_vitesse = limite_vitesse
        self.vehicules_presents = vehicules_presents
    
    def ajouter_vehicule(self, vehicule):
        """
        adds a vehical to the route

        args  :
            vehicule (Vehicule) : the vehical to add
        
        output : 
            None

        """
        if not isinstance(vehicule, Vehicule):
            raise TypeError("vehicule must be an instance of Vehicule")
        if vehicule.identifiant in [vehicule.identifiant for vehicule in self.vehicules_presents]:
            raise VehiculeDejaPresentError("vehicule already present on the route")
        self.vehicules_presents.append(vehicule)

    def metter_a_jour_vehicules(self , time_passed ):
        """
        update the location of all vehicules on the route

        args  :
            time_passed (float) : the time passed since the last update

        output :
            None
        
        """
        try:
            for vehicule in self.vehicules_presents:
                vehicule.avancer(time_passed)
        except Exception as e:
            if isinstance(e , ValueError):
                print("Error : time_passed and vitesse must be a positive number")
            elif isinstance(e , Position_Error):
                print("Error : the vehicule is out of the road")
            else :
                print("Error : ", e)
            

    def __hash__(self) -> str:
        
        return hash(self.nom)




