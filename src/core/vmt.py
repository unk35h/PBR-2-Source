from srctools.keyvalues import Keyvalues
from .material import Material, MaterialMode, GameTarget


'''
"VertexLitGeneric"
{
	$basetexture "pbr2source_test0_albedo"
	$bumpmap "pbr2source_test0_bump"

	$envmap "env_cubemap"
	$envmaptint "[.05 .05 .05]"
	$envmapcontrast 1.0

	$phong 1
	$phongfresnelranges "[0.2 0.8 1.0]"
	$phongexponenttexture "pbr2source_test0_phongexp"
	$phongboost 1.0
}
'''

def game_envmaptint(game: GameTarget, vlg: bool) -> float:
	if game > GameTarget.V2011: return 1.0
	return .05 if vlg else .05**2.2

def game_lightscale(game: GameTarget) -> float|None:
	if game > GameTarget.V2011: return 1.0
	return None


def make_vmt(mat: Material) -> str:
	pbr    = MaterialMode.is_pbr(mat.mode)
	shader = MaterialMode.get_shader(mat.mode)
	vmt    = []

	def write(*args: str):
		l = len(vmt)
		vmt[l:l+len(args)] = args

	write(		f'{shader}\n{{',
				f'	$basetexture		"{mat.name}_albedo"',
				f'	$bumpmap			"{mat.name}_bump"' )

	if MaterialMode.has_alpha(mat.mode):
		write(	'	$translucent	1')

	if pbr:
		write(
				'',
				f'	$mraotexture		"{mat.name}_mrao"',
				f'	$model				{int(MaterialMode.is_model(mat.mode))}' )
		
		if mat.emit:
			write(
				f'	$emissiontexture	"{mat.name}_emit"')
		if mat.height:
			write(
				'',
				'	$parallax			1',
				'	$parallaxdepth		0.04',
				'	$parallaxcenter		0.5')

	else:
		envmaptint = game_envmaptint(mat.target, MaterialMode.is_vlg(mat.mode))
		lightscale = game_lightscale(mat.target)

		write(
				'',
				f'	$envmap						"env_cubemap"',
				f'	$envmaptint					"[{envmaptint} {envmaptint} {envmaptint}]"',
				'	$envmapcontrast				1.0' )


		if MaterialMode.embed_envmap(mat.mode):
			write(
				'	$basetextureenvmapmask		1')
		else:
			write(
				f'	$envmapmask					"{mat.name}_envmap"')


		if lightscale:
			write(
				f'	$envmaplightscale			{lightscale}' )

		if MaterialMode.has_phong(mat.mode):
			write(
				'',
				'	$phong 1',
				f'	$phongexponenttexture		"{mat.name}_phongexp"',
				'	$phongboost					5.0',
				'	$phongfresnelranges			"[0.1 0.8 1.0]"' )

		if MaterialMode.has_selfillum(mat.mode):
			write(	'',
				'	$selfillum		1')
			
			# Mask is always embedded in basetexture alpha, so we don't need this.
			# write(
			# 	f'	$selfillummask	"{mat.name}_emit"' )

	write('}')
	return '\n'.join(vmt)
