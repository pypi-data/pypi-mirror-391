set(HEADERS
  capabilities.hh
  declaration.hh
  dgf.hh
  entity.hh
  entityiterator.hh
  entityseed.hh
  geometry.hh
  grid.hh
  gridfamily.hh
  gridfactory.hh
  gridview.hh
  idset.hh
  identitymatrix.hh
  indexset.hh
  intersection.hh
  iteratortags.hh
  mesh.hh
  meshobjects.hh
  multivector.hh
  subentity.hh
)

install(FILES ${HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/dune/polygongrid)

dune_add_library(dunepolygongrid
  mesh.cc
  ADD_LIBS ${DUNE_LIBS}
)
