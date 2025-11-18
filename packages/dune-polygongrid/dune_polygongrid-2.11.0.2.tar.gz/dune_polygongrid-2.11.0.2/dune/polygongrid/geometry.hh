#ifndef DUNE_POLYGONGRID_GEOMETRY_HH
#define DUNE_POLYGONGRID_GEOMETRY_HH

#include <type_traits>

#include <dune/common/exceptions.hh>
#include <dune/common/fmatrix.hh>
#include <dune/common/fvector.hh>
#include <dune/common/math.hh>

#include <dune/geometry/dimension.hh>
#include <dune/geometry/type.hh>
#include <dune/geometry/axisalignedcubegeometry.hh>

#include <dune/grid/common/geometry.hh>

#include <dune/polygongrid/identitymatrix.hh>
#include <dune/polygongrid/subentity.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // Internal Forward Declarations
    // -----------------------------

    template< int mydim, int cdim, class Grid >
    class Geometry;

    template< int mydim, int cdim, class Grid >
    class LocalGeometry;


    // Geometry for Codimension 0
    // --------------------------

    template< int cdim, class Grid >
    class Geometry< 2, cdim, Grid > : public GeometryDefaultImplementation<2, cdim, Grid, Geometry>
    {
      typedef Geometry< 2, cdim, Grid > This;

    public:
      typedef typename std::remove_const_t< Grid >::ctype ctype;

      static const int mydimension = 2;
      static const int coorddimension = 2;

      typedef FieldVector< ctype, mydimension > LocalCoordinate;
      typedef FieldVector< ctype, coorddimension > GlobalCoordinate;

      //typedef IdentityMatrix< ctype, mydimension > JacobianTransposed;
      //typedef IdentityMatrix< ctype, mydimension > JacobianInverseTransposed;

      typedef Dune::AxisAlignedCubeGeometry< ctype, mydimension, coorddimension> CartesianGeometryType;
      typedef typename CartesianGeometryType :: JacobianTransposed          JacobianTransposed;
      typedef typename CartesianGeometryType :: JacobianInverseTransposed   JacobianInverseTransposed;

      void computeBoundingBox( GlobalCoordinate& lower,
                               GlobalCoordinate& upper ) const
      {
        const int nCorners = corners();
        lower = corner( 0 );
        upper = lower;
        for( int i=1; i<nCorners; ++i )
        {
          const auto& corn = corner( i );
          for( int d=0; d<coorddimension; ++d )
          {
            lower[ d ] = std::min( lower[ d ], corn[ d ]);
            upper[ d ] = std::max( upper[ d ], corn[ d ]);
          }
        }
      }


      typedef __PolygonGrid::Node< ctype > Cell;

      Geometry () = default;

      explicit Geometry ( const Cell &cell ) : cell_( cell ), bboxImpl_()
      {
      }

      int corners () const noexcept { return numSubEntities( cell_, Dune::Codim< 2 >() ); }

      const GlobalCoordinate &corner ( int i ) const noexcept
      {
        return subEntity( cell_, Dune::Codim< 2 >(), i ).position();
      }

      GlobalCoordinate center () const noexcept
      {
        GlobalCoordinate center( 0 );
        ctype volume = 0;
        for( int i = 0; i < corners(); ++i )
        {
          const GlobalCoordinate &x = corner( i );
          const GlobalCoordinate &y = corner( (i+1) % corners() );
          const ctype weight = x[ 0 ]*y[ 1 ] - x[ 1 ]*y[ 0 ];
          center.axpy( weight, x+y );
          volume += weight;
        }
        return center *= ctype( 1 ) / (ctype( 3 )*volume);
      }

      GeometryType type () const noexcept { return GeometryTypes::none( mydimension ); }

      ctype volume () const noexcept
      {
        ctype volume = 0;
        for( int i = 0; i < corners(); ++i )
        {
          const GlobalCoordinate &x = corner( i );
          const GlobalCoordinate &y = corner( (i+1) % corners() );
          volume += x[ 0 ]*y[ 1 ] - x[ 1 ]*y[ 0 ];
        }
        return volume / ctype( 2 );
      }

      bool affine () const { return false; }

      GlobalCoordinate global ( const LocalCoordinate &local ) const
      {
        return bboxImpl().global( local );
      }

      LocalCoordinate local ( const GlobalCoordinate &global ) const
      {
        return bboxImpl().local( global );
      }

      ctype integrationElement ( const LocalCoordinate &local ) const
      {
        return volume(); // bboxImpl().integrationElement( local );
      }

      JacobianTransposed jacobianTransposed ( const LocalCoordinate &local ) const
      {
        return bboxImpl().jacobianTransposed( local );
      }

      JacobianInverseTransposed jacobianInverseTransposed ( const LocalCoordinate &local ) const
      {
        return bboxImpl().jacobianInverseTransposed( local );
      }

    private:
      const CartesianGeometryType& bboxImpl() const
      {
        if( ! bboxImpl_ )
        {
          GlobalCoordinate lower;
          GlobalCoordinate upper;
          computeBoundingBox( lower, upper );
          bboxImpl_.reset( new CartesianGeometryType( lower, upper ) );
        }
        return *bboxImpl_;
      }

      Cell cell_;
      mutable std::shared_ptr< CartesianGeometryType > bboxImpl_;
    };



    // Geometry for Codimension 1
    // --------------------------

    template< int cdim, class Grid >
    class Geometry< 1, cdim, Grid > : public GeometryDefaultImplementation<1, cdim, Grid, Geometry>
    {
      typedef Geometry< 1, cdim, Grid > This;

    public:
      typedef typename std::remove_const_t< Grid >::ctype ctype;

      static const int mydimension = 1;
      static const int coorddimension = 2;

      typedef FieldVector< ctype, mydimension > LocalCoordinate;
      typedef FieldVector< ctype, coorddimension > GlobalCoordinate;

      typedef FieldMatrix< ctype, mydimension, coorddimension > JacobianTransposed;
      typedef FieldMatrix< ctype, coorddimension, mydimension > JacobianInverseTransposed;

      typedef __PolygonGrid::HalfEdge< ctype > HalfEdge;

      Geometry () = default;

      Geometry ( const HalfEdge &halfEdge ) : halfEdge_( halfEdge ) {}

      int corners () const { return numSubEntities( halfEdge_, Dune::Codim< 1 >() ); }

      const GlobalCoordinate &corner ( int i ) const
      {
        return subEntity( halfEdge_, Dune::Codim< 1 >(), i ).position();
      }

      GlobalCoordinate center () const
      {
        GlobalCoordinate center( corner( 0 ) + corner( 1 ) );
        return center /= ctype( 2 );
      }

      GeometryType type () const noexcept { return GeometryTypes::cube( mydimension ); }

      ctype volume () const noexcept { return (corner( 1 ) - corner( 0 )).two_norm(); }

      bool affine () const { return true; }

      GlobalCoordinate global ( const LocalCoordinate &local ) const
      {
        GlobalCoordinate global( corner( 0 ) );
        global.axpy( local[ 0 ], corner( 1 ) - corner( 0 ) );
        return global;
      }

      LocalCoordinate local ( const GlobalCoordinate &global ) const
      {
        const GlobalCoordinate h = corner( 1 ) - corner( 0 );
        return LocalCoordinate{ (global - corner( 0 )) * h / h.two_norm2() };
      }

      ctype integrationElement ( const LocalCoordinate &local ) const { return jacobianTransposed( local )[ 0 ].two_norm(); }

      JacobianTransposed jacobianTransposed ( const LocalCoordinate &local ) const
      {
        return JacobianTransposed{ corner( 1 ) - corner( 0 ) };
      }

      JacobianInverseTransposed jacobianInverseTransposed ( const LocalCoordinate &local ) const
      {
        const GlobalCoordinate h = corner( 1 ) - corner( 0 );
        const ctype w = ctype( 1 ) / h.two_norm2();
        JacobianInverseTransposed jit;
        jit[ 0 ][ 0 ] = w*h[ 0 ];
        jit[ 1 ][ 0 ] = w*h[ 1 ];
        return jit;
      }

    private:
      HalfEdge halfEdge_;
    };


    // Geometry for Codimension 1
    // --------------------------

    template< int mydim, int cdim, class Grid >
    class LocalGeometry : public GeometryDefaultImplementation<mydim, cdim, Grid, LocalGeometry>
    {
      typedef LocalGeometry< mydim, cdim, Grid > This;

       static_assert( mydim == 1 ,"Only implemented for mydim == 1 ");
    public:
      typedef typename std::remove_const_t< Grid >::ctype ctype;

      static const int mydimension = 1;
      static const int coorddimension = 2;

      typedef FieldVector< ctype, mydimension > LocalCoordinate;
      typedef FieldVector< ctype, coorddimension > GlobalCoordinate;

      typedef FieldMatrix< ctype, mydimension, coorddimension > JacobianTransposed;
      typedef FieldMatrix< ctype, coorddimension, mydimension > JacobianInverseTransposed;

      LocalGeometry () = default;

      LocalGeometry ( const GlobalCoordinate& c0, const GlobalCoordinate& c1 )
      {
        corners_[ 0 ] = c0;
        corners_[ 1 ] = c1;
      }

      int corners () const { return 2; }

      const GlobalCoordinate &corner ( int i ) const
      {
        assert( i < corners() );
        return corners_[ i ];
      }

      GlobalCoordinate center () const
      {
        GlobalCoordinate center( corner( 0 ) + corner( 1 ) );
        return center /= ctype( 2 );
      }

      GeometryType type () const noexcept { return GeometryTypes::cube( mydimension ); }

      ctype volume () const noexcept { return (corner( 1 ) - corner( 0 )).two_norm(); }

      bool affine () const { return true; }

      GlobalCoordinate global ( const LocalCoordinate &local ) const
      {
        GlobalCoordinate global( corner( 0 ) );
        global.axpy( local[ 0 ], corner( 1 ) - corner( 0 ) );
        return global;
      }

      LocalCoordinate local ( const GlobalCoordinate &global ) const
      {
        const GlobalCoordinate h = corner( 1 ) - corner( 0 );
        return LocalCoordinate{ (global - corner( 0 )) * h / h.two_norm2() };
      }

      ctype integrationElement ( const LocalCoordinate &local ) const { return jacobianTransposed( local )[ 0 ].two_norm(); }

      JacobianTransposed jacobianTransposed ( const LocalCoordinate &local ) const
      {
        return JacobianTransposed{ corner( 1 ) - corner( 0 ) };
      }

      JacobianInverseTransposed jacobianInverseTransposed ( const LocalCoordinate &local ) const
      {
        const GlobalCoordinate h = corner( 1 ) - corner( 0 );
        const ctype w = ctype( 1 ) / h.two_norm2();
        JacobianInverseTransposed jit;
        jit[ 0 ][ 0 ] = w*h[ 0 ];
        jit[ 1 ][ 0 ] = w*h[ 1 ];
        return jit;
      }

    private:
      GlobalCoordinate corners_[ 2 ];
    };



    // Geometry for Codimension 2
    // --------------------------

    template< int cdim, class Grid >
    class Geometry< 0, cdim, Grid > : public GeometryDefaultImplementation<0, cdim, Grid, Geometry>
    {
      typedef Geometry< 0, cdim, Grid > This;

    public:
      typedef typename std::remove_const_t< Grid >::ctype ctype;

      static const int mydimension = 0;
      static const int coorddimension = 2;

      typedef FieldVector< ctype, mydimension > LocalCoordinate;
      typedef FieldVector< ctype, coorddimension > GlobalCoordinate;

      typedef FieldMatrix< ctype, mydimension, coorddimension > JacobianTransposed;
      typedef FieldMatrix< ctype, coorddimension, mydimension > JacobianInverseTransposed;

      typedef __PolygonGrid::Node< ctype > Node;

      Geometry () = default;

      explicit Geometry ( const Node &node ) : node_( node ) {}

      int corners () const { return 1; }

      const GlobalCoordinate &corner ( int i ) const { return center(); }
      const GlobalCoordinate &center () const { return node_.position(); }

      GeometryType type () const noexcept { return GeometryTypes::none( mydimension ); }

      ctype volume () const noexcept { return ctype( 1 ); }

      bool affine () const { return true; }

      GlobalCoordinate global ( const LocalCoordinate &local ) const { return center(); }
      LocalCoordinate local ( const GlobalCoordinate &global ) const { return {}; }

      ctype integrationElement ( const LocalCoordinate &local ) const { return ctype( 1 ); }

      JacobianTransposed jacobianTransposed ( const LocalCoordinate &local ) const { return {}; }
      JacobianInverseTransposed jacobianInverseTransposed ( const LocalCoordinate &local ) const { return {}; }

    private:
      Node node_;
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_GEOMETRY_HH
