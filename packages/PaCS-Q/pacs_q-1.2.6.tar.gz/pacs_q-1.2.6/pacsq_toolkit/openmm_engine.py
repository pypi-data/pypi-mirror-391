from openmm.app import *
from openmm import *
from openmm.unit import *
from sys import stdout
from parmed.openmm.reporters import NetCDFReporter


_ALLOWED_KEYS = {
    "temperature","pressure","timestep","friction","steps","traj_interval"
}

def openmm_run(crd, top, i, j, opt=False, **cfg):
    cfg = {k: v for k, v in cfg.items() if k in _ALLOWED_KEYS}

    temp = float(cfg.get("temperature", 300))
    press = float(cfg.get("pressure", 1.0))
    time_step = float(cfg.get("timestep", 2.0))
    frict = float(cfg.get("friction", 1.0))
    all_step = float(cfg.get("steps", 50000))
    traj_inter = int(cfg.get("traj_interval", 500))

    inpcrd = AmberInpcrdFile(f"../../../{crd}")
    prmtop = AmberPrmtopFile(f"../../../{top}", periodicBoxVectors=inpcrd.boxVectors)

    system = prmtop.createSystem(nonbondedMethod=PME,
                                 nonbondedCutoff=1 * nanometer,
                                 constraints=HBonds)

    barostat = MonteCarloBarostat(press * bar, temp * kelvin, 25)
    system.addForce(barostat)

    integrator = LangevinMiddleIntegrator(temp * kelvin, frict / picosecond, time_step / 1000 * picoseconds)

    simulation = Simulation(prmtop.topology, system, integrator)

    simulation.context.setPositions(inpcrd.positions)
    if inpcrd.boxVectors is not None:
        simulation.context.setPeriodicBoxVectors(*inpcrd.boxVectors)

    simulation.context.setVelocitiesToTemperature(temp * kelvin)

    if opt == True:
        simulation.minimizeEnergy()

    # dcd save
    # simulation.reporters.append(DCDReporter(f'./md{i}_{j}.dcd', 1000))

    simulation.reporters.append(
        NetCDFReporter(f'./md{i}_{j}.nc', reportInterval=traj_inter, crds=True, vels=False, frcs=False)
    )

    #simulation.reporters.append(StateDataReporter(
    #    'md.log', traj_inter, step=True, potentialEnergy=True, temperature=True, density=True
    #))

    simulation.step(50000)



def openmm_run_cyc(crd, top, i, j, location, foldername, ref, opt=False, **cfg):
    cfg = {k: v for k, v in cfg.items() if k in _ALLOWED_KEYS}

    temp = float(cfg.get("temperature", 300))
    press = float(cfg.get("pressure", 1.0))
    time_step = float(cfg.get("timestep", 2.0))
    frict = float(cfg.get("friction", 1.0))
    all_step = float(cfg.get("steps", 50000))
    traj_inter = float(cfg.get("traj_interval", 500))

    inpcrd = AmberInpcrdFile(f'{location}/{foldername}/{i - 1}/{ref}/min.rst')
    prmtop = AmberPrmtopFile(f"../../../{top}", periodicBoxVectors=inpcrd.boxVectors)
    system = prmtop.createSystem(nonbondedMethod=PME, nonbondedCutoff=1 * nanometer,
                                 constraints=HBonds)

    barostat = MonteCarloBarostat(press * bar, temp * kelvin, 25)
    system.addForce(barostat)

    integrator = LangevinMiddleIntegrator(temp * kelvin, frict / picosecond, time_step / 1000 * picoseconds)

    simulation = Simulation(prmtop.topology, system, integrator)

    simulation.context.setPositions(inpcrd.positions)
    if inpcrd.boxVectors is not None:
        simulation.context.setPeriodicBoxVectors(*inpcrd.boxVectors)

    simulation.context.setVelocitiesToTemperature(temp * kelvin)

    if opt == True:
        simulation.minimizeEnergy()

    # dcd save
    # simulation.reporters.append(DCDReporter(f'./md{i}_{j}.dcd', 1000))

    simulation.reporters.append(
        NetCDFReporter(f'./md{i}_{j}.nc', reportInterval=traj_inter, crds=True, vels=False, frcs=False)
    )

    simulation.reporters.append(StateDataReporter(
        'md.log', traj_inter, step=True, potentialEnergy=True, temperature=True, density=True
    ))

    simulation.step(all_step)
