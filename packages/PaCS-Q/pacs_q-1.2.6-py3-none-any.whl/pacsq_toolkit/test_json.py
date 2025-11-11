from openmm import unit
from openmm.app import *
from openmm import *
import json, argparse

_ALLOWED_KEYS = {
    "temperature","pressure","timestep","friction","steps","traj_interval"
}

def test_json(**cfg):
    cfg = {k: v for k, v in cfg.items() if k in _ALLOWED_KEYS}

    T = float(cfg.get("temperature", 350))
    return T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    args = ap.parse_args()

    cfg = json.load(open(args.config, "r"))

    tt = test_json(**cfg)
    print(tt)

if __name__ == "__main__":
    main()
