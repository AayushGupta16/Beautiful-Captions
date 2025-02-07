"""Animation system for captions."""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class Keyframe:
    """Represents a single keyframe in an animation."""
    time: float  # Time in seconds
    scale_x: float  # X scale percentage
    scale_y: float  # Y scale percentage

class BounceAnimation:
    """Bounce animation generator."""
    
    def __init__(self, duration: float, num_keyframes: int = 10):
        """Initialize bounce animation.
        
        Args:
            duration: Total duration of animation in seconds
            num_keyframes: Number of keyframes to generate
        """
        self.duration = duration
        self.num_keyframes = num_keyframes
        
    def generate_keyframes(self) -> List[Keyframe]:
        """Generate keyframes for bounce animation.
        
        Returns:
            List of keyframes for the animation
        """
        keyframes = []
        
        for i in range(self.num_keyframes):
            t = i * self.duration / (self.num_keyframes - 1)
            scale = max(80, 100 - 90 * (t / self.duration))
            
            keyframe = Keyframe(
                time=t,
                scale_x=scale,
                scale_y=scale
            )
            keyframes.append(keyframe)
            
        return keyframes
    
    def to_ass_commands(self) -> str:
        """Convert animation to ASS animation commands.
        
        Returns:
            String of ASS animation commands
        """
        keyframes = self.generate_keyframes()
        commands = ""
        
        for kf in keyframes:
            commands += f"{{\\t({kf.time:.2f},{kf.time:.2f},\\fscx{kf.scale_x:.0f}\\fscy{kf.scale_y:.0f})}}"
            
        return commands
class AnimationFactory:
    """Factory for creating different types of animations."""
    
    SUPPORTED_TYPES = {"bounce"}  # Define supported types
    
    @staticmethod
    def create(
        animation_type: Optional[str] = None,  # Make optional
        duration: float = 0.0,
        num_keyframes: int = 10
    ) -> str:
        """Create animation commands for specified type.
        
        Args:
            animation_type: Type of animation to create (optional)
            duration: Duration of animation in seconds
            num_keyframes: Number of keyframes to generate
            
        Returns:
            String of ASS animation commands
        """
        if animation_type is None:
            return ""  # Return empty string for no animation
            
        if animation_type not in AnimationFactory.SUPPORTED_TYPES:
            logger.warning(f"Unsupported animation type '{animation_type}', defaulting to no animation")
            return ""
            
        if animation_type == "bounce":
            animation = BounceAnimation(duration, num_keyframes)
            return animation.to_ass_commands()
            
def create_animation_for_subtitle(
    text: str,
    duration: float,
    animation_type: str = "bounce",
    num_keyframes: int = 10
) -> str:
    """Create animated subtitle text.
    
    Args:
        text: Subtitle text to animate
        duration: Duration of subtitle in seconds
        animation_type: Type of animation to apply
        num_keyframes: Number of keyframes for animation
        
    Returns:
        Subtitle text with ASS animation commands
    """
    animation = AnimationFactory.create(
        animation_type,
        duration,
        num_keyframes
    )
    
    return f"{animation}{text}"