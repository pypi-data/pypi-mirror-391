#ifndef DUNE_POLYGONGRID_ITERATORTAGS_HH
#define DUNE_POLYGONGRID_ITERATORTAGS_HH

#include <cstddef>
#include <utility>

namespace Dune
{

  namespace __PolygonGrid
  {

    namespace Tag
    {

      // Begin
      // -----

      struct Begin {};



      // End
      // ---

      struct End {};



      namespace
      {

        // begin
        // -----

        const Begin begin = {};



        // end
        // ---

        const End end = {};

      } // anonymous namespace

    } // namespace Tag



    // Envelope
    // --------

    template< class T >
    struct Envelope
    {
      typedef T element_type;
      typedef const T *const_pointer;
      typedef T *pointer;

      template< class... Args >
      explicit Envelope ( Args &&... args )
        : element_( std::forward< Args >( args )... )
      {}

      Envelope ( const Envelope & ) = default;
      Envelope ( Envelope && ) = default;

      Envelope &operator= ( const Envelope & ) = default;
      Envelope &operator= ( Envelope && ) = default;

      explicit operator bool () const noexcept { return true; }

      const typename std::add_lvalue_reference< element_type >::type operator* () const { return element_; }
      typename std::add_lvalue_reference< element_type >::type operator* () { return element_;  }

      const_pointer operator-> () const { return &element_; }
      pointer operator-> () { return &element_; }

    protected:
      element_type element_;
    };

    namespace detail {
      template <class Category, class T, class Distance = ptrdiff_t,
                class Pointer = T*, class Reference = T&>
      struct std_iterator {
        typedef T         value_type;
        typedef Distance  difference_type;
        typedef Pointer   pointer;
        typedef Reference reference;
        typedef Category  iterator_category;
      };
    }


    // VirtualIterator
    // ---------------

    template< class C, class T, class D = std::ptrdiff_t, class R = T >
    using VirtualIterator = detail::std_iterator< C, T, D, Envelope< R >, R >;

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_ITERATORTAGS_HH
