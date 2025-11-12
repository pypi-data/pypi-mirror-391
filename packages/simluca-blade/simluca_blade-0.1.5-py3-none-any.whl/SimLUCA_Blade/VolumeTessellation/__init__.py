"""
VolumeTessellation
- 2D radial-slice meshing of rotationally symmetric containers (Container).
- Diffusion property calculations over the resulting mesh (DiffusionProperties).

Units:
- Length: nm
- Time: s
"""

from .Container import Container
from .Diffusion import DiffusionProperties, SurfaceArea

