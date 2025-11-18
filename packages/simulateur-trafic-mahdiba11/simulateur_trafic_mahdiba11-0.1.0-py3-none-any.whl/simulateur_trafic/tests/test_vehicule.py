from conftest import   vehicule_exemple




def test_avancer(  vehicule_exemple):

    vehicule_exemple.avancer(0.5)
    assert vehicule_exemple.position ==  min(vehicule_exemple.route_actuelle.limite_vitesse , vehicule_exemple.vitesse) * 0.5
    print("test_avancer OK")





if __name__ == "__main__":
    test_avancer()

