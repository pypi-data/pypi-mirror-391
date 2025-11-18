#ifndef DUNE_POLYGONGRID_DGF_HH
#define DUNE_POLYGONGRID_DGF_HH

#include <cstddef>

#include <algorithm>
#include <fstream>
#include <iosfwd>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include <dune/common/exceptions.hh>

#include <dune/geometry/dimension.hh>
#include <dune/geometry/type.hh>

#include <dune/grid/io/file/dgfparser/dgfparser.hh>
#include <dune/grid/io/file/dgfparser/dgfgridfactory.hh>

#include <dune/polygongrid/grid.hh>
#include <dune/polygongrid/gridfactory.hh>

namespace Dune
{

  // External Forward Declarations
  // -----------------------------

  template< class Grid >
  struct DGFGridInfo;



  // DGFGridInfo
  // -----------

  template< class ct >
  struct DGFGridInfo< PolygonGrid< ct > >
  {
    static constexpr int refineStepsForHalf () { return std::numeric_limits< int > :: max(); }

    static constexpr double refineWeight () { return 1.0; }
  };



  // DGFGridFactory
  // --------------

  template< class ct >
  struct DGFGridFactory< PolygonGrid< ct > >
  {
    typedef PolygonGrid< ct > Grid;
    static const int dimension = 2;

    typedef typename MPIHelper::MPICommunicator MPICommunicator;
    typedef FieldVector< ct, 2 > GlobalCoordinate;

    typedef Dune::Intersection< const Grid, __PolygonGrid::Intersection< const Grid > > Intersection;

    explicit DGFGridFactory ( std::istream &input, const MPICommunicator comm = MPIHelper::getCommunicator() )
      : parser_( 0, 1 )
    {
      generate( input );
    }

    explicit DGFGridFactory ( const std::string &filename, MPICommunicator comm = MPIHelper::getCommunicator() )
      : parser_( 0, 1 )
    {
      std::ifstream input( filename );
      generate( input );
    }

    Grid *grid () { return grid_.release(); }

    bool wasInserted ( const Intersection &intersection ) const { return (findFace( intersection ) != parser_.facemap.end()); }

    int boundaryId ( const Intersection &intersection ) const
    {
      const auto pos = findFace( intersection );
      if( pos != parser_.facemap.end() )
        return pos->second.first;
      else
        return (intersection.boundary() ? 1 : 0);
    }

    bool haveBoundaryParameters () const { return parser_.haveBndParameters; }

    const DGFBoundaryParameter::type &boundaryParameter ( const Intersection &intersection ) const
    {
      const auto pos = findFace( intersection );
      if( pos != parser_.facemap.end() )
        return pos->second.second;
      else
        return DGFBoundaryParameter::defaultValue();
    }

    template< int codim >
    int numParameters () const
    {
      return (codim == 0 ? parser_.nofelparams : (codim == dimension ? parser_.nofvtxparams : 0));
    }

    std::vector< double > &parameter ( const typename Grid::template Codim< 0 >::Entity &element )
    {
      if( numParameters< 0 >() <= 0 )
        DUNE_THROW( InvalidStateException, "Calling DGFGridFactory::parameter is only allowed if there are parameters." );
      return parser_.elParams[ element.impl().index() ];
    }

    std::vector< double > &parameter ( const typename Grid::template Codim< dimension >::Entity &vertex )
    {
      if( numParameters< dimension >() <= 0 )
        DUNE_THROW( InvalidStateException, "Calling DGFGridFactory::parameter is only allowed if there are parameters." );
      return parser_.vtxParams[ vertex.impl().index() ];
    }

  private:
    void generate ( std::istream &input );

    DuneGridFormatParser::facemap_t::const_iterator findFace ( const Intersection &intersection ) const
    {
      const unsigned int p0 = intersection.impl().item().target().uniqueIndex();
      const unsigned int p1 = intersection.impl().item().flip().target().uniqueIndex();
      DuneGridFormatParser::facemap_t::key_type key( { p0, p1 }, false );
      return parser_.facemap.find( key );
    }

    std::unique_ptr< Grid > grid_;
    DuneGridFormatParser parser_;
  };



  // DGFGridFactory::generate
  // ------------------------

  template< class ct >
  inline void DGFGridFactory< PolygonGrid< ct > >::generate ( std::istream &input )
  {
    parser_.element = DuneGridFormatParser::General;

    if( !parser_.readDuneGrid( input, dimension, GlobalCoordinate::dimension ) )
      DUNE_THROW( DGFException, "Unable to read DGF stream." );

    std::vector< GlobalCoordinate > vertices( parser_.nofvtx );
    for( int i = 0; i < parser_.nofvtx; ++i )
      std::copy( parser_.vtx[ i ].begin(), parser_.vtx[ i ].end(), vertices[ i ].begin() );

    std::vector< std::size_t > counts( parser_.nofelements );
    for( int i = 0; i < parser_.nofelements; ++i )
      counts[ i ] = parser_.elements[ i ].size();

    __PolygonGrid::MultiVector< std::size_t > polygons( counts );
    for( int i = 0; i < parser_.nofelements; ++i )
    {
      std::copy( parser_.elements[ i ].begin(), parser_.elements[ i ].end(), polygons[ i ].begin() );
      if( counts[ i ] == 4u )
        std::swap( polygons[ i ][ 2u ], polygons[ i ][ 3u ] );

      // insert polygon oriented counter-clockwise
      const GlobalCoordinate a = vertices[ polygons[ i ][ 1u ] ] - vertices[ polygons[ i ][ 0u ] ];
      const GlobalCoordinate b = vertices[ polygons[ i ][ 2u ] ] - vertices[ polygons[ i ][ 0u ] ];
      if( a[ 0 ]*b[ 1 ] < a[ 1 ]*b[ 0 ] )
        std::reverse( polygons[ i ].begin(), polygons[ i ].end() );
    }

    grid_.reset( new Grid( std::make_shared< typename Grid::Mesh >( vertices, polygons ), __PolygonGrid::Primal ) );
  }

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_DGF_HH
