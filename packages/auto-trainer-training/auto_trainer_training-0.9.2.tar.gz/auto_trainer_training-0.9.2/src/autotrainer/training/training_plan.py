import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

from typing_extensions import Self
from datetime import datetime

from transitions import Machine, State
import humps

from autotrainer.behavior import CaptureAnalysisResult
from autotrainer.behavior.behavior_algorithm import BehaviorAlgorithm
from autotrainer.behavior.pellet_device_protocol import PelletDeviceProtocol
from autotrainer.behavior.tunnel_device_protocol import TunnelDeviceProtocol

from .event_slot import EventSlot
from .training_protocols import PredicateContext, TrainingProgressState
from .training_phase import TrainingPhase


class TrainingPlan:
    def __init__(self, plan_id: Optional[str] = None):
        self.plan_id = plan_id or str(uuid.uuid4())
        self.name: str = ""
        self.description: str = ""
        self.phases: List[TrainingPhase] = []
        self._phase_map: Dict[str, TrainingPhase] = {}

        self._system_context: PredicateContext = PredicateContext()

        # Placeholder of Machine use for type hints/linting.
        self.state = None

        self.machine: Optional[Machine] = None

        # This is a dynamic per-animal value that is not part of the Training Plan definition.  It is tracked in a given
        # instance of TrainingPlan for (de)serializing current animal progress.
        self._current_animal_progress: TrainingProgressState = TrainingProgressState.Active

        # Defines whether to automatically advance if phase predicates are met.  This is currently not serialized, but
        # would likely be part of training progress per-animal if so.
        self._is_automatic: bool = True

        self.property_changed = EventSlot()

    @property
    def is_automatic(self) -> bool:
        return self._is_automatic

    @is_automatic.setter
    def is_automatic(self, value: bool) -> None:
        self._is_automatic = self._on_property_changed("is_automatic", value, self._is_automatic)

    @property
    def behavior_algorithm(self) -> Optional[BehaviorAlgorithm]:
        return self._system_context.algorithm

    @behavior_algorithm.setter
    def behavior_algorithm(self, value: Optional[BehaviorAlgorithm]) -> None:
        if self.behavior_algorithm is not None:
            self.behavior_algorithm.session_processing_ending -= self._on_session_ending
            self.behavior_algorithm.pellets_presented_evt -= self._on_pellets_presented
            self.behavior_algorithm.pellets_consumed_evt -= self._on_pellets_consumed
            self.behavior_algorithm.successful_reaches_evt -= self._on_successful_reaches

        self._system_context.algorithm = value

        if self.behavior_algorithm is not None:
            self.behavior_algorithm.session_processing_ending += self._on_session_ending
            self.behavior_algorithm.pellets_presented_evt += self._on_pellets_presented
            self.behavior_algorithm.pellets_consumed_evt += self._on_pellets_consumed
            self.behavior_algorithm.successful_reaches_evt += self._on_successful_reaches

    @property
    def pellet_device(self) -> Optional[PelletDeviceProtocol]:
        return self._system_context.pellet_device

    @pellet_device.setter
    def pellet_device(self, value: Optional[PelletDeviceProtocol]) -> None:
        self._system_context.pellet_device = value

    @property
    def tunnel_device(self) -> Optional[TunnelDeviceProtocol]:
        return self._system_context.tunnel_device

    @tunnel_device.setter
    def tunnel_device(self, value: Optional[TunnelDeviceProtocol]) -> None:
        self._system_context.tunnel_device = value

    @property
    def current_phase(self) -> Optional[TrainingPhase]:
        """Get the current training phase object"""
        if self.machine is None:
            return None
        return self._phase_map.get(self.state)

    @property
    def training_start_timestamp(self) -> Optional[datetime]:
        """Get the timestamp when training began from the first phase"""
        if not self.phases:
            return None
        return self.phases[0].progress.timestamp

    @property
    def total_session_count(self) -> int:
        """Get the total session count from all phases"""
        return sum(phase.progress.session_count for phase in self.phases)

    @property
    def total_pellets_presented(self) -> int:
        """Get the total pellets consumed from all phases"""
        return sum(phase.progress.pellets_presented for phase in self.phases)

    @property
    def total_pellets_consumed(self) -> int:
        """Get the total pellets consumed from all phases"""
        return sum(phase.progress.pellets_consumed for phase in self.phases)

    @property
    def total_successful_reaches(self) -> int:
        """Get the total successful reaches from all phases"""
        return sum(phase.progress.successful_reaches for phase in self.phases)

    @property
    def total_time(self):
        """Get the total time in training from all phases"""
        return sum(phase.progress.time_in_training for phase in self.phases)

    @property
    def progress_state(self) -> TrainingProgressState:
        return self._current_animal_progress

    @progress_state.setter
    def progress_state(self, value: TrainingProgressState) -> None:
        self._current_animal_progress = value

    def fallback(self, phase: TrainingPhase):
        if phase is None:
            return

        current_idx = self.phases.index(phase)
        if current_idx > 0:
            prev_phase = self.phases[current_idx - 1]
            trigger_name = f"fallback_to_{prev_phase.name}"
            if hasattr(self, trigger_name):
                getattr(self, trigger_name)()
            return

    def advance(self, current_phase: Optional[TrainingPhase]):
        if current_phase is None:
            if self.phases:
                self._before_phase_enter(self.phases[0].name)
            return

        current_idx = self.phases.index(current_phase)
        if current_idx < len(self.phases) - 1:
            next_phase = self.phases[current_idx + 1]
            trigger_name = f"advance_to_{next_phase.name}"
            if hasattr(self, trigger_name):
                getattr(self, trigger_name)()

    def _before_phase_enter(self, phase_name: str, is_resume: bool = False) -> None:
        """Call before_enter on the destination phase"""
        phase = self._phase_map.get(phase_name)
        if phase is not None:
            phase.before_enter(self._system_context, is_resume)

    def _after_phase_exit(self, phase_name: str) -> None:
        """Call after_exit on the current phase"""
        phase = self._phase_map.get(phase_name)
        if phase is not None:
            phase.after_exit(self._system_context)

    def _create_transitions(self) -> List[Dict[str, Any]]:
        """Generate forward and backward transitions between phases"""
        if not self.phases:
            return []

        transitions = []

        for idx, phase in enumerate(self.phases):
            if idx < len(self.phases) - 1:
                next_phase = self.phases[idx + 1]
                transitions.append({
                    "trigger": f"advance_to_{next_phase.name}",
                    "source": phase.name,
                    "dest": next_phase.name,
                    "after": lambda phase_name=phase.name: self._after_phase_exit(phase_name),
                    "before": lambda phase_name=phase.name: self._before_phase_enter(phase_name)
                })

            if idx > 0:
                prev_phase = self.phases[idx - 1]
                transitions.append({
                    "trigger": f"fallback_to_{prev_phase.name}",
                    "source": phase.name,
                    "dest": prev_phase.name,
                    "after": lambda phase_name=phase.name: self._after_phase_exit(phase_name),
                    "before": lambda phase_name=phase.name: self._before_phase_enter(phase_name, False)
                })

            transitions.append({
                "trigger": f"resume_{phase.name}",
                "source": "*",
                "dest": phase.name,
                "after": lambda phase_name=phase.name: self._after_phase_exit(phase_name),
                "before": lambda phase_name=phase.name: self._before_phase_enter(phase_name, True)
            })

        return transitions

    def _initialize_state_machine(self) -> None:
        """Initialize the state machine with dynamic states and transitions"""
        if not self.phases:
            return

        states = [State(name=phase.name, on_enter=lambda phase_name=phase.name: self._on_enter_phase(phase_name)) for
                  phase in self.phases]
        # states = [phase.name for phase in self.phases]

        self._phase_map = {phase.name: phase for phase in self.phases}

        transitions = self._create_transitions()

        initial_state = self.phases[0].name if self.phases else None

        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=initial_state,
            auto_transitions=False
        )

        self.advance(None)

    def _on_enter_phase(self, phase_name: str) -> None:
        self._on_property_changed("current_phase", self._phase_map[phase_name], None)

    def _resume_phase(self, index: int):
        phase = self.phases[index]

        self.machine.state = phase.name

        trigger_name = f"resume_{phase.name}"

        if hasattr(self, trigger_name):
            getattr(self, trigger_name)()

    def _on_session_ending(self, _: CaptureAnalysisResult) -> None:
        """Handle session_processing_ending event from BehaviorAlgorithm"""
        current_phase = self.current_phase

        if current_phase is None:
            return

        current_phase.progress.session_count += 1

        # TODO CaptureOnly CaptureAnalysisResult (no intersession analysis) might be a useful flag as part of
        #  system_context to some predicates or session actions to shortcut their behavior.

        current_phase.perform_session_actions(self._system_context)

        if not self.is_automatic:
            return

        if current_phase.should_fallback(self._system_context):
            self.fallback(current_phase)

        if current_phase.should_advance(self._system_context):
            self.advance(current_phase)

    def _on_pellets_presented(self, amount: int):
        current_phase = self.current_phase
        if current_phase is not None:
            current_phase.progress.pellets_presented += amount

    def _on_pellets_consumed(self, amount: int):
        current_phase = self.current_phase
        if current_phase is not None:
            current_phase.progress.pellets_consumed += amount

    def _on_successful_reaches(self, amount: int):
        current_phase = self.current_phase
        if current_phase is not None:
            current_phase.progress.successful_reaches += amount

    def serialize_progress(self) -> Dict:
        """Serialize the TrainingProgress from each phase into a JSON array"""
        progress = [phase.serialize_progress() for phase in self.phases]

        return {"plan_id": self.plan_id,
                "progress_state": self.progress_state,
                "current_phase_index": self.phases.index(self.current_phase) if self.current_phase else None,
                "progress": progress
                }

    def serialize_progress_to_file(self, file_path: Path) -> None:
        """Serialize the TrainingProgress from each phase and write to JSON file"""
        progress_data = self.serialize_progress()
        with open(file_path, "w") as file:
            json.dump(progress_data, file, indent=2)

    def deserialize_progress(self, progress_dict: Dict) -> None:
        """Deserialize TrainingProgress instances from list of dictionaries back into phase progress values"""
        progress_dict = humps.decamelize(progress_dict)
        progress_data = progress_dict["progress"]

        if progress_dict["plan_id"] != self.plan_id:
            raise ValueError(f"Progress plan id ({progress_dict['plan_id']}) does not match this plan ({self.plan_id})")

        self.progress_state = progress_dict["progress_state"]

        if len(progress_data) != len(self.phases):
            raise ValueError(f"Progress length ({len(progress_data)}) does not match phase count ({len(self.phases)})")

        for idx, progress_item in enumerate(progress_data):
            if not isinstance(progress_item, dict):
                raise ValueError(f"Expected dictionary at index {idx}, got {type(progress_item)}")

            self.phases[idx].deserialize_progress(progress_item)

        self._resume_phase(progress_dict["current_phase_index"])

    def deserialize_progress_from_file(self, file_path: Path) -> None:
        """Deserialize TrainingProgress instances from JSON file back into phase progress values"""
        with open(file_path, "r") as file:
            progress_data = json.load(file)

        self.deserialize_progress(progress_data)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the training plan to dictionary"""
        data = {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "phases": [phase.to_dict() for phase in self.phases]
        }
        return humps.camelize(data)

    @classmethod
    def from_json_file(cls, file_path: Path) -> Self:
        """Load training plan from JSON file"""
        with open(file_path, "r") as file:
            data = json.load(file)

        return TrainingPlan.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        """Load training plan from dictionary"""
        data = humps.decamelize(data)
        plan = cls(data["plan_id"])
        plan.name = data["name"]
        plan.description = data["description"]

        plan.phases = [TrainingPhase.from_dict(phase_data) for phase_data in data["phases"]]

        plan._initialize_state_machine()

        return plan

    def info(self) -> str:
        info = ""

        def add_line(line: str) -> None:
            nonlocal info
            info += f"{line}\n"

        def add_prop(line: str) -> None:
            add_line(f"  {line}")

        add_line(f"Plan ID:     {self.plan_id}")
        add_line(f"Name:        {self.name or '(unnamed)'}")
        add_line(f"Description: {self.description or '(no description)'}")

        if self.phases:
            add_line("Phases:")
            for idx, phase in enumerate(self.phases):
                add_prop(f"{idx + 1}: {phase.name or '(unnamed)'} ({phase.phase_id})")
                add_prop(f"   {phase.description or '(no description)'}")

        return info

    def status(self) -> str:
        status = ""

        def add_line(line: str) -> None:
            nonlocal status
            status += f"{line}\n"

        add_line(f"Current State:       {self._current_animal_progress}")

        if self.current_phase:
            add_line(f"Current phase:        {self.current_phase.name}")
            add_line(self.current_phase.status())
        else:
            add_line("Current phase:         None")

        return status

    def progress_status(self) -> str:
        status = ""

        def add_line(line: str) -> None:
            nonlocal status
            status += f"{line}\n"

        def add_prop(line: str) -> None:
            add_line(f"  {line}")

        def add_subprop(line: str) -> None:
            add_prop(f"  {line}")

        add_line(f"Start:    {self.training_start_timestamp or '(not started)'}")
        add_line(f"Duration: {self.total_time}s")
        add_line("Overall Metrics:")
        add_prop(f"Total sessions: {self.total_session_count}")
        add_prop(f"Pellets presented: {self.total_pellets_presented}")
        add_prop(f"Pellets consumed: {self.total_pellets_consumed}")
        add_prop(f"Successful reaches: {self.total_successful_reaches}")

        if self.current_phase:
            add_line("Current Phase Progress:")
            add_line(self.current_phase.progress_status())

        return status

    def _on_property_changed(self, property_name, new_value, old_value):
        if old_value == new_value:
            return old_value

        for listener in self.property_changed:
            listener(property_name, new_value, old_value)

        return new_value
