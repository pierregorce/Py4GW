from dataclasses import dataclass
from collections import deque
from Py4GWCoreLib import Map, Agent
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE

from Py4GWCoreLib.enums_src.GameData_enums import Range
from Sources.oazix.CustomBehaviors.primitives.helpers.targeting.enemies.targeting_enemy import TargetingEnemy
from Sources.oazix.CustomBehaviors.primitives.infrastructure.external_dependency_factory import ExternalDependencyFactory

@dataclass
class EnemyCastingState:
    """Current casting state for a single enemy."""
    agent_id: int
    skill_id: int
    activation_time_ms: float
    cast_started_at_ms: float

    @property
    def remaining_casting_time_ms(self) -> float:
        """Calculate remaining cast time based on current time."""
        now_ms = Map.GetInstanceUptime()
        elapsed_ms = now_ms - self.cast_started_at_ms
        remaining = self.activation_time_ms - elapsed_ms
        return max(0.0, remaining)

    @property
    def cast_progress_percent(self) -> float:
        """Calculate cast progress as percentage (0.0 to 1.0)."""
        if self.activation_time_ms <= 0:
            return 1.0
        elapsed_ms = Map.GetInstanceUptime() - self.cast_started_at_ms
        return min(1.0, max(0.0, elapsed_ms / self.activation_time_ms))


@dataclass(frozen=True, slots=True)
class HistoricalCast:
    """Historical record of a completed/interrupted cast."""
    agent_id: int
    skill_id: int
    activation_time_ms: float
    cast_started_at_ms: float
    cast_ended_at_ms: float
    was_interrupted: bool


