#include <config.h>

#include <dune/polygongrid/mesh.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // boundaries
    // ----------

    MultiVector< std::size_t > boundaries ( std::size_t numVertices, const MultiVector< std::size_t > &polygons )
    {
      // count number of polygons adjacent to a vertex
      std::vector< std::size_t > count( numVertices, 0u );
      for( std::size_t vtx : polygons.values() )
        ++count[ vtx ];

      // store succeeding vertices
      MultiVector< std::size_t > halfEdges( count, std::numeric_limits< std::size_t >::max() );
      std::fill( count.begin(), count.end(), 0u );
      for( auto polygon : polygons )
      {
        const std::size_t n = polygon.size();
        for( std::size_t j = 0u; j < n; ++j )
        {
          const std::size_t vtx = polygon[ j ];
          halfEdges[ vtx ][ count[ vtx ]++ ] = polygon[ (j+1)%n ];
        }
      }

      // if a preceeding vertex is not in the list, we have a boundary edge
      MultiVector< std::size_t > boundaries;
      std::vector< std::size_t > edge( 2 );
      for( auto polygon : polygons )
      {
        const std::size_t n = polygon.size();
        for( std::size_t j = 0u; j < n; ++j )
        {
          edge[ 0 ] = polygon[ j ];
          edge[ 1 ] = polygon[ (j+n-1)%n ];
          if( std::find( halfEdges[ edge[ 0 ] ].begin(), halfEdges[ edge[ 0 ] ].end(), edge[ 1 ] ) == halfEdges[ edge[ 0 ] ].end() )
            boundaries.push_back( edge );
        }
      }
      return boundaries;
    }



    // printStructure
    // --------------

    void printStructure ( const MultiVector< IndexPair > &nodes, std::ostream &out )
    {
      out << std::endl;
      for( std::size_t i = 0u; i < nodes.size(); ++i )
      {
        auto node = nodes[ i ];
        out << "node " << i << ": ";
        for( IndexPair p : node )
        {
          out << "  " << p.first;
          if( p.second < std::numeric_limits< std::size_t >::max() )
            out << " [" << p.second << "]";
          else
            out << " [-]";
        }
        std::cout << std::endl;
      }
    }


    // meshStructure
    // -------------

    MeshStructure meshStructure ( std::size_t numVertices, const MultiVector< std::size_t > &polygons, const MultiVector< std::size_t > &boundaries )
    {
      const std::size_t numPolygons = polygons.size();
      const std::size_t numBoundaries = boundaries.size();

      MeshStructure nodes;
      std::vector< std::size_t > count;

      // number of halfedges for primal grid:
      // - p.size() for each polygon p
      // - 3 for each boundary edge
      // - 2 for each boundary vertex
      count = polygons.sizes();
      count.insert( count.end(), numBoundaries, 3u );
      count.insert( count.end(), numBoundaries, 2u );

      // initialize primal nodes (without target position)
      nodes[ Dual ].resize( count );
      auto makeIndexPair = [] ( std::size_t i ) { return IndexPair( i, std::numeric_limits< std::size_t >::max() ); };
      for( std::size_t i = 0; i < numPolygons; ++i )
        std::transform( polygons[ i ].begin(), polygons[ i ].end(), nodes[ Dual ][ i ].begin(), makeIndexPair );
      for( std::size_t i = 0; i < numBoundaries; ++i )
      {
        // create boundary edge node
        auto item = nodes[ Dual ][ numPolygons + i ];
        item[ 0 ] = IndexPair( boundaries[ i ][ 0 ], 1 );
        item[ 1 ] = makeIndexPair( boundaries[ i ][ 1 ] );
        item[ 2 ] = IndexPair( numVertices + 2*i+1, 0 );
      }
      for( std::size_t i = 0; i < numBoundaries; ++i )
      {
        // create boundary vertex node
        auto item = nodes[ Dual ][ numPolygons + numBoundaries + i ];
        item[ 0 ] = IndexPair( boundaries[ i ][ 0 ], 2 );
        item[ 1 ] = IndexPair( numVertices + 2*i, 0 );
      }

      // number of halfedges for dual grid:
      // - for each regular vertex:
      //   + 1 for each adjacent polygon
      //   + 1 for each adjacent boundary edge (for bisected boundary edge)
      //   + 1 for being a boundary vertex (for vertex element)
      // - 1 for each bisected boundary edge center
      count = std::vector< std::size_t >( numVertices, 0u );
      for( std::size_t vtx : polygons.values() )
        ++count[ vtx ];
      for( auto boundary : boundaries )
      {
        ++count[ boundary[ 0 ] ];
        for( std::size_t vtx : boundary )
          ++count[ vtx ];
      }
      count.insert( count.end(), 2*numBoundaries, 1u );

      // a regular vertex points to:
      // - the succeeding position in a polygon
      // - the second position in a boundary edge node
      // - the second position in a boundary vertex node
      nodes[ Primal ].resize( count );
      std::fill( count.begin(), count.end(), 0u );
      for( std::size_t i = 0; i < numBoundaries; ++i )
      {
        // boundary vertices automatically get 3 connections
        const std::size_t v0 = boundaries[ i ][ 0 ];
        count[ v0 ] = 3;
        nodes[ Primal ][ v0 ][ 0 ] = IndexPair( numPolygons + i, 1 );
        nodes[ Primal ][ v0 ][ 1 ] = IndexPair( numPolygons + numBoundaries + i, 1 );
        const std::size_t v1 = boundaries[ i ][ 1 ];
        nodes[ Primal ][ v1 ][ 2 ] = IndexPair( numPolygons + i, 2 );
      }
      for( std::size_t i = 0; i < numBoundaries; ++i )
      {
        nodes[ Primal ][ numVertices + 2*i ][ 0 ] = IndexPair( numPolygons + i, 0 );
        const std::size_t j = nodes[ Primal ][ boundaries[ i ][ 1 ] ][ 0 ].first;
        nodes[ Primal ][ numVertices + 2*i+1 ][ 0 ] = IndexPair( j + numBoundaries, 0 );
      }
      for( std::size_t i = 0; i < numPolygons; ++i )
      {
        const std::size_t n = polygons[ i ].size();
        for( std::size_t j = 0u; j < n; ++j )
        {
          const std::size_t vtx = polygons[ i ][ j ];
          nodes[ Primal ][ vtx ][ count[ vtx ]++ ] = IndexPair( i, (j+1)%n );
        }
      }

      // sort regular primal nodes
      for( std::size_t i = 0; i < numVertices; ++i )
      {
        auto node1 = nodes[ Primal ][ i ];
        const std::size_t n1 = node1.size();
        std::size_t k1 = (node1[ 0 ].first >= numPolygons ? 2u : 0u);
        while( true )
        {
          assert( k1 < n1 );
          // look at preceeding half edge
          auto node2 = nodes[ Dual ][ node1[ k1 ].first ];
          const std::size_t n2 = node2.size();
          const std::size_t k2 = node1[ k1 ].second;
          ++k1;

          // the preceeding vertex points to us
          assert( node2[ (k2+n2-1)%n2 ].first == i );
          node2[ (k2+n2-1)%n2 ].second = k1 % n1;

          // now find the next half edge
          std::size_t nbvtx = node2[ (k2+n2-2)%n2 ].first;
          auto pos = std::find_if( node1.begin()+k1, node1.end(), [ &nodes, nbvtx ] ( IndexPair p ) { return (nodes[ Dual ][ p ].first == nbvtx); } );
          assert( (k1 == n1) || (pos != node1.end()) );
          if( pos == node1.end() )
            break;
          std::swap( node1[ k1 ], *pos );
        }
      }

      return nodes;
    }



    // checkStructure
    // --------------

    bool checkStructure ( const MeshStructure &nodes, MeshType type, std::ostream &out )
    {
      const std::size_t size1 = nodes[ type ].size();
      const std::array< MeshType, 4 > types = {{ type, dual( type ), type, dual( type ) }};
      for( std::size_t i = 0; i < size1; ++i )
      {
        const std::size_t n = nodes[ type ][ i ].size();
        for( std::size_t j = 0u; j < n; ++j )
        {
          std::array< IndexPair, 5 > p;
          p[ 0 ] = IndexPair( i, j );
          for( std::size_t k = 0u; k < 4u; ++k )
            p[ k+1 ] = nodes[ types[ k ] ].at( p[ k ] );
          if( p[ 4 ] == p[ 0 ] )
            continue;

          out << "Invalid half edge cycle in " << type << " mesh:";
          for( IndexPair q : p )
            out << "  " << q.first << " [" << q.second << "]";
          out << std::endl;

          return false;
        }
      }

      return true;
    }

    bool checkStructure ( const MeshStructure &nodes, std::ostream &out )
    {
      return checkStructure( nodes, Primal ) && checkStructure( nodes, Dual );
    }



    // edgeIndices
    // -----------

    std::vector< std::size_t > edgeIndices ( const MeshStructure &nodes, MeshType type )
    {
      const MultiVector< IndexPair > &vertices = nodes[ type ];
      const MultiVector< IndexPair > &cells = nodes[ dual( type ) ];

      const std::size_t size = cells.values().size();
      std::vector< std::size_t > edgeIndices( size, std::numeric_limits< std::size_t >::max() );

      std::size_t numEdges = 0;
      const std::size_t numCells = cells.size();
      for( std::size_t i = 0; i < numCells; ++i )
      {
        const std::size_t n = cells[ i ].size();
        for( std::size_t j = 0u; j < n; ++j )
        {
          const std::size_t k = cells.position_of( i, j );
          if( edgeIndices[ k ] < std::numeric_limits< std::size_t >::max() )
            continue;

          const IndexPair p = vertices[ cells[ i ][ j ] ];
          assert( edgeIndices[ cells.position_of( p ) ] == std::numeric_limits< std::size_t >::max() );
          edgeIndices[ k ] = edgeIndices[ cells.position_of( p ) ] = numEdges++;
        }
      }

      assert( 2u*numEdges == size );
      return edgeIndices;
    }

  } // namespace __PolygonGrid

} // namespace Dune
