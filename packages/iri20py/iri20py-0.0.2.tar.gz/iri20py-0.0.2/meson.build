# SPDX-FileCopyrightText: 2023 Sunip K. Mukherjee
#
# SPDX-License-Identifier: Apache-2.0

project('iri20py', 'c',
  version : '1.0',
  license: 'BSD-3',
  meson_version: '>=0.64.0',
  default_options : ['warning_level=2'],
)

add_languages('fortran')

py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

install_dir = join_paths(py.get_install_dir(), 'iri20py')

fortran_srcs = [
  'src/IRI2020/dfp.f90',
  'src/IRI2020/cira.f',
  'src/IRI2020/igrf.f',
  'src/IRI2020/iridreg.f',
  'src/IRI2020/iriflip.f',
  'src/IRI2020/irifun.f',
  'src/IRI2020/irisub.f',
  'src/IRI2020/iritec.f',
  'src/IRI2020/rocdrift.f',
]

py.install_sources(
    'src/iri20py/__init__.py',
    'src/iri20py/base.py',
    'src/iri20py/download.py',
    'src/iri20py/settings.py',
    'src/iri20py/utils.py',
    subdir: 'iri20py',
    pure: false,
)

install_subdir(
    'src/IRI2020/data',
    install_dir: install_dir,
    strip_directory: false,
)

iri20_static = static_library('iri20',
  fortran_srcs,
  fortran_args : ['-cpp', '-march=native', '-ffast-math', '-std=legacy'],
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
  'src/IRI2020/irishim.f90',
]

fortshim_tgt = custom_target('iri20shimmodule.c',
  input : fortshim_srcs,
  output : ['iri20shimmodule.c', 'iri20shim-f2pywrappers.f'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'iri20shim', '--lower']
)

inc_np = include_directories(incdir_numpy, incdir_f2py)

py.extension_module('iri20shim',
  fortshim_srcs + [fortshim_tgt],
  incdir_f2py / 'fortranobject.c',
  include_directories: inc_np,
  dependencies : py_dep,
  link_with: [iri20_static],
  install : true,
  install_dir: install_dir
)