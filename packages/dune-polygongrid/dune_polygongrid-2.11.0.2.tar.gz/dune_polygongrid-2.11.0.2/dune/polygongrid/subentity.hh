#ifndef DUNE_POLYGONGRID_SUBENTITY_HH
#define DUNE_POLYGONGRID_SUBENTITY_HH

#include <cassert>

#include <dune/geometry/dimension.hh>

#include <dune/polygongrid/meshobjects.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // numSubEntities
    // --------------

    template< class Item >
    inline static std::size_t numSubEntities ( Item item, Dune::Codim< 0 > ) noexcept
    {
      return 1u;
    }

    template< class ct >
    inline static std::size_t numSubEntities ( Node< ct > cell, Dune::Codim< 1 > ) noexcept
    {
      return cell.halfEdges().size();
    }

    template< class ct >
    inline static std::size_t numSubEntities ( Node< ct > cell, Dune::Codim< 2 > ) noexcept
    {
      return cell.halfEdges().size();
    }

    template< class ct >
    inline static std::size_t numSubEntities ( HalfEdge< ct > halfEdge, Dune::Codim< 1 > ) noexcept
    {
      return 2u;
    }



    // subEntity
    // ---------

    template< class Item >
    inline static Item subEntity ( Item item, Dune::Codim< 0 >, std::size_t i ) noexcept
    {
      assert( i == 0u );
      return item;
    }

    template< class ct >
    inline static HalfEdge< ct > subEntity ( Node< ct > cell, Dune::Codim< 1 >, std::size_t i ) noexcept
    {
      assert( i < cell.halfEdges().size() );
      return cell.halfEdges().begin()[ i ];
    }

    template< class ct >
    inline static Node< ct > subEntity ( Node< ct > cell, Dune::Codim< 2 >, std::size_t i ) noexcept
    {
      assert( i < cell.halfEdges().size() );
      return cell.halfEdges().begin()[ i ].target();
    }

    template< class ct >
    inline static Node< ct > subEntity ( HalfEdge< ct > halfEdge, Dune::Codim< 1 >, std::size_t i ) noexcept
    {
      assert( i < 2u );
      return (i == 1u ? halfEdge.target() : halfEdge.flip().target());
    }

  } // namespace __PolygonGrid

} // namespace Dune


#endif // #ifndef DUNE_POLYGONGRID_SUBENTITY_HH
