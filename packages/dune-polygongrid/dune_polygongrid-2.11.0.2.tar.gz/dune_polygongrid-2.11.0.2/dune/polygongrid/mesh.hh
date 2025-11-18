#ifndef DUNE_POLYGONGRID_MESH_HH
#define DUNE_POLYGONGRID_MESH_HH

#include <cstddef>

#include <algorithm>
#include <array>
#include <iostream>
#include <limits>
#include <utility>
#include <vector>

#include <dune/common/fvector.hh>
#include <dune/common/math.hh>

#include <dune/geometry/dimension.hh>

#include <dune/polygongrid/multivector.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // MeshType
    // --------

    enum MeshType : std::size_t { Primal = 0u, Dual = 1u };

    inline static constexpr MeshType dual ( MeshType type ) noexcept { return static_cast< MeshType >( type^1u ); }

    inline std::ostream &operator<< ( std::ostream &out, MeshType type ) { return out << (type == Primal ? "primal" : "dual"); }

    typedef std::integral_constant< MeshType, Primal > PrimalType;
    typedef std::integral_constant< MeshType, Dual > DualType;

    namespace
    {

      const PrimalType primalMesh = {};
      const DualType dualMesh = {};

    } // anonymous namespace



    // Index
    // -----

    template< class Tag >
    class Index
    {
      typedef Index< Tag > This;

    public:
      Index () noexcept : index_( std::numeric_limits< std::size_t >::max() ) {}
      constexpr Index ( std::size_t index, MeshType type ) : index_( 2u*index + type ) {}

      operator std::size_t () const noexcept { return (index_ / 2u); }

      explicit operator bool () const noexcept { return (index_ < std::numeric_limits< std::size_t >::max()); }

      bool operator== ( const This &other ) const noexcept { return (index_ == other.index_); }
      bool operator!= ( const This &other ) const noexcept { return (index_ != other.index_); }
      bool operator< ( const This &other ) const noexcept { return (index_ < other.index_); }
      bool operator<= ( const This &other ) const noexcept { return (index_ <= other.index_); }
      bool operator> ( const This &other ) const noexcept { return (index_ > other.index_); }
      bool operator>= ( const This &other ) const noexcept { return (index_ >= other.index_); }

      This &operator++ () noexcept { index_ += 2u; return *this; }
      This &operator-- () noexcept { index_ -= 2u; return *this; }

      This &operator+= ( std::ptrdiff_t n ) noexcept { index_ += 2u*n; return *this; }
      This &operator-= ( std::ptrdiff_t n ) noexcept { index_ += 2u*n; return *this; }

      friend This operator+ ( This a, std::ptrdiff_t b ) noexcept { return a += b; }
      friend This operator+ ( std::ptrdiff_t a, This b ) noexcept { return b += a; }
      friend This operator- ( This a, std::ptrdiff_t b ) noexcept { return a -= b; }

      friend std::ptrdiff_t operator- ( This a, This b ) noexcept { return ((a.index_ - b.index_) / 2u); }

      constexpr MeshType type () const noexcept { return MeshType( index_ & 1u ); }
      // constexpr This dual () const noexcept { This copy( *this ); copy.index_ ^= 1u; return copy; }

    private:
      std::size_t index_;
    };

#if 0
    template< class Tag >
    inline static constexpr Index< Tag > dual ( Index< Tag > index ) noexcept
    {
      return index.dual();
    }
