roles_list = ['Medic', 'Quarantine Specialist', 'Scientist', 'Researcher', 'Operations Expert', 'Dispatcher', 'Contingency Planner']

def load_role(name): #I think there has to be a much better way of doing this...
    if name == 'Medic':
        from amoeba.roles.medic import Medic
        return Medic
    elif name == 'Quarantine Specialist':
        from amoeba.roles.quarantine_specialist import QuarantineSpecialist
        return QuarantineSpecialist
    elif name == 'Scientist':
        from amoeba.roles.scientist import Scientist
        return Scientist
    elif name == 'Researcher':
        from amoeba.roles.researcher import Researcher
        return Researcher
    elif name == 'Operations Expert':
        from amoeba.roles.operations_expert import OperationsExpert
        return OperationsExpert
    elif name == 'Dispatcher':
        from amoeba.roles.dispatcher import Dispatcher
        return Dispatcher
    elif name == 'Contingency Planner':
        from amoeba.roles.contingency_planner import ContingencyPlanner
        return ContingencyPlanner
