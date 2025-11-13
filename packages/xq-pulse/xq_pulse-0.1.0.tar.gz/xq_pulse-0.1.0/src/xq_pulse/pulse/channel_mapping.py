from __future__ import annotations

from typing import Dict, List, Set

from constraint import Problem

from xq_pulse.pulse.channel import Channel
from xq_pulse.pulse.program import PulseProgram
from xq_pulse.pulse.pulse import (
    AcquisitionPulse,
    ChannelMappedPulse,
    DelayPulse,
    DrivePulse,
    ForLoopPulse,
    LaserPulse,
    ParallelPulse,
    Pulse,
    SequencePulse,
)
from xq_pulse.pulse.setup import Setup

AbstractLeafId = int  # use id() of the abstract leaf pulse

# Mapping from unrolled concrete pulse id to its abstract source leaf pulse
SourceMap = Dict[int, Pulse]


class ChannelMappingError(RuntimeError):
    pass


def map_channels(program: PulseProgram, setup: Setup) -> PulseProgram:
    """
    Map abstract leaf pulses in the program to the available channels in the setup.
    Returns a new PulseProgram with leaves wrapped by ChannelMappedPulse.
    """
    sweep_parameters = {
        parameter for sweep in program.parameter_sweeps for parameter in (sweep.parameter, sweep.index_parameter)
    }
    free_parameters = program.root.parameters.difference(sweep_parameters)
    assert not free_parameters, (
        "Cannot map channels on a program with free parameters outside parameter sweeps. "
        f"Free parameters: {sorted(p.name for p in free_parameters)}"
    )

    # Unroll to determine abstract leaves and their instances
    unrolled = program.unroll()

    # Helper: determine if channel can generate all instances of an abstract leaf
    def channel_can_generate_all_instances(channel: Channel, unrolled_pulses: List[Pulse]) -> bool:
        for unrolled_pulse in unrolled_pulses:
            base = unrolled_pulse.pulse if isinstance(unrolled_pulse, ChannelMappedPulse) else unrolled_pulse
            if isinstance(base, DelayPulse):
                continue
            if not channel.can_generate(base):
                return False
        return True

    # Collect all abstract leaves that actually require channels
    leaf_ids: List[AbstractLeafId] = []
    for source_id, instances in unrolled.unrolled_by_source.items():
        if not instances:
            continue
        first = instances[0]
        base = first.pulse if isinstance(first, ChannelMappedPulse) else first
        if isinstance(base, (DrivePulse, LaserPulse, AcquisitionPulse)):
            leaf_ids.append(source_id)

    if not leaf_ids:
        new_root = program.root.apply_channel_mapping({})
        return PulseProgram(
            root=new_root,
            acquisition_targets=program.acquisition_targets,
            parameter_sweeps=program.parameter_sweeps,
        )

    # Build eligibility per abstract leaf across all available channels
    all_channels: List[Channel] = sorted(list(setup.channels), key=lambda c: c.name)
    eligible: Dict[AbstractLeafId, List[Channel]] = {}
    for leaf_id in leaf_ids:
        instances = unrolled.unrolled_by_source[leaf_id]
        candidates = [ch for ch in all_channels if channel_can_generate_all_instances(ch, instances)]
        if not candidates:
            raise ChannelMappingError(f"No eligible channels for leaf {leaf_id}")
        eligible[leaf_id] = candidates

    # Prepare solver variables for all leaves
    problem = Problem()
    leaf_variables: Dict[AbstractLeafId, str] = {}

    for leaf_id in leaf_ids:
        var_name = str(leaf_id)
        leaf_variables[leaf_id] = var_name
        allowed = tuple(eligible[leaf_id])
        problem.addVariable(var_name, allowed)

    # Helper: collect abstract leaf ids under a subtree
    def collect_leaf_ids(pulse: Pulse) -> Set[AbstractLeafId]:
        if isinstance(pulse, ChannelMappedPulse):
            base = pulse.pulse
            if isinstance(base, (DrivePulse, LaserPulse, AcquisitionPulse)):
                return {id(base)} if id(base) in leaf_variables else set()
            return set()
        if isinstance(pulse, (DrivePulse, LaserPulse, AcquisitionPulse)):
            return {id(pulse)} if id(pulse) in leaf_variables else set()
        if isinstance(pulse, DelayPulse):
            return set()
        if isinstance(pulse, SequencePulse):
            acc: Set[AbstractLeafId] = set()
            for sp in pulse.pulses:
                acc |= collect_leaf_ids(sp)
            return acc
        if isinstance(pulse, ParallelPulse):
            acc: Set[AbstractLeafId] = set()
            for sp in pulse.pulses:
                acc |= collect_leaf_ids(sp)
            return acc
        if isinstance(pulse, ForLoopPulse):
            return collect_leaf_ids(pulse.body)
        return set()

    # Traverse the pulse tree and add disjoint-channel constraints for Parallel nodes
    def add_parallel_constraints(pulse: Pulse) -> None:
        if isinstance(pulse, ParallelPulse):
            branch_leaf_sets: List[Set[AbstractLeafId]] = [collect_leaf_ids(sp) for sp in pulse.pulses]
            # For every pair of branches, ensure no shared channel between any leaves
            for i in range(len(branch_leaf_sets)):
                for j in range(i + 1, len(branch_leaf_sets)):
                    for a in branch_leaf_sets[i]:
                        for b in branch_leaf_sets[j]:
                            if a in leaf_variables and b in leaf_variables:
                                problem.addConstraint(lambda x, y: x != y, (leaf_variables[a], leaf_variables[b]))
            # Recurse into children
            for sp in pulse.pulses:
                add_parallel_constraints(sp)
        elif isinstance(pulse, SequencePulse):
            for sp in pulse.pulses:
                add_parallel_constraints(sp)
        elif isinstance(pulse, ForLoopPulse):
            add_parallel_constraints(pulse.body)
        else:
            return

    add_parallel_constraints(program.root)

    # Solve and build mapping
    solution = problem.getSolution()
    if solution is None:
        raise ChannelMappingError("Failed to find a channel assignment")
    mapping: Dict[AbstractLeafId, Channel] = {}
    for leaf_id in leaf_ids:
        channel = solution.get(leaf_variables[leaf_id])
        if channel is None:
            raise ChannelMappingError("Failed to extract channel assignment for leaf")
        mapping[leaf_id] = channel

    new_root = program.root.apply_channel_mapping(mapping)
    return PulseProgram(
        root=new_root,
        acquisition_targets=program.acquisition_targets,
        parameter_sweeps=program.parameter_sweeps,
    )
