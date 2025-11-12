"""
seraa/core/monitor.py - Subconscious monitoring system
"""

from typing import Callable, Any, Optional, List, Dict
from .ternary import TernaryValue, TernaryState  # Fixed import
import logging


class SubconsciousMonitor:
    """
    Monitors a subprocess and escalates to conscious attention on deviation.
    
    This implements the ternary monitoring concept where:
    - NEUTRAL (0): Process running optimally (subconscious)
    - POSITIVE (1): Enhancement opportunity detected (conscious attention)
    - NEGATIVE (-1): Correction needed (conscious intervention)
    
    Usage:
        >>> def is_optimal(output):
        ...     return output['quality'] > 0.8
        >>> 
        >>> monitor = SubconsciousMonitor(
        ...     name="language_processing",
        ...     optimal_checker=is_optimal
        ... )
        >>> state = monitor.check({'quality': 0.9})
        >>> print(state.value)  # 0 (NEUTRAL - subconscious)
    """
    
    def __init__(
        self, 
        name: str, 
        optimal_checker: Callable[[Any], bool],
        enhancement_checker: Optional[Callable[[Any], bool]] = None,
        correction_checker: Optional[Callable[[Any], bool]] = None
    ) -> None:
        """
        Initialize a subconscious monitor.
        
        Args:
            name: Identifier for this monitor
            optimal_checker: Function that returns True if process is optimal
            enhancement_checker: Optional function to detect enhancement opportunities
            correction_checker: Optional function to detect when correction needed
        """
        self.name = name
        self.optimal_checker = optimal_checker
        self.escalation_callback: Optional[Callable[[str, TernaryValue], None]] = None
        self.enhancement_checker = enhancement_checker
        self.correction_checker = correction_checker
        self.current_state = TernaryValue(TernaryState.NEUTRAL)
        self.history: List[TernaryValue] = []
        logger = self._get_logger()
        self.logger = logger
        logger.info(f"SubconsciousMonitor '{self.name}' initialized.")
    
    def _get_logger(self):
        logger = logging.getLogger(f"SubconsciousMonitor.{self.name}")
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)  # Fixed: should be INFO not info
            logger.info(f"Logger for SubconsciousMonitor '{self.name}' set up.")
        return logger
    
    def check(self, subprocess_output: Any) -> TernaryValue:
        """
        Monitor subprocess and return ternary state.
        
        Args:
            subprocess_output: Output from the monitored subprocess
            
        Returns:
            TernaryValue indicating current state and whether conscious attention needed
        """
        # Check if optimal (subconscious operation)
        if self.optimal_checker(subprocess_output):
            self.current_state = TernaryValue(TernaryState.NEUTRAL)
            
        # Check if enhancement opportunity
        elif self.enhancement_checker and self.enhancement_checker(subprocess_output):
            self.current_state = TernaryValue(TernaryState.POSITIVE)
            self._escalate()
            
        # Check if correction needed
        elif self.correction_checker and self.correction_checker(subprocess_output):
            self.current_state = TernaryValue(TernaryState.NEGATIVE)
            self._escalate()
            
        else:
            # Default to correction needed if not optimal
            self.current_state = TernaryValue(TernaryState.NEGATIVE)
            self._escalate()
        
        self.history.append(self.current_state)
        return self.current_state
    
    def _escalate(self) -> None:
        """Escalate to conscious layer"""
        if self.escalation_callback:
            self.escalation_callback(self.name, self.current_state)
    
    @property
    def is_subconscious(self) -> bool:
        """Is the monitor currently operating subconsciously?"""
        return self.current_state.value == TernaryState.NEUTRAL
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        if not self.history:
            return {"total": 0}
        
        total = len(self.history)
        return {
            "total_checks": total,
            "subconscious_rate": sum(1 for s in self.history if s.value == 0) / total,
            "enhancement_rate": sum(1 for s in self.history if s.value == 1) / total,
            "correction_rate": sum(1 for s in self.history if s.value == -1) / total,
            "current_state": self.current_state.value
        }


class ConsciousLayer:
    """
    Receives escalations from multiple monitors and manages attention.
    
    This represents the "conscious" processing layer that only activates
    when subconscious monitors detect deviations requiring attention.
    
    Usage:
        >>> conscious = ConsciousLayer()
        >>> monitor1 = SubconsciousMonitor("ethics", lambda x: x > 0.8)
        >>> monitor2 = SubconsciousMonitor("safety", lambda x: x > 0.9)
        >>> conscious.add_monitor(monitor1)
        >>> conscious.add_monitor(monitor2)
        >>> 
        >>> # Later, check what needs attention
        >>> attention_items = conscious.get_attention_queue()
    """
    
    def __init__(self, max_attention_items: int = 5):
        """
        Initialize the conscious layer.
        
        Args:
            max_attention_items: Maximum items that can be in conscious attention
        """
        self.monitors: Dict[str, SubconsciousMonitor] = {}
        self.attention_queue: List[tuple[str, TernaryValue]] = []
        self.max_attention_items = max_attention_items
        
    def add_monitor(self, monitor: SubconsciousMonitor) -> None:
        """
        Register a monitor with the conscious layer.
        
        Args:
            monitor: SubconsciousMonitor to register
        """
        monitor.escalation_callback = self._receive_escalation
        self.monitors[monitor.name] = monitor
        
    def _receive_escalation(self, monitor_name: str, state: TernaryValue) -> None:
        """Receive escalation from a monitor"""
        self.attention_queue.append((monitor_name, state))
        
        # Maintain attention limit - prioritize by urgency
        if len(self.attention_queue) > self.max_attention_items:
            # Sort by absolute value (most urgent deviations)
            self.attention_queue.sort(key=lambda x: abs(x[1].value), reverse=True)
            self.attention_queue = self.attention_queue[:self.max_attention_items]
    
    def get_attention_queue(self) -> List[tuple[str, TernaryValue]]:
        """Get current items requiring conscious attention"""
        return self.attention_queue.copy()
    
    def clear_attention(self, monitor_name: str) -> None:
        """
        Mark an item as consciously processed.
        
        Args:
            monitor_name: Name of monitor to clear from attention
        """
        self.attention_queue = [
            (name, state) for name, state in self.attention_queue 
            if name != monitor_name
        ]
    
    def get_conscious_report(self) -> Dict[str, Any]:
        """
        Get what's currently in conscious awareness.
        
        Returns:
            Dictionary with attention statistics and details
        """
        return {
            "attention_items": len(self.attention_queue),
            "items": [
                {"monitor": name, "state": state.value} 
                for name, state in self.attention_queue
            ],
            "subconscious_monitors": [
                name for name, monitor in self.monitors.items()
                if monitor.is_subconscious
            ],
            "total_monitors": len(self.monitors)
        }
    
    def reset(self) -> None:
        """Clear all attention items"""
        self.attention_queue = []
