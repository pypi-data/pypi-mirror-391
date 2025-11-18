#ifndef DUNE_POLYGONGRID_INTERSECTION_HH
#define DUNE_POLYGONGRID_INTERSECTION_HH

#include <cassert>
#include <cstddef>

#include <type_traits>

#include <dune/common/exceptions.hh>

#include <dune/geometry/type.hh>

#include <dune/grid/common/intersection.hh>
#include <dune/grid/common/intersectioniterator.hh>

#include <dune/polygongrid/declaration.hh>
#include <dune/polygongrid/entity.hh>
#include <dune/polygongrid/geometry.hh>
#include <dune/polygongrid/meshobjects.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // Intersection
    // ------------

    template< class Grid >
    class Intersection
    {
      typedef Intersection< Grid > This;

      typedef HalfEdge< typename std::remove_const< Grid >::type::ctype > Item;

      typedef __PolygonGrid::Entity< 0, 2, Grid > EntityImpl;
      typedef __PolygonGrid::Geometry< 1, 2, Grid > GeometryImpl;
      typedef __PolygonGrid::LocalGeometry< 1, 2, Grid > LocalGeometryImpl;

    public:
      static const int dimension = 2;
      static const int codimension = 1;
      static const int mydimension = dimension - codimension;

      typedef typename std::remove_const< Grid >::type::ctype ctype;

      typedef Dune::Entity< 0, 2, Grid, __PolygonGrid::Entity > Entity;
      typedef Dune::Geometry< 1, 2, Grid, __PolygonGrid::Geometry > Geometry;
      typedef Dune::Geometry< 1, 2, Grid, __PolygonGrid::LocalGeometry > LocalGeometry;
      //typedef Geometry LocalGeometry;

      typedef typename Geometry::GlobalCoordinate GlobalCoordinate;
      typedef typename Geometry::LocalCoordinate LocalCoordinate;

      Intersection () = default;

      explicit Intersection ( Item item ) : item_( item ) {}

      bool equals ( const This &other ) const { return (item_ == other.item_); }

      bool conforming () const noexcept { return true; }

      bool boundary () const noexcept { return !neighbor(); }

      bool neighbor () const noexcept { return item().neighbor().regular(); }

      int boundaryId () const noexcept { return 1; }

      std::size_t boundarySegmentIndex () const noexcept { assert( boundary() ); return item().neighbor().boundaryIndex(); }

      Entity inside () const { return EntityImpl( item().cell() ); }
      Entity outside () const { return EntityImpl( item().neighbor() ); }

      int indexInInside () const { return item().indexInCell(); }
      int indexInOutside () const { return item().indexInNeighbor(); }

      GeometryType type () const noexcept { return GeometryTypes::cube( mydimension ); }

      Geometry geometry () const { return Geometry( GeometryImpl( item() ) ); }

      LocalGeometry geometryInInside () const
      {
        const auto& geom = this->geometry();
        const auto& elemGeo = this->inside().geometry();
        const auto& c0 = elemGeo.local( geom.corner( 0 ) );
        const auto& c1 = elemGeo.local( geom.corner( 1 ) );
        return LocalGeometry( LocalGeometryImpl(c0 , c1) );
        assert( false );
        DUNE_THROW( InvalidStateException, "Intersection::geometryInOutside does not make for arbitrary polytopes." );
      }

      LocalGeometry geometryInOutside () const
      {
        const auto& geom = this->geometry();
        const auto& elemGeo = this->outside().geometry();
        const auto& c0 = elemGeo.local( geom.corner( 0 ) );
        const auto& c1 = elemGeo.local( geom.corner( 1 ) );
        return LocalGeometry( LocalGeometryImpl(c0 , c1) );
        assert( false );
        DUNE_THROW( InvalidStateException, "Intersection::geometryInOutside does not make for arbitrary polytopes." );
      }

      GlobalCoordinate integrationOuterNormal ( const LocalCoordinate & ) const { return outerNormal(); }
      GlobalCoordinate outerNormal ( const LocalCoordinate & ) const { return outerNormal(); }

      GlobalCoordinate unitOuterNormal ( const LocalCoordinate & ) const { return centerUnitOuterNormal(); }

      GlobalCoordinate centerUnitOuterNormal () const
      {
        GlobalCoordinate normal = outerNormal();
        return normal *= ctype( 1 ) / normal.two_norm();
      }

      const Item &item () const { return item_; }

    private:
      GlobalCoordinate outerNormal () const
      {
        const GlobalCoordinate tangent = (item().target().position() - item().flip().target().position());
        return GlobalCoordinate{ tangent[ 1 ], -tangent[ 0 ] };
      }

      Item item_;
    };



    // IntersectionIterator
    // --------------------

    template< class Grid >
    class IntersectionIterator
    {
      typedef IntersectionIterator< Grid > This;

      typedef __PolygonGrid::Intersection< Grid > IntersectionImpl;

    public:
      typedef typename HalfEdges< typename std::remove_const< Grid >::type::ctype >::Iterator HalfEdgeIterator;

      typedef Dune::Intersection< const Grid, IntersectionImpl > Intersection;

      IntersectionIterator () = default;

      explicit IntersectionIterator ( const HalfEdgeIterator halfEdgeIterator ) : halfEdgeIterator_( halfEdgeIterator ) {}

      void increment () { ++halfEdgeIterator_; }

      Intersection dereference () const { return IntersectionImpl( *halfEdgeIterator_ ); }

      bool equals ( const This &other ) const { return (halfEdgeIterator_ == other.halfEdgeIterator_); }

    private:
      HalfEdgeIterator halfEdgeIterator_;
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_INTERSECTION_HH
