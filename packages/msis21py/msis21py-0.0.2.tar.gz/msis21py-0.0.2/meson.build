# SPDX-FileCopyrightText: 2023 Sunip K. Mukherjee
#
# SPDX-License-Identifier: Apache-2.0

project('msis21py', 'c',
  version : '1.0',
  license: 'BSD-3',
  meson_version: '>=0.64.0',
  default_options : ['warning_level=2'],
)

add_languages('fortran')

fs = import('fs')
py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

install_dir = join_paths(py.get_install_dir(), 'msis21py')
build_dir = meson.build_root()
msis_tar = build_dir / 'nrlmsis21.tar.gz'
msis_src = build_dir / 'nrlmsis21'

run_command(py, [
  'scripts/downloader.py',
  'https://map.nrl.navy.mil/map/pub/nrl/NRLMSIS/NRLMSIS2.1/nrlmsis2.1.tar.gz',
  msis_tar,
  '-hash',
  'md5',
  'b4d2001e09333b1b97496627d8b70032',
], check: true)

run_command(
  py, [
  'scripts/untar.py',
  msis_tar,
  msis_src
], check: true)

fortran_srcs = [
  msis_src / 'msis_calc.F90',
  msis_src / 'msis_constants.F90',
  msis_src / 'msis_dfn.F90',
  msis_src / 'msis_gfn.F90',
  msis_src / 'msis_gtd8d.F90',
  msis_src / 'msis_init.F90',
  msis_src / 'msis_tfn.F90',
  msis_src / 'msis_utils.F90',
]

py.install_sources(
    'src/msis21py/__init__.py',
    'src/msis21py/base.py',
    'src/msis21py/settings.py',
    'src/msis21py/utils.py',
    subdir: 'msis21py',
    pure: false,
)

msis21_static = static_library('msis21',
  fortran_srcs,
  fortran_args : ['-march=native', '-ffast-math'],
  install : false,
)

incdir_numpy = run_command(py,
  [
    '-c',
    'import numpy; print(numpy.get_include())'
  ],
  check: true
).stdout().strip()

incdir_f2py = run_command(py,
    ['-c', 'import numpy.f2py; print(numpy.f2py.get_include())'],
    check : true
).stdout().strip()

fortshim_srcs = [
  'src/msis21fort/msis21shim.f90',
]

fortshim_tgt = custom_target('msis21shimmodule.c',
  input : fortshim_srcs,
  output : ['msis21shimmodule.c', 'msis21shim-f2pywrappers.f'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'msis21shim', '--lower']
)

fs.copyfile(msis_src / 'msis21.parm', 'msis21.parm', install_dir: install_dir, install: true)

inc_np = include_directories(incdir_numpy, incdir_f2py)

py.extension_module('msis21shim',
  fortshim_srcs + [fortshim_tgt],
  incdir_f2py / 'fortranobject.c',
  include_directories: inc_np,
  dependencies : py_dep,
  link_with: [msis21_static],
  install : true,
  install_dir: install_dir
)