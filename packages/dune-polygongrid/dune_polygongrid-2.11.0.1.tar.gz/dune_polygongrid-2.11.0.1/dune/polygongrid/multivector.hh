#ifndef DUNE_POLYGONGRID_MULTIVECTOR_HH
#define DUNE_POLYGONGRID_MULTIVECTOR_HH

#include <algorithm>
#include <initializer_list>
#include <iterator>
#include <vector>

#include <dune/polygongrid/iteratortags.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    namespace __MultiVector
    {

      // Reference
      // ---------

      template< class I, class CI >
      class Reference
      {
        typedef Reference< I, CI > This;

      public:
        typedef I iterator;
        typedef CI const_iterator;

        typedef std::reverse_iterator< const_iterator > const_reverse_iterator;
        typedef std::reverse_iterator< iterator > reverse_iterator;

        typedef typename std::iterator_traits< iterator >::value_type value_type;

        typedef typename std::iterator_traits< iterator >::reference reference;
        typedef typename std::iterator_traits< const_iterator >::reference const_reference;

        typedef typename std::iterator_traits< iterator >::pointer pointer;
        typedef typename std::iterator_traits< const_iterator >::pointer const_pointer;

        typedef typename std::iterator_traits< iterator >::difference_type difference_type;
        typedef std::size_t size_type;

        Reference ( iterator begin, iterator end ) : begin_( begin ), end_( end ) {}

        template< class II >
        Reference ( const Reference< II, CI > &other )
          : begin_( other.begin() ), end_( other.end() )
        {}

        Reference ( const This & ) = default;
        Reference ( This && ) = default;

        This &operator= ( const This &other ) { assign( other.begin(), other.end() ); return *this; }
        This &operator= ( const value_type &other ) { assign( other.begin(), other.end() ); return *this; }

        const_iterator begin () const noexcept { return begin_; }
        iterator begin () noexcept { return begin_; }
        const_iterator end () const noexcept { return end_; }
        iterator end () noexcept { return end_; }

        const_reverse_iterator rbegin () const noexcept { return const_reverse_iterator( end() ); }
        reverse_iterator rbegin () noexcept { return reverse_iterator( end() ); }
        const_reverse_iterator rend () const noexcept { return const_reverse_iterator( begin() ); }
        reverse_iterator rend () noexcept { return reverse_iterator( begin() ); }

        const_iterator cbegin () const noexcept { return begin(); }
        const_iterator cend () const noexcept { return end(); }
        const_reverse_iterator crbegin () const noexcept { return rbegin(); }
        const_reverse_iterator crend () const noexcept { return rend(); }

        const_reference operator[] ( size_type i ) const { return begin()[ i ]; }
        reference operator[] ( size_type i ) { return begin()[ i ]; }

        const_reference at ( size_type i ) const { return begin()[ i ]; }
        reference at ( size_type i ) { return begin()[ i ]; }

        const_reference front () const noexcept { return *begin(); }
        reference front () noexcept { return *begin(); }
        const_reference back () const noexcept { return *rbegin(); }
        reference back () noexcept { return *rbegin(); }

        bool empty () const noexcept { return (begin() == end()); }
        size_type size () const noexcept { return (end() - begin()); }
        size_type max_size () const noexcept { return size(); }

        template< class InputIterator >
        void assign ( InputIterator first, InputIterator last )
        {
          assert( std::distance( first, last ) == size() );
          std::copy( first, last, begin() );
        }

        void fill ( const value_type &value ) { std::fill( begin(), end(), value ); }

      private:
        iterator begin_, end_;
      };



      // Iterator
      // --------

      template< class I, class R >
      class Iterator
        : public VirtualIterator< std::random_access_iterator_tag, typename R::value_type, typename std::iterator_traits< I >::difference_type,  R >
      {
        typedef Iterator< I, R > This;
        typedef VirtualIterator< std::random_access_iterator_tag, typename R::value_type, typename std::iterator_traits< I >::difference_type,  R > Base;

      public:
        typedef typename Base::reference reference;
        typedef typename Base::pointer pointer;

        typedef typename Base::difference_type difference_type;

        Iterator () = default;
        Iterator ( I iterator, typename reference::iterator begin ) : iterator_( iterator ), begin_( begin ) {}

        bool operator== ( const This &other ) const { return (iterator_ == other.iterator_); }
        bool operator!= ( const This &other ) const { return (iterator_ != other.iterator_); }

        bool operator< ( const This &other ) const { return (iterator_ < other.iterator_); }
        bool operator<= ( const This &other ) const { return (iterator_ <= other.iterator_); }
        bool operator> ( const This &other ) const { return (iterator_ > other.iterator_); }
        bool operator>= ( const This &other ) const { return (iterator_ >= other.iterator_); }

        reference operator[] ( difference_type n ) const { return reference( begin_ + iterator_[ n ], begin_ + iterator_[ n+1 ] ); }
        reference operator* () const { return reference( begin_ + iterator_[ 0 ], begin_ + iterator_[ 1 ] ); }
        pointer operator-> () const { return pointer( begin_ + iterator_[ 0 ], begin_ + iterator_[ 1 ] ); }

        This &operator++ () { ++iterator_; return *this; }
        This operator++ ( int ) { This copy; ++(*this); return copy; }
        This &operator-- () { --iterator_; return *this; }
        This operator-- ( int ) { This copy; --(*this); return copy; }

        This &operator+= ( difference_type n ) { iterator_ += n; }
        This &operator-= ( difference_type n ) { iterator_ -= n; }

        friend This operator+ ( This a, difference_type n ) { return This( a.iterator_ + n, a.begin_ ); }
        friend This operator+ ( difference_type n, This a ) { return This( a.iterator_ + n, a.begin_ ); }
        friend This operator- ( This a, difference_type n ) { return This( a.iterator_ - n, a.begin_ ); }

        difference_type operator- ( const This &other ) const { return (iterator_ - other.iterator_); }

        I iterator_;
        typename reference::iterator begin_;
      };

    } // namespace __MultiVector



    // MultiVector
    // -----------

    /**
     * \brief efficient vector of small vectors
     *
     * The MultiVector< T > essentially behaves like a
     * std::vector< std::vector< T > >.
     */
    template< class T >
    class MultiVector
    {
      typedef MultiVector< T > This;

    public:
      typedef std::vector< T > value_type;
      typedef std::size_t size_type;

      typedef std::pair< size_type, size_type > index_type;

      typedef __MultiVector::Reference< typename value_type::iterator, typename value_type::const_iterator > reference;
      typedef __MultiVector::Reference< typename value_type::const_iterator, typename value_type::const_iterator > const_reference;

      typedef __MultiVector::Iterator< typename std::vector< size_type >::iterator, reference > iterator;
      typedef __MultiVector::Iterator< typename std::vector< size_type >::const_iterator, const_reference > const_iterator;

      typedef std::reverse_iterator< const_iterator > const_reverse_iterator;
      typedef std::reverse_iterator< iterator > reverse_iterator;

      explicit MultiVector ( size_type size = 0 ) : offsets_( size+1, 0u ) {}

      explicit MultiVector ( const std::vector< size_type > &counts ) { resize( counts ); }
      MultiVector ( const std::vector< size_type > &counts, const T &value ) { resize( counts, value ); }

      MultiVector ( std::initializer_list< value_type > values ) { assign( values ); }
      MultiVector ( std::initializer_list< std::initializer_list< T > > values ) { assign( values ); }

      size_type begin_of ( std::size_t i ) const noexcept { return offsets_[ i ]; }
      size_type end_of ( std::size_t i ) const noexcept { return offsets_[ i+1 ]; }

      size_type position_of ( std::size_t i, std::size_t k ) const noexcept { return (begin_of( i ) + k); }
      size_type position_of ( index_type i ) const noexcept { return position_of( i.first, i.second ); }

      const_iterator begin () const noexcept { return const_iterator( offsets_.begin(), values_.begin() ); }
      iterator begin () noexcept { return iterator( offsets_.begin(), values_.begin() ); }
      const_iterator end () const noexcept { return const_iterator( offsets_.end()-1, values_.begin() ); }
      iterator end () noexcept { return iterator( offsets_.end()-1, values_.begin() ); }

      const_reverse_iterator rbegin () const noexcept { return const_reverse_iterator( end() ); }
      reverse_iterator rbegin () noexcept { return reverse_iterator( end() ); }
      const_reverse_iterator rend () const noexcept { return const_reverse_iterator( begin() ); }
      reverse_iterator rend () noexcept { return reverse_iterator( begin() ); }

      const_iterator cbegin () const noexcept { return begin(); }
      const_iterator cend () const noexcept { return end(); }
      const_reverse_iterator crbegin () const noexcept { return rbegin(); }
      const_reverse_iterator crend () const noexcept { return rend(); }

      const_reference operator[] ( size_type i ) const noexcept { return const_reference( values_.begin() + begin_of( i ), values_.begin() + end_of( i ) ); }
      reference operator[] ( size_type i ) noexcept { return reference( values_.begin() + begin_of( i ), values_.begin() + end_of( i ) ); }
      const_reference at ( size_type i ) const { return const_reference( values_.begin() + offsets_.at( i ), values_.begin() + offsets_.at( i+1 ) ); }
      reference at ( size_type i ) { return reference( values_.begin() + offsets_.at( i ), values_.begin() + offsets_.at( i+1 ) ); }

      const T &operator[] ( index_type i ) const noexcept { return values_[ position_of( i ) ]; }
      T operator[] ( index_type i ) noexcept { return values_[ position_of( i ) ]; }
      const T &at ( index_type i ) const { return values_.at( offsets_.at( i.first ) + i.second ); }
      T &at ( index_type i ) { return values_.at( offsets_.at( i.first ) + i.second ); }

      bool empty () const noexcept { return (offsets_.size() == 1u); }
      bool empty ( size_type i ) const noexcept { return (begin_of( i ) == end_of( i )); }
      size_type size () const noexcept { return (offsets_.size()-1); }
      size_type size ( size_type i ) const noexcept { return (end_of( i ) - begin_of( i )); }

      std::vector< size_type > sizes () const
      {
        const std::size_t n = size();
        std::vector< size_type > sizes( n );
        for( std::size_t k = 0; k < n; ++k )
          sizes[ k ] = end_of( k ) - begin_of( k );
        return sizes;
      }

      void assign ( std::initializer_list< value_type > values )
      {
        compute_offsets( values.size(), [ values ] ( std::size_t i ) { return values.begin()[ i ].size(); } );
        values_.resize( offsets_.back() );
        auto it = values_.begin();
        for( const value_type &value : values )
          it = std::copy( value.begin(), value.end(), it );
      }

      void assign ( std::initializer_list< std::initializer_list< T > > values )
      {
        compute_offsets( values.size(), [ values ] ( std::size_t i ) { return values.begin()[ i ].size(); } );
        values_.resize( offsets_.back() );
        auto it = values_.begin();
        for( const value_type &value : values )
          it = std::copy( value.begin(), value.end(), it );
      }

      void clear ()
      {
        offsets_.resize( 1 );
        values_.clear();
      }

      void resize ( const std::vector< size_type > &counts )
      {
        compute_offsets( counts.size(), [ &counts ] ( size_type i ) { return counts[ i ]; } );
        values_.resize( offsets_.back() );
      }

      void resize ( const std::vector< size_type > &counts, const T &value )
      {
        compute_offsets( counts.size(), [ &counts ] ( size_type i ) { return counts[ i ]; } );
        values_.resize( offsets_.back(), value );
      }

      void push_back ( const value_type &vector )
      {
        size_type size = vector.size();
        offsets_.push_back( offsets_.back() + size );
        values_.reserve( offsets_.back() );
        for( const T &value : vector )
          values_.push_back( value );
      }

      void pop_pack ()
      {
        offsets_.pop_back();
        values_.resize( offsets_.back() );
      }

      const std::vector< T > &values () const noexcept { return values_; }
      std::vector< T > &values () noexcept { return values_; }

      void fill_each ( const T &value ) { std::fill( values_.begin(), values_.end(), value ); }

      void sort_each ()
      {
        for( size_type k = 0u; k < size(); ++k )
          std::sort( values_.begin() + begin_of( k ), values_.begin() + end_of( k ) );
      }

      void unique_each ()
      {
        auto pos = values_.begin();
        size_type offset = 0u;
        for( size_type k = 0u; k < size(); ++k )
        {
          auto end = std::unique_copy( values_.begin() + offset, values_.end() + offsets_[ k+1 ], pos );
          offsets_[ k+1 ] = std::distance( pos, end );
          pos = end;
        }
        values_.resize( offsets_.back() );
      }

    private:
      template< class Count >
      void compute_offsets ( std::size_t size, Count count )
      {
        offsets_.resize( size+1 );
        offsets_[ 0 ] = 0u;
        for( size_type k = 0u; k < size; ++k )
          offsets_[ k+1 ] = offsets_[ k ] + count( k );
      }

      std::vector< size_type > offsets_;
      std::vector< T > values_;
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_MULTIVECTOR_HH
