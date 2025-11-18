#ifndef DUNE_POLYGONGRID_GRIDVIEW_HH
#define DUNE_POLYGONGRID_GRIDVIEW_HH

#include <functional>
#include <type_traits>

#include <dune/common/parallel/communication.hh>

#include <dune/geometry/type.hh>

#include <dune/grid/common/datahandleif.hh>
#include <dune/grid/common/gridenums.hh>

#include <dune/polygongrid/declaration.hh>
#include <dune/polygongrid/capabilities.hh>
#include <dune/polygongrid/entity.hh>
#include <dune/polygongrid/entityiterator.hh>
#include <dune/polygongrid/indexset.hh>
#include <dune/polygongrid/intersection.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // GridView
    // --------

    template< class ct >
    class GridView
    {
      typedef GridView< ct > This;

    public:
      typedef PolygonGrid< ct > Grid;

      typedef __PolygonGrid::IndexSet< ct > IndexSet;

      template< int codim >
      struct Codim
      {
        typedef typename std::conditional< codim == 1, HalfEdge< ct >, Node< ct > >::type Item;

        typedef Dune::Entity< codim, 2, const Grid, __PolygonGrid::Entity > Entity;

        typedef Dune::EntitySeed< const Grid, __PolygonGrid::EntitySeed< typename Item::Index, codim > > EntitySeed;
        typedef Dune::Geometry< 2 - codim, 2, const Grid, __PolygonGrid::Geometry > Geometry;

        // local geometry does not make sense; add a phony typedef
        //typedef Geometry LocalGeometry;
        typedef typename std::conditional< codim == 1,
            Dune::Geometry< 2 - codim, 2, const Grid, __PolygonGrid::LocalGeometry >,
            Geometry > :: type LocalGeometry;

        template< PartitionIteratorType pitype >
        struct Partition
        {
          typedef Dune::EntityIterator< codim, const Grid, __PolygonGrid::EntityIterator< codim, const Grid > > Iterator;
        };

        typedef typename Partition< All_Partition >::Iterator Iterator;
      };

      typedef Dune::Intersection< const Grid, __PolygonGrid::Intersection< const Grid > > Intersection;
      typedef Dune::IntersectionIterator< const Grid, __PolygonGrid::IntersectionIterator< const Grid >, __PolygonGrid::Intersection< const Grid > > IntersectionIterator;

      typedef Dune::Communication< No_Comm > Communication;
      typedef Communication CollectiveCommunication;

      static const bool conforming = Capabilities::isLevelwiseConforming< Grid >::v;

      explicit GridView ( const Grid &grid ) : grid_( grid ) {}

      const IndexSet &indexSet () const { return grid().leafIndexSet(); }

      bool isConforming() const { return bool(conforming); }

      template< class Entity >
      bool contains ( const Entity &entity ) const
      {
        return indexSet().contains( entity );
      }

      int size ( int codim ) const { return indexSet().size( codim ); }

      int size ( GeometryType type ) const { return indexSet().size( type ); }

      template< int codim, PartitionIteratorType pitype >
      typename Codim< codim >::template Partition< pitype >::Iterator begin () const
      {
        typedef __PolygonGrid::EntityIterator< codim, const Grid > IteratorImpl;
        if( pitype != Ghost_Partition )
          return IteratorImpl( Tag::begin, grid().mesh(), grid().type() );
        else
          return IteratorImpl( Tag::end, grid().mesh(), grid().type() );
      }

      template< int codim, PartitionIteratorType pitype >
      typename Codim< codim >::template Partition< pitype >::Iterator end () const
      {
        typedef __PolygonGrid::EntityIterator< codim, const Grid > IteratorImpl;
        return IteratorImpl( Tag::end, grid().mesh(), grid().type() );
      }

      template< int codim >
      typename Codim< codim >::template Partition< All_Partition >::Iterator begin () const
      {
        return begin< codim, All_Partition >();
      }

      template< int codim >
      typename Codim< codim >::template Partition< All_Partition >::Iterator end () const
      {
        return end< codim, All_Partition >();
      }

      IntersectionIterator ibegin ( const typename Codim< 0 >::Entity &entity ) const
      {
        typedef __PolygonGrid::IntersectionIterator< const Grid > IntersectionIteratorImpl;
        return IntersectionIteratorImpl( entity.impl().item().halfEdges().begin() );
      }

      IntersectionIterator iend ( const typename Codim< 0 >::Entity &entity ) const
      {
        typedef __PolygonGrid::IntersectionIterator< const Grid > IntersectionIteratorImpl;
        return IntersectionIteratorImpl( entity.impl().item().halfEdges().end() );
      }

      template< class DataHandle, class DataType >
      void communicate ( CommDataHandleIF< DataHandle, DataType > &, InterfaceType, CommunicationDirection ) const
      {}

      const CollectiveCommunication &comm () const { return grid().comm(); }

      const Grid &grid () const { return grid_; }

      int ghostSize ( int codim ) const { return 0; }
      int overlapSize ( int codim ) const { return 0; }

    private:
      std::reference_wrapper< const Grid > grid_;
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_GRIDVIEW_HH
