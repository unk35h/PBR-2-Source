# from PIL.Image import Image
# import PIL.Image
from .material import Material, MaterialMode, Texture, GameTarget
from . import texops
from .io.image import Image

def from_images(src: dict[str, Image], name: str, mode: MaterialMode, target: GameTarget) -> 'Material':
	albedo = src.get('albedo')
	normal = src.get('normal')
	roughness = src.get('roughness')

	assert albedo is not None
	assert normal is not None
	assert roughness is not None

	metallic = src.get('metallic')
	if metallic is None:
		metallic = Image.blank(normal.size, (0,))

	emit = src.get('emit')
	ao = src.get('ao')
	height = src.get('height')

	return Material(
		mode,
		target,
		albedo.size,
		normal.size,
		name,
		albedo=texops.normalize(albedo, mode='RGBA'),
		roughness=texops.normalize(roughness, normal.size, mode='L'),
		metallic=texops.normalize(metallic, normal.size, mode='L'),
		emit=texops.normalize(emit, albedo.size, noAlpha=True) if emit else None,
		ao=texops.normalize(ao, albedo.size, mode='L') if ao else None,
		normal=texops.normalize(normal, mode='RGB'),
		height=texops.normalize(height, normal.size, mode='L') if height else None
	)

def export(src: Material) -> list[Texture]:

	textures = []
	basecolor = texops.make_basecolor(src)
	basecolor = basecolor.resize(src.size)
	basecolor = basecolor.convert('uint8', clip=True)
	textures.append(Texture(basecolor, '_albedo'))

	bumpmap = texops.make_bumpmap(src)
	bumpmap = bumpmap.convert('uint8', clip=True)
	textures.append(Texture(bumpmap, '_bump', compressed=False))

	if (MaterialMode.has_selfillum(src.mode) or MaterialMode.is_pbr(src.mode)) and src.emit:
			emit = texops.make_emit(src)
			illum_mask = emit.convert('uint8')
			textures.append(Texture(illum_mask, '_emit'))

	if MaterialMode.is_pbr(src.mode):
		mrao = texops.make_mrao(src)
		mrao = mrao.convert('uint8')
		textures.append(Texture(mrao, '_mrao'))
		
	else:
		if MaterialMode.has_phong(src.mode):
			phong_exp = texops.make_phong_exponent(src)
			phong_exp = phong_exp.convert('uint8', clip=True)
			textures.append(Texture(phong_exp, '_phongexp'))

		if MaterialMode.has_envmap(src.mode) and not MaterialMode.embed_envmap(src.mode):
			envmap_mask = texops.make_envmask(src)
			envmap_mask = envmap_mask.convert('uint8', clip=True)
			textures.append(Texture(envmap_mask, '_envmap'))

	return textures
