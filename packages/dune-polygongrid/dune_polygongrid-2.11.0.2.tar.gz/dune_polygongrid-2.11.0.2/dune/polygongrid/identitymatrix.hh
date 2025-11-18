#ifndef DUNE_POLYGONGRID_IDENTITYMATRIX_HH
#define DUNE_POLYGONGRID_IDENTITYMATRIX_HH

#include <cassert>
#include <cmath>
#include <cstddef>

#include <dune/common/densematrix.hh>
#include <dune/common/ftraits.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // Internal forward declaration
    // ----------------------------

    template< class K, int N >
    class IdentityMatrix;

  } // namespace __PolygonGrid



#ifndef DOXYGEN

  // FieldTraits
  // -----------

  template< class K, int N >
  struct FieldTraits< __PolygonGrid::IdentityMatrix< K, N > >
  {
    typedef typename FieldTraits< K >::field_type field_type;
    typedef typename FieldTraits< K >::real_type real_type;
  };

#endif // #ifndef DOXYGEN



  namespace __PolygonGrid
  {

    // IdentityMatrix
    // --------------

    /**
     * \class IdentityMatrix
     *
     * \brief Read-only identity matrix
     *
     * Implementation of an identity matrix that does not store any data.
     *
     * \tparam  K  field type
     * \tparam  N  dimension
     **/
    template< class K, int N >
    class IdentityMatrix
    {
      typedef IdentityMatrix< K, N > This;

    public:
      typedef typename FieldTraits< This >::field_type field_type;
      typedef K value_type;

      typedef std::size_t size_type;

      static const int rows = N;
      static const int cols = N;

      template< class X, class Y >
      void mv ( const X &x, Y &y ) const
      {
        y = x;
      }

      template< class X, class Y >
      void mtv ( const X &x, Y &y ) const
      {
        y = x;
      }

      template< class X, class Y >
      void umv ( const X &x, Y &y ) const
      {
        y += x;
      }

      template< class X, class Y >
      void umtv ( const X &x, Y &y ) const
      {
        y += x;
      }

      template< class X, class Y >
      void umhv ( const X &x, Y &y ) const
      {
        y += x;
      }

      template< class X, class Y >
      void mmv ( const X &x, Y &y ) const
      {
        y -= x;
      }

      template< class X, class Y >
      void mmtv ( const X &x, Y &y ) const
      {
        y -= x;
      }

      template< class X, class Y >
      void mmhv ( const X &x, Y &y ) const
      {
        y -= x;
      }

      template< class X, class Y >
      void usmv ( const typename FieldTraits< Y >::field_type &alpha, const X &x, Y &y ) const
      {
        y.axpy( alpha, x );
      }

      template< class X, class Y >
      void usmtv ( const typename FieldTraits< Y >::field_type &alpha, const X &x, Y &y ) const
      {
        y.axpy( alpha, x );
      }

      template< class X, class Y >
      void usmhv ( const typename FieldTraits< Y >::field_type &alpha, const X &x, Y &y ) const
      {
        y.axpy( alpha, x );
      }

      typename FieldTraits< field_type >::real_type frobenius_norm () const
      {
        using std::sqrt;
        return sqrt( frobenius_norm2() );
      }

      typename FieldTraits< field_type >::real_type frobenius_norm2 () const
      {
        return FieldTraits< field_type >::real_type( N );
      }

      typename FieldTraits< field_type >::real_type infinity_norm () const
      {
        return FieldTraits< field_type >::real_type( 1 );
      }

      typename FieldTraits< field_type >::real_type infinity_norm_real () const
      {
        return FieldTraits< field_type >::real_type( 1 );
      }
    };

  } // namespace __PolygonGrid



  // Template specialization of DenseMatrixAssigner
  // ----------------------------------------------

  template< class DenseMatrix, class K, int N >
  class DenseMatrixAssigner< DenseMatrix, __PolygonGrid::IdentityMatrix< K, N > >
  {
  public:
    static void apply ( DenseMatrix &denseMatrix, const __PolygonGrid::IdentityMatrix< K, N > & )
    {
      assert( denseMatrix.N() == N );
      assert( denseMatrix.M() == N );
      for( int i = 0; i < N; ++i )
        for( int j = 0; j < N; ++j )
          denseMatrix[ i ][ j ] = (i == j) ? 1 : 0;
    }
  };

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_IDENTITYMATRIX_HH
