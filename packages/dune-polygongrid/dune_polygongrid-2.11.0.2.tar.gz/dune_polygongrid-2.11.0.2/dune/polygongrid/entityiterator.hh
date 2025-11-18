#ifndef DUNE_POLYGONGRID_ENTITYITERATOR_HH
#define DUNE_POLYGONGRID_ENTITYITERATOR_HH

#include <cassert>
#include <cstddef>

#include <type_traits>

#include <dune/geometry/dimension.hh>

#include <dune/polygongrid/entity.hh>
#include <dune/polygongrid/iteratortags.hh>
#include <dune/polygongrid/meshobjects.hh>

namespace Dune
{

  namespace __PolygonGrid
  {

    // EntityIterator for Node
    // -----------------------

    template< int codim, class Grid >
    class EntityIterator
    {
      typedef EntityIterator< codim, Grid > This;

      typedef IndexIterator< Node< typename std::remove_const< Grid >::type::ctype > > Iterator;
      typedef __PolygonGrid::Entity< codim, 2, Grid > EntityImpl;

    public:
      static const int codimension = codim;
      static const int dimension = 2;
      static const int mydimension = dimension - codimension;

      typedef __PolygonGrid::Mesh< typename std::remove_const< Grid >::type::ctype > Mesh;

      typedef Dune::Entity< codim, 2, Grid, __PolygonGrid::Entity > Entity;

      EntityIterator () = default;

      EntityIterator ( Tag::Begin, const Mesh &mesh, MeshType type ) : iterator_( mesh, mesh.begin( type, Codim< codim >() ) ) {}
      EntityIterator ( Tag::End, const Mesh &mesh, MeshType type ) : iterator_( mesh, mesh.end( type, Codim< codim >() ) ) {}

      Entity dereference () const { return EntityImpl( *iterator_ ); }

      bool equals ( const This &other ) const noexcept { return (iterator_ == other.iterator_); }

      void increment () noexcept { ++iterator_; }

    protected:
      Iterator iterator_;
    };



    // EntityIterator for HalfEdge
    // ---------------------------

    template< class Grid >
    class EntityIterator< 1, Grid >
    {
      typedef EntityIterator< 1, Grid > This;

      typedef IndexIterator< HalfEdge< typename std::remove_const< Grid >::type::ctype > > Iterator;
      typedef __PolygonGrid::Entity< 1, 2, Grid > EntityImpl;

    public:
      static const int codimension = 1;
      static const int dimension = 2;
      static const int mydimension = dimension - codimension;

      typedef __PolygonGrid::Mesh< typename std::remove_const< Grid >::type::ctype > Mesh;

      typedef Dune::Entity< 1, 2, Grid, __PolygonGrid::Entity > Entity;

      EntityIterator () = default;

      EntityIterator ( Tag::Begin, const Mesh &mesh, MeshType type ) : iterator_( begin( mesh, type ) ) { advance(); }
      EntityIterator ( Tag::End, const Mesh &mesh, MeshType type ) : iterator_( end( mesh, type ) ) {}

      Entity dereference () const { return EntityImpl( *iterator_ ); }

      bool equals ( const This &other ) const noexcept { return (iterator_ == other.iterator_); }

      void increment () noexcept { ++iterator_; advance(); }

    protected:
      static Iterator begin ( const Mesh &mesh, MeshType type ) { return Iterator( mesh, mesh.begin( type, Codim< 1 >() ) ); }
      static Iterator end ( const Mesh &mesh, MeshType type ) { return Iterator( mesh, mesh.end( type, Codim< 1 >() ) ); }

      Iterator begin () const { return begin( iterator_->mesh(), iterator_->type() ); }
      Iterator end () const { return end( iterator_->mesh(), iterator_->type() ); }

      void advance ()
      {
        for( ; (iterator_ != end()) && (iterator_->cell().index() > iterator_->neighbor().index()); ++iterator_ )
          continue;
      }

      Iterator iterator_;
    };

  } // namespace __PolygonGrid

} // namespace Dune

#endif // #ifndef DUNE_POLYGONGRID_ENTITYITERATOR_HH
