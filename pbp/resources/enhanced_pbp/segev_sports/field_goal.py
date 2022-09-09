import math

import pbp
import pbp.resources.enhanced_pbp as e
from pbp.resources.enhanced_pbp import Rebound, Foul, FieldGoal
from pbp.resources.enhanced_pbp.segev_sports.enhanced_pbp_item import SegevEnhancedPbpItem


class SegevFieldGoal(FieldGoal, SegevEnhancedPbpItem):
    """
    class for Field Goal Events
    """
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return f'{"made" if self.is_made else "missed"} {self.action_type} {self.sub_type} by {self.player_id}' \
               f'at period {self.period} and {self.time} left to play'

    @property
    def is_blocked(self) -> bool:
        return not self.is_made and hasattr(self, e.BLOCK_ID_STRING)

    @property
    def is_assisted(self) -> bool:
        return self.is_made and hasattr(self, e.ASSIST_ID_STRING)

    @property
    def shot_distance(self) -> float:
        if self.x is not None and self.y is not None:
            x_squared = ((self.x - 5) * 2) ** 2
            y_squared = (self.y - 50) ** 2
            shot_distance = math.sqrt(x_squared + y_squared)
            return round(shot_distance, 1)
        raise Exception('Cannot calculate distance without shot location data')

    @property
    def is_heave(self) -> bool:
        return self.shot_distance > pbp.HEAVE_DISTANCE_CUTOFF and self.seconds_remaining < pbp.HEAVE_TIME_CUTOFF

    @property
    def rebound(self) -> Rebound:
        """
        returns
        """
        if not self.is_made and isinstance(self.next_event, Rebound):
            return self.next_event

    @property
    def rebound_event_id(self) -> str:
        return self.rebound.event_id if self.rebound else None

    @property
    def is_corner_3(self) -> bool:
        """
        returns True is shot was a corner 3, False otherwise
        """
        return self.shot_value == 3 and self.x <= 11

    @property
    def shot_type(self) -> str:
        """
        returns shot type string ('AtRim', 'ShortMidRange', 'LongMidRange', 'Arc3' or 'Corner3')
        """
        if self.shot_value == 3:
            if self.is_corner_3:
                return pbp.CORNER_3_STRING
            else:
                return pbp.ARC_3_STRING
        if self.shot_distance:
            if self.shot_distance < pbp.AT_RIM_CUTOFF:
                return pbp.AT_RIM_STRING
            elif self.shot_distance < pbp.SHORT_MID_RANGE_CUTOFF:
                return pbp.SHORT_MID_RANGE_STRING
            else:
                return pbp.LONG_MID_RANGE_STRING
        return pbp.UNKNOWN_SHOT_DISTANCE_STRING

    @property
    def is_putback(self) -> bool:
        """
        returns True if shot is a 2pt attempt within 2 seconds of an
        offensive rebound attempted by the same player who got the rebound
        """
        if self.is_assisted or self.shot_value == 3:
            return False
        prev_ev = self.previous_event
        while prev_ev and not (isinstance(prev_ev, Rebound) and prev_ev.is_offensive):
            prev_ev = prev_ev.previous_event
        if not prev_ev:
            return False
        in_time = prev_ev.seconds_remaining - self.seconds_remaining <= 2
        return prev_ev.sub_type == e.OFFENSIVE_STRING and prev_ev.player_id == self.player_id and in_time

    @property
    def is_and_one(self) -> bool:
        if self.is_make_that_does_not_end_possession:
            return isinstance(self.next_event, Foul) and self.next_event.is_and_one_foul
        return False

    @property
    def is_make_that_does_not_end_possession(self) -> bool:
        return self.is_made and not self.is_possession_ending_event

    def get_offense_team_id(self) -> str:
        """
        returns team id that took the shot
        """
        return self.team_id