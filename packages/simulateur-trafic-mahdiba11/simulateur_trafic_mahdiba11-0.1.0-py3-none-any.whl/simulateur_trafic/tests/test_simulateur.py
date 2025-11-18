import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import pytest
from simulateur_trafic.core.simulateur import Simulateur



def test_init_simulator():
    from pathlib import Path
    data_dir = Path(__file__).parent.parent
    data_path = data_dir / "data" / "config_reseau.json"

    sim =Simulateur(data_path)
    assert len(sim.routes) !=0 and len(sim.vehicules)!=0


def test_simulateur():
    from pathlib import Path
    data_dir = Path(__file__).parent.parent
    data_path = data_dir / "data" / "config_reseau.json"

    sim =Simulateur(data_path)

    sim.lancer_simulation(10)
    