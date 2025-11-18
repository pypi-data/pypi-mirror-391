


def test_add_vehicul(route_simple , vehicule_exemple):
    nb_vehicules = len(route_simple.vehicules_presents)
    route_simple.ajouter_vehicule(vehicule_exemple)
    nb_vehicules_after= len(route_simple.vehicules_presents)
    assert nb_vehicules_after == nb_vehicules +1




def test_vehicule_avance(route_simple , vehicule_exemple):

    route_simple.ajouter_vehicule(vehicule_exemple)
    route_simple.metter_a_jour_vehicules(1)

    assert vehicule_exemple.position !=0




