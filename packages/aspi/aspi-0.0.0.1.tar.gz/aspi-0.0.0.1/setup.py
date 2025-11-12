#!/usr/bin/env python
# -*- encoding: utf8 -*-
import io
import os

from setuptools import setup, find_packages
from distutils.core import Extension #from setuptools import Extension #has a slightly different syntax
import numpy
import glob

long_description = """
Source code: https://github.com/aspi/aspi""".strip() 


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")).read()

## below compile seistr
dipc_module = Extension('dipcfun', sources=['aspi/seistr/src/dip_cfuns.c'], 
										include_dirs=[numpy.get_include()])
sofc_module = Extension('sofcfun', sources=['aspi/seistr/src/sof_cfuns.c'], 
										include_dirs=[numpy.get_include()])
sofc3d_module = Extension('sof3dcfun', sources=['aspi/seistr/src/sof3d_cfuns.c'], 
										include_dirs=[numpy.get_include()])
sointc3d_module = Extension('soint3dcfun', sources=['aspi/seistr/src/soint3d_cfuns.c'], 
										include_dirs=[numpy.get_include()])
sointc2d_module = Extension('soint2dcfun', sources=['aspi/seistr/src/soint2d_cfuns.c'], 
										include_dirs=[numpy.get_include()])
bpc_module = Extension('bpcfun', sources=['aspi/seistr/src/bp_cfuns.c'], 
										include_dirs=[numpy.get_include()])
cohc_module = Extension('cohcfun', sources=['aspi/seistr/src/coh_cfuns.c'], 
										include_dirs=[numpy.get_include()])
paintc2d_module = Extension('paint2dcfun', sources=['aspi/seistr/src/paint_cfuns.c'], 
										include_dirs=[numpy.get_include()])

## below compile ekfmm								
eikonalc_module = Extension('eikonalc', sources=['aspi/ekfmm/src/eikonal.c'], 
										include_dirs=[numpy.get_include()])

eikonalvtic_module = Extension('eikonalvtic', sources=['aspi/ekfmm/src/eikonalvti.c'], 
										include_dirs=[numpy.get_include()])				


## below compile wave	
aps_module = Extension('apscfun', sources=['aspi/wave/src/aps.c',
                                                'aspi/wave/src/wave_psp.c',
                                                'aspi/wave/src/wave_ricker.c',
                                                'aspi/wave/src/wave_abc.c',
                                                'aspi/wave/src/wave_fft2.c',
                                                'aspi/wave/src/wave_fft3.c',
                                                'aspi/wave/src/wave_freqfilt.c',
                                                'aspi/wave/src/wave_alloc.c',
                                                'aspi/wave/src/wave_kissfft.c',
                                                'aspi/wave/src/wave_komplex.c',
                                                'aspi/wave/src/wave_conjgrad.c',
                                                'aspi/wave/src/wave_cdivn.c',
                                                'aspi/wave/src/wave_ctriangle.c',
                                                'aspi/wave/src/wave_ctrianglen.c',
                                                'aspi/wave/src/wave_cntriangle.c',
                                                'aspi/wave/src/wave_cntrianglen.c',
                                                'aspi/wave/src/wave_decart.c',
                                                'aspi/wave/src/wave_win.c',
                                                'aspi/wave/src/wave_memcpy.c',
                                                'aspi/wave/src/wave_fft1.c'],
										depends=glob.glob('aspi/wave/src/*.h'),
                                                include_dirs=[numpy.get_include()])

