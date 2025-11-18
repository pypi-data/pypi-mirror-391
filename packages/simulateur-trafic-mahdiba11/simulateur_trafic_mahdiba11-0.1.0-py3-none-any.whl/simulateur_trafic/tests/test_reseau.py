

def test_add_routes(reseau_simple , route_simple):
    nb_routes = len(reseau_simple.routes)
    reseau_simple.ajouter_route(route_simple)
    nb_routes_after = len(reseau_simple.routes)
    assert nb_routes_after == nb_routes + 1


def test_update_routes(reseau_simple , route_simple):
    positions_before = {vehicule: vehicule.position 
                   for route in reseau_simple.routes 
                   for vehicule in route.vehicules_presents}
    reseau_simple.simulateur_de_trafic(1)
    positions_after = {vehicule: vehicule.position 
                   for route in reseau_simple.routes 
                   for vehicule in route.vehicules_presents}
    assert positions_before != positions_after