#endif



    // NodeIndex
    // ---------

    struct NodeTag
    {};

    typedef Index< NodeTag > NodeIndex;



    // HalfEdgeIndex
    // -------------

    struct HalfEdgeTag
    {};

    typedef Index< HalfEdgeTag > HalfEdgeIndex;



    // Type Definitions
    // ----------------

    typedef std::pair< std::size_t, std::size_t > IndexPair;

    typedef std::array< MultiVector< IndexPair >, 2 > MeshStructure;



    // External Forward Declarations
    // -----------------------------

    MultiVector< std::size_t > boundaries ( std::size_t numVertices, const MultiVector< std::size_t > &polygons );

    void printStructure ( const MultiVector< IndexPair > &nodes, std::ostream &out = std::cout );

    MeshStructure meshStructure ( std::size_t numVertices, const MultiVector< std::size_t > &polygons, const MultiVector< std::size_t > &boundaries );

    bool checkStructure ( const MeshStructure &nodes, MeshType type, std::ostream &out = std::cout );
    bool checkStructure ( const MeshStructure &nodes, std::ostream &out = std::cout );

    std::vector< std::size_t > edgeIndices ( const MeshStructure &nodes, MeshType type );



    // vertexPositions
    // ---------------

    template< class V >
    inline std::array< std::vector< V >, 2 > positions ( const MeshStructure &nodes, const std::vector< V > &vertices )
    {
      typedef typename FieldTraits< V >::field_type ctype;

      const std::size_t numVertices = vertices.size();
      const std::size_t numBoundaries = (nodes[ Primal ].size() - numVertices) / 2u;
      const std::size_t numPolygons = (nodes[ Dual ].size() - 2u*numBoundaries);

      std::array< std::vector< V >, 2 > positions;
      positions[ Primal ].resize( nodes[ Primal ].size(), V( 0 ) );
      positions[ Dual ].resize( nodes[ Dual ].size(), V( 0 ) );

      // copy given vertex positions
      std::copy( vertices.begin(), vertices.end(), positions[ Primal ].begin() );

      // for now, use the average of polygon vertices as center position
      for( std::size_t i = 0u; i < numPolygons; ++i )
      {
        for( IndexPair j : nodes[ Dual ][ i ] )
          positions[ Dual ][ i ] += positions[ Primal ][ j.first ];
        positions[ Dual ][ i ] *= ctype( 1 ) / ctype( nodes[ Dual ][ i ].size() );
      }

      // positions for boundary edge cells
      for( std::size_t i = numPolygons; i < numPolygons + numBoundaries; ++i )
      {
        for( std::size_t j = 0u; j < 2u; ++j )
          positions[ Dual ][ i ].axpy( ctype( 1 ) / ctype( 2 ), positions[ Primal ][ nodes[ Dual ][ i ][ j ].first ] );
      }

      // positions for boundary vertex cells
      for( std::size_t i = numPolygons + numBoundaries; i < numPolygons + 2u*numBoundaries; ++i )
        positions[ Dual ][ i ] = positions[ Primal ][ nodes[ Dual ][ i ][ 0 ].first ];

      // positions for dual boundaries
      for( std::size_t i = 0u; i < numBoundaries; ++i )
      {
        for( std::size_t j = 0u; j < 2u; ++j )
        {
          const std::size_t v = nodes[ Dual ][ numPolygons + i ][ j ].first;
          positions[ Primal ][ numVertices + 2*i+j ].axpy( ctype( 1 ) / ctype( 2 ), positions[ Primal ][ v ] );
          positions[ Primal ][ numVertices + 2*i+j ].axpy( ctype( 1 ) / ctype( 2 ), positions[ Dual ][ numPolygons + i ] );
        }
      }

      return positions;
    }



    // Mesh
    // ----

    template< class ct >
    class Mesh
    {
      typedef Mesh< ct > This;

      typedef std::pair< std::size_t, std::size_t > Pair;

      static constexpr MeshType dual ( MeshType type ) noexcept { return __PolygonGrid::dual( type ); }

    public:
      typedef FieldVector< ct, 2 > GlobalCoordinate;

      Mesh ( const std::vector< GlobalCoordinate > &vertices, const MultiVector< std::size_t > &polygons )
        : numRegularNodes_{{ vertices.size(), polygons.size() }}
      {
        MultiVector< std::size_t > boundaries = __PolygonGrid::boundaries( numRegularNodes_[ Primal ], polygons );
        nodes_ = __PolygonGrid::meshStructure( numRegularNodes_[ Primal ], polygons, boundaries );
        positions_ = __PolygonGrid::positions( nodes_, vertices );
        edgeIndices_ = __PolygonGrid::edgeIndices( nodes_, Primal );
      }

      NodeIndex target ( HalfEdgeIndex index ) const noexcept { return NodeIndex( indexPair( index ).first, index.type() ); }

      std::size_t edgeIndex ( HalfEdgeIndex index ) const noexcept
      {
        // We only store edge indices for the primal mesh.
        return edgeIndices_[ index.type() == Primal ? index : dual( index ) ];
      }

      const GlobalCoordinate &position ( NodeIndex index ) const noexcept
      {
        assert( index < positions_[ index.type() ].size() );
        return positions_[ index.type() ][ index ];
      }

      HalfEdgeIndex dual ( HalfEdgeIndex index ) const noexcept
      {
        return HalfEdgeIndex( nodes( index.type() ).position_of( indexPair( index ) ), dual( index.type() ) );
      }

      HalfEdgeIndex flip ( HalfEdgeIndex index ) const noexcept { return dual( dual( index ) ); }

      std::size_t size ( NodeIndex index ) const noexcept { return nodes( index.type() ).size( index ); }

      std::size_t numNodes ( MeshType type ) const noexcept { return nodes( type ).size(); }

      std::size_t numRegularNodes ( MeshType type ) const noexcept { return numRegularNodes_[ type ]; }

      std::size_t numBoundaries ( MeshType type ) const noexcept
      {
        return (numNodes( Primal ) - numRegularNodes( Primal )) / (2u - static_cast< std::size_t >( type ));
      }

      std::size_t numCells ( MeshType type ) const noexcept { return numRegularNodes( dual( type ) ); }

      std::size_t numEdges ( MeshType type ) const noexcept
      {
        return nodes( Primal ).values().size() / 2u - (type == Primal ? numBoundaries( Dual ) : 0u);
      }

      std::size_t numVertices ( MeshType type ) const noexcept
      {
        return (type == Primal ? numRegularNodes( type ) : numNodes( type ));
      }

      bool regular ( NodeIndex index ) const noexcept { return (static_cast< std::size_t >( index ) < numRegularNodes( index.type() )); }

      HalfEdgeIndex begin ( NodeIndex index ) const noexcept
      {
        return HalfEdgeIndex( nodes( index.type() ).begin_of( index ), dual( index.type() ) );
      }

      HalfEdgeIndex end ( NodeIndex index ) const noexcept
      {
        return HalfEdgeIndex( nodes( index.type() ).end_of( index ), dual( index.type() ) );
      }

      NodeIndex begin ( MeshType type, Codim< 0 > ) const noexcept { return NodeIndex( 0u, dual( type ) ); }
      NodeIndex end ( MeshType type, Codim< 0 > ) const noexcept { return NodeIndex( numCells( type ), dual( type ) ); }

      HalfEdgeIndex begin ( MeshType type, Codim< 1 > ) const noexcept { return begin( begin( type, Codim< 0 >() ) ); }
      HalfEdgeIndex end ( MeshType type, Codim< 1 > ) const noexcept { return end( --end( type, Codim< 0 >() ) ); }

      NodeIndex begin ( MeshType type, Codim< 2 > ) const noexcept { return NodeIndex( 0u, type ); }
      NodeIndex end ( MeshType type, Codim< 2 > ) const noexcept { return NodeIndex( numVertices( type ), type ); }

      const MultiVector< IndexPair > &nodes ( MeshType type ) const { return nodes_[ type ]; }

    private:
      const IndexPair &indexPair ( HalfEdgeIndex index ) const noexcept
      {
        assert( index < nodes_[ dual( index.type() ) ].values().size() );
        return nodes_[ dual( index.type() ) ].values()[ index ];
      }

      std::array< std::size_t, 2 > numRegularNodes_;
      MeshStructure nodes_;
      std::array< std::vector< GlobalCoordinate >, 2 > positions_;
      std::vector< std::size_t > edgeIndices_;
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_MESH_HH