afd_module = Extension('afdcfun', sources=['aspi/wave/src/afd.c',
                                                'aspi/wave/src/wave_fdm.c',
                                                'aspi/wave/src/wave_psp.c',
                                                'aspi/wave/src/wave_ricker.c',
                                                'aspi/wave/src/wave_abc.c',
                                                'aspi/wave/src/wave_fft2.c',
                                                'aspi/wave/src/wave_fft3.c',
                                                'aspi/wave/src/wave_freqfilt.c',
                                                'aspi/wave/src/wave_alloc.c',
                                                'aspi/wave/src/wave_kissfft.c',
                                                'aspi/wave/src/wave_komplex.c',
                                                'aspi/wave/src/wave_conjgrad.c',
                                                'aspi/wave/src/wave_cdivn.c',
                                                'aspi/wave/src/wave_ctriangle.c',
                                                'aspi/wave/src/wave_ctrianglen.c',
                                                'aspi/wave/src/wave_cntriangle.c',
                                                'aspi/wave/src/wave_cntrianglen.c',
                                                'aspi/wave/src/wave_decart.c',
                                                'aspi/wave/src/wave_win.c',
                                                'aspi/wave/src/wave_memcpy.c',
                                                'aspi/wave/src/wave_fft1.c'],
										depends=glob.glob('aspi/wave/src/*.h'),
                                                include_dirs=[numpy.get_include()])

pfwi_module = Extension('pfwicfun', sources=['aspi/wave/src/pfwi.c',
                                                'aspi/wave/src/wave_fwi.c',
                                                'aspi/wave/src/wave_fwiutil.c',
                                                'aspi/wave/src/wave_fwigradient.c',
                                                'aspi/wave/src/wave_fwilbfgs.c',
                                                'aspi/wave/src/wave_fwimodeling.c',
                                                'aspi/wave/src/wave_triutil.c',
                                                'aspi/wave/src/wave_bigsolver.c',
                                                'aspi/wave/src/wave_cgstep.c',
                                                'aspi/wave/src/wave_butter.c',
                                                'aspi/wave/src/wave_chain.c',
                                                'aspi/wave/src/wave_fdm.c',
                                                'aspi/wave/src/wave_psp.c',
                                                'aspi/wave/src/wave_ricker.c',
                                                'aspi/wave/src/wave_abc.c',
                                                'aspi/wave/src/wave_fft2.c',
                                                'aspi/wave/src/wave_fft3.c',
                                                'aspi/wave/src/wave_freqfilt.c',
                                                'aspi/wave/src/wave_alloc.c',
                                                'aspi/wave/src/wave_kissfft.c',
                                                'aspi/wave/src/wave_komplex.c',
                                                'aspi/wave/src/wave_conjgrad.c',
                                                'aspi/wave/src/wave_cdivn.c',
                                                'aspi/wave/src/wave_triangle.c',
                                                'aspi/wave/src/wave_ctriangle.c',
                                                'aspi/wave/src/wave_ctrianglen.c',
                                                'aspi/wave/src/wave_cntriangle.c',
                                                'aspi/wave/src/wave_cntrianglen.c',
                                                'aspi/wave/src/wave_blas.c',
                                                'aspi/wave/src/wave_blasc.c',
                                                'aspi/wave/src/wave_decart.c',
                                                'aspi/wave/src/wave_win.c',
                                                'aspi/wave/src/wave_memcpy.c',
                                                'aspi/wave/src/wave_fft1.c'],
										depends=glob.glob('aspi/wave/src/*.h'),
                                                include_dirs=[numpy.get_include()])

## below compile npre	
nprec3d_module = Extension('npre3dcfun', sources=['aspi/npre/src/npre3d.c',
												'aspi/npre/src/npre_fxynpre.c',
												'aspi/npre/src/npre_alloc.c',
												'aspi/npre/src/npre_kissfft.c',
												'aspi/npre/src/npre_komplex.c',
												'aspi/npre/src/npre_conjgrad.c',
												'aspi/npre/src/npre_cdivn.c',
												'aspi/npre/src/npre_triangle.c',
												'aspi/npre/src/npre_trianglen.c',
												'aspi/npre/src/npre_ntriangle.c',
												'aspi/npre/src/npre_ntrianglen.c',		
												'aspi/npre/src/npre_decart.c',	
												'aspi/npre/src/npre_win.c',	
												'aspi/npre/src/npre_memcpy.c',			
												'aspi/npre/src/npre_fft1.c'], 
										depends=glob.glob('aspi/npre/src/*.h'),
                                                include_dirs=[numpy.get_include()])

