#include <config.h>

#include <memory>

#include <dune/common/parallel/mpihelper.hh>

#include <dune/polygongrid/grid.hh>
#include <dune/polygongrid/gridfactory.hh>
#include <dune/polygongrid/dgf.hh>

#include <dune/grid/test/checkintersectionit.hh>
#include <dune/grid/test/checkiterators.hh>
#include <dune/grid/test/checkpartition.hh>
#include <dune/grid/test/gridcheck.hh>

#include <dune/grid/io/file/vtk/vtkwriter.hh>

#if HAVE_DUNE_VIZ
#include <dune/viz/writer/vtk/polygonwriter.hh>
#endif // #if HAVE_DUNE_VIZ


typedef Dune::PolygonGrid< double > Grid;

std::unique_ptr< Grid > createArbitraryGrid ()
{
  const std::vector< Dune::FieldVector< double, 2 > > vertices
    = { { 0.0, 0.0 }, { 0.5, 0.0 }, { 1.0, 0.0 },
        { 0.0, 0.4 }, { 0.5, 0.2 }, { 0.7, 0.4 }, { 1.0, 0.4 },
        { 0.0, 0.7 }, { 0.7, 0.6 }, { 1.0, 0.6 },
        { 0.0, 1.0 }, { 0.3, 1.0 }, { 1.0, 1.0 } };
  const std::vector< std::vector< unsigned int > > polys
    = { { 0, 1, 4, 3 }, { 1, 2, 6, 5, 4 }, { 3, 4, 5, 8, 11, 7 }, { 5, 6, 9, 8 }, { 7, 11, 10 }, { 8, 9, 12, 11 } };

  Dune::GridFactory< Grid > factory;
  for( const auto &vertex : vertices )
    factory.insertVertex( vertex );
  for( const auto &poly : polys )
    factory.insertElement( Dune::GeometryTypes::none( 2 ), poly );
  return std::unique_ptr< Grid >( factory.createGrid() );
}


// performCheck
// ------------

void performCheck ( Grid &grid )
{
  std::cerr << ">>> Checking " << grid.type() << " grid..." << std::endl;
  gridcheck( grid );
  checkIterators( grid.leafGridView() );
  checkPartitionType( grid.leafGridView() );
  std::cerr << "<<< Checking intersection of " << grid.type() << " grid..." << std::endl;
  checkIntersectionIterator( grid );
  std::cout << std::endl;
}


void write ( const Grid &grid, const std::string &name )
{
#if HAVE_DUNE_VIZ
  Dune::Viz::VTKPolygonWriter< Grid::LeafGridView > vtkWriter( grid.leafGridView() );
  vtkWriter.write( name );
#else
  Dune::VTKWriter< typename Grid::LeafGridView > vtkWriter( grid.leafGridView() );
  vtkWriter.write( name );
#endif // #if HAVE_DUNE_VIZ
}


// main
// ----

int main ( int argc, char **argv )
try
{
  Dune::MPIHelper::instance( argc, argv );

  {
    Grid grid = *createArbitraryGrid();
    /*
    std::stringstream file;
    file << "DGF" << std::endl;
    file << "Interval" << std::endl;
    file << "0 0" << std::endl;
    file << "1 0.25" << std::endl;
    file << "8 2" << std::endl;
    file << "#" << std::endl;
    file << "Simplex" << std::endl;
    file << "#" << std::endl;

    Dune::GridPtr< Grid > dgf( file );

    Grid grid = *dgf;
    */

    //Grid grid = *createArbitraryGrid();

    std::cout << std::endl << std::endl;
    std::cout << "Primal Structure:" << std::endl;
    Dune::__PolygonGrid::printStructure( grid.mesh().nodes( Dune::__PolygonGrid::Primal ) );
    std::cout << std::endl;

    std::cout << std::endl << std::endl;
    std::cout << "Dual Structure:" << std::endl;
    Dune::__PolygonGrid::printStructure( grid.mesh().nodes( Dune::__PolygonGrid::Dual ) );
    std::cout << std::endl;

    performCheck( grid );
    write( grid, "primalgrid-dgf" );

    Grid dualGrid = grid.dualGrid();
    performCheck( dualGrid );
    write( dualGrid, "dualgrid-dgf" );
  }

  {
    // create arbitrary grid
    Grid grid = *createArbitraryGrid();

    std::cout << std::endl << std::endl;
    std::cout << "Primal Structure:" << std::endl;
    Dune::__PolygonGrid::printStructure( grid.mesh().nodes( Dune::__PolygonGrid::Primal ) );
    std::cout << std::endl;

    std::cout << std::endl << std::endl;
    std::cout << "Dual Structure:" << std::endl;
    Dune::__PolygonGrid::printStructure( grid.mesh().nodes( Dune::__PolygonGrid::Dual ) );
    std::cout << std::endl;

    performCheck( grid );
    write( grid, "primalgrid-arbi" );

    Grid dualGrid = grid.dualGrid();
    performCheck( dualGrid );
    write( dualGrid, "dualgrid-arbi" );
  }

  return 0;
}
catch( const Dune::Exception &e )
{
  std::cerr << e << std::endl;
  return 1;
}
