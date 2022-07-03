from dataclasses import dataclass
from gl_abstractions.shader import Shader
from gl_abstractions.texture import Texture
from objects.element import Element, ElementSpecification, ShapeSpec

from wavefront.model import Model

@dataclass
class ModelElement(Element):
    ''' A general class for elements that use a model. '''
    model: Model = None
    shader: Shader = None
    texture: Texture = None
    shape_specs: list[ShapeSpec] = None

    def __post_init__(self):
        assert self.model, f'model field is required, got {self.model}'
        elspec = ElementSpecification.from_model(
            model=self.model,
            shader=self.shader,
            texture=self.texture,
        )
        # TODO: stop using shape_specs here, it doesn't make sense
        # it should be self.element_spec = ElementSpecification.from_model(...)
        self.shape_specs = elspec.shape_specs
        return super().__post_init__()
