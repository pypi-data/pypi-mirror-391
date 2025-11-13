# loopfinder

<img align="center" src="https://nox.apps.okd.maxiv.lu.se/widget?package=loopfinder"/>

A library for loop centring in MX crystallography

## Modules

This library consists of two modules, `vision` and `motion`,
where the latter uses the former.

### Vision

contains all image processing. The main function here is `find_loop()` which
determines at which coordinates the loop tip is.

### Motion

Contains `CentringNavigator` which with each call to `next_step()` can guide the
caller to reliably center the loop in 3 dimensions.

#### Example

```python
from loopfinder.motion import CentringNavigator
from diffractometer import camera_image, rotate, move_to_center  # examples

def autocenter():
    patience = 100
    nav = CentringNavigator()
    while patience > 0:
        step = nav.next_step(camera_image())
        if step.finished():
            return True
        if step.rotate:
            rotate(step.rotate)
        if step.x_to_center and step.y_to_center:
            move_to_center(step.x_to_center, step.y_to_center)
    return False
```

## Environment variables

only one so far, `LOOPFINDER_DIAGNOSTICS_PATH`.
If set, this is where loopfinder will write diagnostic images.
used for debugging.
