import typing as typ
import functools

import cv2
import numpy as np

from loopfinder import utils


def canny_masker(img: np.ndarray, min_sharpness=100):
    return cv2.Canny(img, min_sharpness, min_sharpness + 10)


def mini(
    fn: typ.Callable[(np.ndarray), np.ndarray],
    processing_size=(128, 128),
) -> typ.Callable[(np.ndarray), np.ndarray]:
    """
    Returns a version of fn that works on a resized version of the
    image it is passed, but returns the same size as it is given.
    """

    def minified(img):
        small_img = cv2.resize(img, processing_size)
        small_out = fn(small_img)
        return cv2.resize(small_out, img.shape[1::-1], interpolation=cv2.INTER_NEAREST)

    return minified


def mini_canny_masker(
    img: np.ndarray,
    min_sharpness: int = 100,
    processing_size=(128, 128),
) -> np.ndarray:
    return mini(
        functools.partial(canny_masker, min_sharpness=min_sharpness),
        processing_size=processing_size,
    )(img)


def tunnel_vision(img: np.ndarray, radius_gain=1) -> np.ndarray:
    """
    masks out the corners of img in a circle shape
    with radius = height of img * radius_gain

    operates on monochrome images
    """
    out = np.zeros_like(img)
    height, width = img.shape[:2]
    cv2.circle(
        img=out,
        center=(width // 2, height // 2),
        radius=(height // 2) * radius_gain,
        color=1,
        thickness=-1,
    )

    return img * out


def micromax_masker(img: np.ndarray) -> np.ndarray:
    return mini(lambda mini_img: tunnel_vision(canny_masker(mini_img)))(img)


def find_tip_of_mask(mask: np.ndarray) -> typ.Optional[tuple[int, int]]:
    """
    Finds the coordinates of the furthest point in the mask from the goniometer head.
    """
    for y in range(len(mask) - 1, 0, -1):  # starting at the bottom, go upwards
        row = mask[y]
        if any(row):
            nonzero_indexes = np.nonzero(row)[0]
            leftmost = nonzero_indexes[0]
            rightmost = nonzero_indexes[-1]
            x = (rightmost + leftmost) // 2
            return x, y
    return None


def find_loop(
    img: np.ndarray,
    foreground_segmentor=mini_canny_masker,
) -> typ.Optional[tuple[int, int]]:
    """
    return values are x, y pixel coordinates of the loop tip.
    returns None if there is no foreground visible.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    foreground = foreground_segmentor(gray)
    utils.save_img("mask", foreground)
    tip = find_tip_of_mask(foreground)
    if tip:
        x, y = tip
        utils.save_img("cross", utils.draw_crosshair(img, y, x))
    return tip
