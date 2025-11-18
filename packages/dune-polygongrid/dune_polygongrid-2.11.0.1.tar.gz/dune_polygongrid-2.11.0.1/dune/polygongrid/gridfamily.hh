#ifndef DUNE_POLYGONGRID_GRIDFAMILY_HH
#define DUNE_POLYGONGRID_GRIDFAMILY_HH

#include <dune/common/parallel/mpicommunication.hh>

#include <dune/geometry/dimension.hh>

#include <dune/grid/common/entityseed.hh>
#include <dune/grid/common/grid.hh>

#include <dune/polygongrid/gridview.hh>
#include <dune/polygongrid/idset.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // GridViewTraits
    // --------------

    template< class ct >
    struct GridViewTraits
    {
      typedef __PolygonGrid::GridView< ct > GridViewImp;

      typedef ct ctype;

      typedef typename GridViewImp::Grid Grid;
      typedef typename GridViewImp::IndexSet IndexSet;

      template< int codim >
      using Codim = typename GridViewImp::template Codim< codim >;

      typedef typename GridViewImp::IntersectionIterator IntersectionIterator;
      typedef typename GridViewImp::Intersection Intersection;

      typedef typename GridViewImp::Communication Communication;
      typedef Communication CollectiveCommunication;

      static const bool conforming = true;
    };



    // GridFamily
    // ----------

    template< class ct >
    struct GridFamily
    {
      struct Traits
      {
        typedef ct ctype;

        typedef Dune::PolygonGrid< ct > Grid;

        typedef Dune::GridView< GridViewTraits< ct > > MacroGridView;
        typedef MacroGridView LeafGridView;
        typedef MacroGridView LevelGridView;

        typedef __PolygonGrid::IdSet< ct > LocalIdSet;
        typedef LocalIdSet GlobalIdSet;

        typedef __PolygonGrid::IndexSet< ct > LeafIndexSet;
        typedef __PolygonGrid::IndexSet< ct > LevelIndexSet;

        typedef Dune::Intersection< const Grid, __PolygonGrid::Intersection< const Grid > > LeafIntersection;
        typedef Dune::IntersectionIterator< const Grid, __PolygonGrid::IntersectionIterator< const Grid >, __PolygonGrid::Intersection< const Grid > > LeafIntersectionIterator;

        typedef Dune::Intersection< const Grid, __PolygonGrid::Intersection< const Grid > > LevelIntersection;
        typedef Dune::IntersectionIterator< const Grid, __PolygonGrid::IntersectionIterator< const Grid >, __PolygonGrid::Intersection< const Grid > > LevelIntersectionIterator;

        typedef Dune::EntityIterator< 0, const Grid, __PolygonGrid::EntityIterator< 0, const Grid > > HierarchicIterator;

        typedef Dune::Communication< No_Comm > Communication;
        typedef Communication CollectiveCommunication;

        template< int codim >
        struct Codim
        {
          typedef typename std::conditional< codim == 1, HalfEdge< ct >, Node< ct > >::type Item;

          typedef Dune::Entity< codim, 2, const Grid, __PolygonGrid::Entity > Entity;

          typedef Dune::EntitySeed< const Grid, __PolygonGrid::EntitySeed< typename Item::Index, codim > > EntitySeed;
          typedef Dune::Geometry< 2 - codim, 2, const Grid, __PolygonGrid::Geometry > Geometry;

          // local geometry does not make sense; add a phony typedef
          typedef typename std::conditional< codim == 1,
              Dune::Geometry< 2 - codim, 2, const Grid, __PolygonGrid::LocalGeometry >,
              Geometry > :: type LocalGeometry;

          //typedef Geometry LocalGeometry;

          template< PartitionIteratorType pitype >
          struct Partition
          {
            typedef Dune::EntityIterator< codim, const Grid, __PolygonGrid::EntityIterator< codim, const Grid > > LeafIterator;
            typedef Dune::EntityIterator< codim, const Grid, __PolygonGrid::EntityIterator< codim, const Grid > > LevelIterator;
          };

          typedef typename Partition< All_Partition >::LeafIterator LeafIterator;
          typedef typename Partition< All_Partition >::LevelIterator LevelIterator;
        };
      };
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_GRIDFAMILY_HH