class CastingObserver:
    """
    Tracks enemy casting state and history using polling approach.

    Call act() each frame to update casting state from game data.
    Uses Agent.IsCasting() and Agent.GetCastingSkillID() to detect active casts.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CastingObserver, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = ExternalDependencyFactory().external_logger_factory.get_logger(self.__class__.__name__)
            # Current casting state: one skill per enemy
            self._current_casts: dict[int, EnemyCastingState] = {}

            # Historical casts: deque per agent for time-windowed queries
            self._cast_history: dict[int, deque[HistoricalCast]] = {}

            # Maximum cast history window in milliseconds (default: 30 seconds)
            self._history_window_ms: float = 30000.0

            # Maximum casts to track per agent
            self._max_casts_per_agent: int = 5

            # Track interrupted agents (event sets flag, polling completes cast)
            # Event fires first, but snapshot is source of truth for when cast actually ends
            self._interrupted_agents: set[int] = set()

            self._initialized = True

    def act(self):
        """
        Update casting state from current game data.

        Call this each frame to:
        - Detect new casts that started
        - Detect casts that completed
        - Detect casts that were interrupted
        - Clean up stale history
        """
        # Get all enemies in range
        enemies = TargetingEnemy.create().get_enemies(
            within_range=Range.Spirit.value,
            condition_predicate=lambda enemy_data: Agent.IsCasting(enemy_data.agent_id),
            is_alive=True
        )

        current_time_ms = Map.GetInstanceUptime()
        currently_casting_agents = set()

        # Check each enemy for casting state
        for enemy in enemies:
            agent_id = enemy.agent_id

            currently_casting_agents.add(agent_id)
            skill_id = Agent.GetCastingSkillID(agent_id)

            # Check if this is a new cast or continuation
            existing_cast = self._current_casts.get(agent_id)

            if existing_cast is None:
                # New cast detected - start tracking
                self._start_tracking_cast(agent_id, skill_id, current_time_ms)
            elif existing_cast.skill_id != skill_id:
                # Skill changed - previous cast was interrupted, start new one
                self._complete_cast(agent_id, current_time_ms, was_interrupted=False)
                self._start_tracking_cast(agent_id, skill_id, current_time_ms)
            # else: same cast continuing, no action needed

        # Check for completed casts (agents no longer casting)
        # Snapshot is source of truth - event only sets interrupt flag
        agents_to_remove = []
        for agent_id in self._current_casts.keys():
            
            if not Agent.IsValid(agent_id):
                agents_to_remove.append(agent_id)
                continue

            if agent_id not in currently_casting_agents:
                # Check if interrupt event fired for this agent
                was_interrupted = agent_id in self._interrupted_agents

                # Complete the cast (snapshot confirms it ended)
                self._complete_cast(agent_id, current_time_ms, was_interrupted=was_interrupted)
                agents_to_remove.append(agent_id)

                # Clear interrupt flag
                if was_interrupted:
                    self._interrupted_agents.discard(agent_id)

        # Remove completed casts from current tracking
        for agent_id in agents_to_remove:
            del self._current_casts[agent_id]

        # Clean up old history entries
        self._cleanup_old_history(current_time_ms)

    def clear(self):
        """Clear all casting data."""
        self._current_casts.clear()
        self._cast_history.clear()
        self._interrupted_agents.clear()

    # ── Event handlers ─────────────────────────────────────────────────────

    def on_skill_interrupted_event(self, agent_id: int, skill_id: int, timestamp_ms: float):
        """
        Handle skill interrupted event from event bus.

        Only sets the interrupt flag - polling will complete the cast when snapshot confirms it ended.
        This avoids race conditions where event fires but snapshot still shows casting.

        Args:
            agent_id: The agent whose cast was interrupted
            skill_id: The skill that was interrupted
            timestamp_ms: When the interrupt occurred
        """
        self.logger.information(f"Interrupt event: agent={agent_id}, skill={skill_id}, time={timestamp_ms}")

        # Mark agent as interrupted - polling will complete when snapshot confirms cast ended
        self._interrupted_agents.add(agent_id)

    # ── Internal helper methods ────────────────────────────────────────────

    def _start_tracking_cast(self, agent_id: int, skill_id: int, current_time_ms: float):
        """Start tracking a new cast."""
        if skill_id == 0:
            return  # Invalid skill, don't track

        activation_time_ms = self._get_skill_activation_time_ms(skill_id)

        self._current_casts[agent_id] = EnemyCastingState(
            agent_id=agent_id,
            skill_id=skill_id,
            activation_time_ms=activation_time_ms,
            cast_started_at_ms=current_time_ms
        )

    def _complete_cast(self, agent_id: int, current_time_ms: float, was_interrupted: bool):
        """Complete a cast and move it to history."""
        cast_state = self._current_casts.get(agent_id)
        if cast_state is None:
            return

        # Create historical record
        historical = HistoricalCast(
            agent_id=agent_id,
            skill_id=cast_state.skill_id,
            activation_time_ms=cast_state.activation_time_ms,
            cast_started_at_ms=cast_state.cast_started_at_ms,
            cast_ended_at_ms=current_time_ms,
            was_interrupted=was_interrupted
        )

        # Add to history
        if agent_id not in self._cast_history:
            self._cast_history[agent_id] = deque(maxlen=self._max_casts_per_agent)

        self._cast_history[agent_id].append(historical)

    def _cleanup_old_history(self, current_time_ms: float):
        """Remove history entries older than the configured window."""
        cutoff_time_ms = current_time_ms - self._history_window_ms

        for agent_id, history_deque in list(self._cast_history.items()):
            # Filter out old entries
            filtered = [cast for cast in history_deque if cast.cast_ended_at_ms > cutoff_time_ms]

            if len(filtered) == 0:
                # No recent casts, remove agent entirely
                del self._cast_history[agent_id]
            elif len(filtered) < len(history_deque):
                # Some entries removed, rebuild deque
                self._cast_history[agent_id] = deque(filtered, maxlen=self._max_casts_per_agent)

    def _get_skill_activation_time_ms(self, skill_id: int) -> float:
        """
        Get skill activation/cast time in milliseconds from skill database.

        Note: This is the base activation time and doesn't account for:
        - Fast casting attribute
        - Consumable effects (e.g., Essence of Celerity)
        - Dazed condition (doubles cast time)
        """
        # GetActivation() returns seconds, convert to milliseconds
        activation_time_seconds = GLOBAL_CACHE.Skill.Data.GetActivation(skill_id)
        activation_time_ms = activation_time_seconds * 1000.0

        # Instant skills (0ms activation) are valid, just return them
        return activation_time_ms

    # ── Query methods ──────────────────────────────────────────────────────

    def get_all_current_casts(self) -> list[EnemyCastingState]:
        """Get all currently tracked casts."""
        return list(self._current_casts.values())

    def get_all_cast_history(self, window_ms: float | None = None) -> dict[int, list[HistoricalCast]]:
        """Get cast history for all agents, optionally filtered by time window."""
        if window_ms is None:
            history = {agent_id: list(casts) for agent_id, casts in self._cast_history.items()}
            return history

        now_ms = Map.GetInstanceUptime()
        cutoff_time_ms = now_ms - window_ms

        filtered_history = {
            agent_id: [cast for cast in casts if cast.cast_ended_at_ms > cutoff_time_ms]
            for agent_id, casts in self._cast_history.items()
        }

        return filtered_history

        