###############################################################################
# This file is part of the lib-maxiv-loopfinder project.
#
# Copyright Lund University
#
# Distributed under the GNU GPLv3 license. See LICENSE file for more info.
###############################################################################
import logging
import math
import typing as typ
import numpy as np
import dataclasses
import json

from loopfinder.vision import find_loop, mini_canny_masker


logger = logging.getLogger("loopfinder")

Point: typ.TypeAlias = tuple[int, int]
Img: typ.TypeAlias = np.ndarray
Segmentor: typ.TypeAlias = typ.Callable[[Img], [Img]]


@dataclasses.dataclass
class Step:
    """
    A step for the goniometer to perform before
    the next call to `CentringSequence.step()`.

    Attributes:
        rotate: Rotate by this many degrees.
            Works either clockwise or anticlockwise
            as long as you are consistent.
        x_to_center: move the sample so this x position is in the center.
        y_to_center: move the sample so this y position is in the center.
    """

    rotate: typ.Optional[float] = None
    x_to_center: typ.Optional[float] = None
    y_to_center: typ.Optional[float] = None
    hopeless: bool = False
    _debug_dict: dict = None

    def finished(self) -> bool:
        """
        An empty step means you are finished.
        """
        return all(
            getattr(self, field) is None
            for field in ["rotate", "x_to_center", "y_to_center"]
        )

    def has_translation(self) -> bool:
        return self.x_to_center is not None or self.y_to_center is not None

    def to_json(self) -> str:
        fields = [self.rotate, self.x_to_center, self.y_to_center]
        fields = [str(f) for f in fields]
        data = dict(
            x=self.x_to_center,
            y=self.y_to_center,
            rot=self.rotate,
        )
        if self._debug_dict:
            data.update(self._debug_dict)
        return json.dumps(data)


class CentringNavigator:
    def __init__(
        self,
        target_coordinates: Point,
        tolerance: int,
        segmentor: Segmentor = mini_canny_masker,
        hope=20,
    ):
        """
        A CenteringNavigator contains all the logic to center the tip of a sample.
        The sample is assumed to be mounted from above.
        Arguments:
            target_coordinates: (x,y) tuple of the point in the image to center on.
            Usually the middle.
            tolerance: How many pixels away from target_coordinates is it allowed to be?
            hope: for how many steps will we continue to try to center if we see no
            sign that a sample is even mounted? this is here to reduce the delay in
            the case that there is no pin.
        """
        self._found_in_2d = False
        self._previous_steps = []

        self.segmentor = segmentor
        self.target_coordinates = target_coordinates
        self.tolerance = tolerance
        self.hope = hope

    def distance_to_target(self, x: int, y: int) -> float:
        tx, ty = self.target_coordinates
        return math.sqrt((x - tx) ** 2 + (y - ty) ** 2)

    def cancels_out(self, a_x, a_y, b_x, b_y, tolerance) -> bool:
        mean_x = np.mean([a_x, b_x])
        mean_y = np.mean([a_y, b_y])
        return self.distance_to_target(mean_x, mean_y) < tolerance

    def make_step(self, *args, **kwargs) -> Step:
        step = Step(*args, **kwargs)
        self._previous_steps.append(step)
        return step

    def back_the_way_i_came(self, x: int, y: int) -> bool:
        """
        True if x, y will move us back to where we were at the start of the previous step.
        """
        if len(self._previous_steps) < 1:
            return False
        last_step = self._previous_steps[-1]
        if last_step.has_translation():
            px = last_step.x_to_center
            py = last_step.y_to_center
            if self.cancels_out(x, y, px, py, self.tolerance):
                return True
        return False

    def next_step(self, img: Img) -> Step:
        """
        Args:
            img: the current image from the diffractometer camera in RGB/BGR
        Returns:
            A Step object which instructs you what motors should be moved and how much
            before calling next_step again with a new image. When step.finished() is
            True, then the centring is finished.
        """
        loop_pos = find_loop(img, foreground_segmentor=self.segmentor)
        debug_dict = dict(found_in_2d=self._found_in_2d)
        if loop_pos:
            self.hope = 1_000_000  # I HAVE SEEN THE LOOP! I KNOW IT IS THERE SOMEWHERE!
            distance = self.distance_to_target(*loop_pos)
            debug_dict["distance"] = distance
            if self.distance_to_target(*loop_pos) < self.tolerance:
                if self._found_in_2d:
                    logger.debug("loop centring finished!")
                    return self.make_step(_debug_dict=debug_dict)
                self._found_in_2d = True
                logger.debug(
                    "the loop is now found in two dimensions, rotating 90 degrees."
                )
                return self.make_step(rotate=90, _debug_dict=debug_dict)
            else:
                logger.debug(
                    "Loop is off-center, translating {} to beam".format(loop_pos)
                )
                self._found_in_2d = False
                x, y = loop_pos
                if self.back_the_way_i_came(x, y):
                    logger.debug(
                        "I seem to be going back where I came from. "
                        + "To avoid getting stuck in a bad loop "
                        + "I will rotate 35 degrees."
                    )
                    return self.make_step(rotate=35)
                return self.make_step(
                    x_to_center=x, y_to_center=y, _debug_dict=debug_dict
                )
        else:  # no foreground is visible, loop might be above or to the side.
            logger.debug(
                "I see nothing. fishing for loop, rot70 and moving half a screen down"
            )
            self._found_in_2d = False
            return self.make_step(
                rotate=70,
                x_to_center=img.shape[1] // 2,
                y_to_center=0,
                hopeless=(len(self._previous_steps) > self.hope),
                _debug_dict=debug_dict,
            )

    def write_blackbox(self, path: str) -> None:
        with open(path, "w") as fh:
            fh.writelines(s.to_json() + "\n" for s in self._previous_steps)


class CentringNavigatorUp(CentringNavigator):
    def next_step(self, img: Img, *args, **kwargs):
        flipped_img = img[-1::-1]
        step = super().next_step(flipped_img, *args, **kwargs)
        height = img.shape[0]
        if step.y_to_center is not None:
            step.y_to_center = height - step.y_to_center
        return step