ftfa_module = Extension('ftfacfun', sources=['aspi/npre/src/tf.c',
                                                'aspi/npre/src/npre_fxynpre.c',
                                                'aspi/npre/src/npre_alloc.c',
                                                'aspi/npre/src/npre_kissfft.c',
                                                'aspi/npre/src/npre_komplex.c',
                                                'aspi/npre/src/npre_conjgrad.c',
                                                'aspi/npre/src/npre_cdivn.c',
                                                'aspi/npre/src/npre_triangle.c',
                                                'aspi/npre/src/npre_trianglen.c',
                                                'aspi/npre/src/npre_ntriangle.c',
                                                'aspi/npre/src/npre_ntrianglen.c',
                                                'aspi/npre/src/npre_decart.c',
                                                'aspi/npre/src/npre_win.c',
                                                'aspi/npre/src/npre_memcpy.c',
                                                'aspi/npre/src/npre_fft1.c'],
										depends=glob.glob('aspi/npre/src/*.h'),
                                                include_dirs=[numpy.get_include()])

## below compile ntfa
ntfac_module = Extension('ntfacfun', sources=['aspi/ntfa/src/main.c',
											  'aspi/ntfa/src/ntfa_alloc.c',
											  'aspi/ntfa/src/ntfa_blas.c',
											  'aspi/ntfa/src/ntfa_divnnsc.c',
											  'aspi/ntfa/src/ntfa_conjgrad.c',
											  'aspi/ntfa/src/ntfa_weight2.c',
											  'aspi/ntfa/src/ntfa_decart.c',
											  'aspi/ntfa/src/ntfa_triangle.c',
											  'aspi/ntfa/src/ntfa_ntriangle.c',
											  'aspi/ntfa/src/ntfa_ntrianglen.c'	],
										depends=glob.glob('aspi/ntfa/src/*.h'),
                                        include_dirs=[numpy.get_include()])
                                                                
## below compile ortho
orthoc_module = Extension('orthocfun', sources=['aspi/ortho/src/orthocfuns.c'], 
										include_dirs=[numpy.get_include()])

## below compile radon
radonc_module = Extension('radoncfun', sources=['aspi/radon/src/radon.c','aspi/radon/src/adjnull.c'],include_dirs=[numpy.get_include()])
                                                                
modules=[]
modules=modules+[dipc_module,sofc_module,sofc3d_module,sointc2d_module,sointc3d_module,bpc_module,paintc2d_module,cohc_module]
modules.append(eikonalc_module)
modules.append(eikonalvtic_module)
modules=modules+[aps_module,afd_module,pfwi_module]
modules=modules+[nprec3d_module,ftfa_module]
modules.append(ntfac_module)
modules.append(orthoc_module)
modules.append(radonc_module)
    
setup(
    name="aspi",
    version="0.0.0.1",
    license='MIT License',
    description="ASPI: Advanced Seismic Processing and Imaging",
    long_description=long_description,
    author="aspi developing team",
    author_email="chenyk2016@gmail.com",
    url="https://github.com/aaspip/aspi",
    ext_modules=modules,
    packages=find_packages(),
    include_package_data=True,
#     exclude_package_data={
#             'aspi.seistr': ['*'],
#             'aspi.seistr': ['src/*'],
#             'aspi.ekfmm': ['src/*'],
#     },
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics"
    ],
    keywords=[
        "seismology", "earthquake seismology", "exploration seismology", "array seismology", "denoising", "science", "engineering", "structure", "local slope", "filtering"
    ],
    install_requires=[
        "numpy", "scipy", "matplotlib"
    ],
    extras_require={
        "docs": ["sphinx", "ipython", "runipy"]
    }
)
