"""
DISCO.thermal_imagery

Contains data handling, preprocessing, and augmentation logic
for thermal and RGB modalities.
"""


from .augmentor import ThermalAugmentor, occlusion, contrast,brightness_contrast, elastic

__all__ = ["ThermalAugmentor", "occlusion","contrast","brightness_contrast","elastic"]
